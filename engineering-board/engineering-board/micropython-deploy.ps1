# mpremote will usually detect the COM port the MicroPython device is on, but if you have multiple
# devices connected, you can enumerate them with this command:
# Get-PnpDevice -Class Ports | Where-Object Status -EQ 'OK' | Where-Object DeviceId -Match 'PID'

# I have aliased mpremote to "mp"

# mp ls returns a listing of the requested folder that is formatted like this:
# > mp ls :/
# ls :/
#            0 bob/
#         7025 card_manager.py
#         3004 color_utils.py
#         9857 convert_animations.py
#         8582 dave_tm1637.py
#         6675 demo_data_manager.py
#         4166 device_manager.py
#         3725 eng_utils.py
#            0 lib/
#         4994 main.py
#         5001 pixel_strip_manager.py
#
# > mp ls :/bob
# ls :/bob
#         4146 AGENTS.md
#
# mp cannot perform a recursive listing, so we will have to create one ourselves

# mp cp cannot take wildcards, so we have to enumerate the files and directories we want to copy,
# and then pass them as an array to mp cp. mp cp can do a recursive copy, so we only need to worry
# about enumerating the top-level files and directories we want to copy, and not their children.

param(
    [switch]$DryRun
)

if ($DryRun) {
    Write-Host "[DRY RUN] No changes will be made to the device." -ForegroundColor Magenta
}

# Overall process:
# 1. Enumerate all files and directories in the current directory, excluding certain ones that we
#    don't want to copy
# 2. Enumerate recursively all files on the device
# 3. Remove any files on the device that are not in the list of files we want to copy
# 4. Copy all files we want to copy to the device
# 5. Prune any empty directories left on the device
# 6. Send a soft-reset to the device

$ignoreDirectories = @(
    '__pycache__',
    '\.vscode',
    '\.git',
    'host_comms'
)

$ignoreFiles = @(
    '\.txt',
    'secrets-eng-board\.py',
    '\.jpg',
    '\.png',
    '\.ps1',
    '\.sln',
    '\.pyproj',
    '\.ttf',
    '\.md',
    '\.toml',
    'pylintrc'
)

# Wrapper that runs an mpremote command, checks the exit code, and aborts on failure.
# In -DryRun mode, prints what would be run without executing it.
function Invoke-Mpremote {
    param(
        [Parameter(Mandatory, ValueFromRemainingArguments)]
        [string[]]$Arguments
    )

    if ($DryRun) {
        Write-Host "  [DRY RUN] mpremote $($Arguments -join ' ')" -ForegroundColor Magenta
        return
    }

    mpremote @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Error "mpremote $($Arguments -join ' ') failed with exit code $LASTEXITCODE. Aborting."
        exit $LASTEXITCODE
    }
}

# Enumerate all files on the device recursively.
# Returns paths in mpremote format, e.g. ':/main.py', ':/card_reader/constants.py'
function Get-DeviceFiles {
    param (
        [string]$remotePath = ':/'
    )

    $files = @()
    $output = @(mpremote ls $remotePath 2>&1)

    foreach ($line in $output) {
        # Match lines like "     1234 filename.py" or "        0 dirname/"
        if ($line -match '^\s*\d+\s+(.+)$') {
            $entry = $matches[1].Trim()
            $isDir = $entry.EndsWith('/')
            $name = $entry.TrimEnd('/')

            # Build the full remote path, keeping the ':/' root intact
            $base = $remotePath.TrimEnd('/')
            $fullPath = "$base/$name"

            if ($isDir) {
                $files += Get-DeviceFiles $fullPath
            } else {
                $files += $fullPath
            }
        }
    }

    return $files
}

$ignoreRE = ($ignoreDirectories + $ignoreFiles) -join '|'

# All local files (recursive, files only) normalized to forward-slash relative paths,
# used to determine what should exist on the device.
$localFiles = @(
    Get-ChildItem -Recurse -File |
        Where-Object { $_.FullName -notmatch $ignoreRE } |
        ForEach-Object { (Resolve-Path -Relative $_.FullName) -replace '^\.[\\/]', '' -replace '\\', '/' }
)

# Top-level items (files and directories) to copy to the device.
# mpremote cp -r handles recursive directory copies, so only top-level items are needed.
$topLevelItems = @(
    Get-ChildItem |
        Where-Object { $_.Name -notmatch $ignoreRE } |
        ForEach-Object { Resolve-Path -Relative $_.FullName }
)

# Step 2: Enumerate all files currently on the device
Write-Host "Enumerating device files..." -ForegroundColor Cyan
$deviceFiles = Get-DeviceFiles ':/'

# Step 3: Remove any device files that are not in the local file list
$filesToRemove = @(
    $deviceFiles | Where-Object {
        $normalized = $_ -replace '^:/', ''
        $localFiles -notcontains $normalized
    }
)

if ($filesToRemove.Count -gt 0) {
    Write-Host "Removing $($filesToRemove.Count) orphaned file(s) from device..." -ForegroundColor Yellow
    Invoke-Mpremote rm @filesToRemove
    # foreach ($file in $filesToRemove) {
    #     Write-Host "  Removing: $file" -ForegroundColor Yellow
    #     Invoke-Mpremote rm $file
    # }
} else {
    Write-Host "No orphaned files to remove." -ForegroundColor Green
}

# Step 4: Copy all local items to the device
Write-Host "Copying $($topLevelItems.Count) item(s) to device..." -ForegroundColor Cyan
Invoke-Mpremote cp -rv $topLevelItems :/

# foreach ($item in $topLevelItems) {
#     $isDir = (Get-Item $item).PSIsContainer
#     if ($isDir) {
#         Write-Host "  Copying directory: $item" -ForegroundColor Cyan
#         # No trailing slash on src: copies the directory itself (not just its contents) into :/
#         Invoke-Mpremote cp -r $item :/
#     } else {
#         Write-Host "  Copying file: $item" -ForegroundColor Cyan
#         Invoke-Mpremote cp $item :/
#     }
# }

# Copy our secrets file if it exists. This file is not checked in to source control.
$secretsSource = "$env:USERPROFILE\source\repos\secrets\secrets-eng-board.py"

if (Test-Path $secretsSource) {
    Invoke-Mpremote cp $secretsSource :secrets.py
    Write-Host "Copied secrets-eng-board.py -> :/secrets.py" -ForegroundColor Green
} else {
    Write-Host "Warning: $secretsSource not found — board will not connect to WiFi" -ForegroundColor Yellow
}

# Step 5: Prune any empty directories left on the device after file removal
Write-Host "Pruning empty directories on device..." -ForegroundColor Cyan
$pruneScript = @'
import os
def _prune(path):
    for entry in os.listdir(path):
        full = path.rstrip('/') + '/' + entry
        try:
            os.listdir(full)
            _prune(full)
            if not os.listdir(full):
                os.rmdir(full)
                print('Removed empty directory:', full)
        except OSError:
            pass
_prune('/')
'@
Invoke-Mpremote exec $pruneScript

# Step 6: Soft-reset the device so it picks up the new files
# Write-Host "Resetting device..." -ForegroundColor Cyan
# Invoke-Mpremote soft-reset

Write-Host "Deployment complete." -ForegroundColor Green
