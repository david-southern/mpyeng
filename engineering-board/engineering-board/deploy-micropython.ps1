# mpremote will usually detect the COM port the MicroPython device is on, but if you have multiple
# devices connected, you can enumerate them with this command:
# Get-PnpDevice -Class Ports | Where-Object Status -EQ 'OK' | Where-Object DeviceId -Match 'PID'

# I have aliased mpremote to "mp"


# mp cp cannot take wildcards, so we have to enumerate the files and directories we want to copy,
# and then pass them as an array to mp cp. mp cp can do a recursive copy, so we only need to worry
# about enumerating the top-level files and directories we want to copy, and not their children.

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$DebugOutput,
    [switch]$Prune,
    [string]$FilterPattern = ''
)

$script:MpDryRun = $false

if ($DryRun) {
    $script:MpDryRun = $true
    Write-Host "[DRY RUN] No changes will be made to the device." -ForegroundColor Magenta
}
if ($Force) {
    Write-Host "[FORCE] All files will be copied regardless of size." -ForegroundColor Magenta
}
if ($FilterPattern -ne '') {
    Write-Host "[FILTER] Only copying files matching: $FilterPattern" -ForegroundColor Magenta
}
if ($DebugOutput) {
    Write-Host "[DEBUG OUTPUT] Verbose skip messages enabled." -ForegroundColor Magenta
}

. .\deployment-utils\common-utils.ps1

# Overall process:
# 1. Enumerate all files and directories in the current directory, excluding certain ones that we
#    don't want to copy
# 2. Enumerate recursively all files on the device
# 3. Remove any files on the device that are not in the list of files we want to copy
# 4. Copy files to the device, skipping any whose size has not changed (use -Force to override)
# 5. Prune any empty directories left on the device
# 6. Send a soft-reset to the device

$ignoreDirectories = @(
    '__pycache__',
    '\.venv',
    '\.vscode',
    '\.git',
    '\.ruff_cache',
    'host_comms',
    'deployment-utils',
    'typings'
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

$ignoreRE = ($ignoreDirectories + $ignoreFiles) -join '|'

# All local files (recursive, files only) normalized to forward-slash relative paths,
# used to determine what should exist on the device.
$deployFiles = @(
    Get-ChildItem -Recurse -File |
        Where-Object { $_.FullName -notmatch $ignoreRE } |
        ForEach-Object { (Resolve-Path -Relative $_.FullName) -replace '^\.[\\/]', '' -replace '\\', '/' }
)

# Step 2: Enumerate all files currently on the device
Write-Host "Enumerating device files..." -ForegroundColor Cyan
$deviceFiles = Get-DeviceFiles ':/'

# Step 3: Remove any device files that are not in the local file list
$filesToRemove = @(
    $deviceFiles.Keys | Where-Object {
        $normalized = $_ -replace '^:/', ''
        $deployFiles -notcontains $normalized
    }
)

if ($filesToRemove.Count -gt 0) {
    Write-Host "Removing $($filesToRemove.Count) orphaned file(s) from device..." -ForegroundColor Yellow
    Invoke-Mpremote rm @filesToRemove
} else {
    Write-Host "No orphaned files to remove." -ForegroundColor Green
}

$manifestPath = "deployment-utils\last-deployment-manifest.json"
$manifest = if (Test-Path $manifestPath) {
    Get-Content $manifestPath -Raw | ConvertFrom-Json -AsHashtable
} else {
    @{}
}

$filteredSkipCount = 0
$timestampSkipCount = 0

# Step 4: Copy all local items to the device
Write-Host "Copying $($deployFiles.Count) item(s) to device..." -ForegroundColor Cyan

# For some reason, this command does not work when called from this script, even though it works
# when I call it from PowerShell. No idea why, but the loop below does work...
# Invoke-Mpremote cp -rv $topLevelItems :/

# Derive the set of directories that already exist on the device from the file paths.
$deviceDirectories = @(
    $deviceFiles.Keys | ForEach-Object { $_ -replace '^:/', '' } |
        Where-Object { $_.Contains('/') } |
        ForEach-Object { $_.Substring(0, $_.LastIndexOf('/')) } |
        Select-Object -Unique
)

if($DebugOutput) {
    Write-Host "Initial Device directories:" -ForegroundColor Gray
    foreach ($dir in $deviceDirectories) {
        Write-Host "  $dir" -ForegroundColor DarkGray
    }
    Write-Host "Initial Device files:" -ForegroundColor Gray
    foreach ($file in $deviceFiles.Keys) {
        Write-Host "  $file" -ForegroundColor DarkGray
    }
}

foreach ($item in $deployFiles) {
    # $item for a directory: utils\other\thingy.py
    # required $remotePath for the directory: :/utils/other
    $remotePath = $item -replace '\\', '/'

    if ($remotePath.Contains('/')) {
        $remoteDirectoryNormalized = $remotePath.Substring(0, $remotePath.LastIndexOf('/'))
        $remoteDirectory = ':/' + $remoteDirectoryNormalized
        if ($deviceDirectories -notcontains $remoteDirectoryNormalized) {
            Write-Host "  Creating directory: $remoteDirectory" -ForegroundColor Cyan
            Invoke-Mpremote mkdir $remoteDirectory -IgnoreErrors
            $deviceDirectories += $remoteDirectoryNormalized
        } elseif ($DebugOutput) {
            Write-Host "Create directory: Skipping existing: $remoteDirectory" -ForegroundColor DarkGray
        }
    }

    $remotePath = ":/" + $remotePath

    if($DebugOutput) {
        Write-Host "Ensure file: $remotePath" -ForegroundColor DarkGray
    }

    if (-not [string]::IsNullOrEmpty($FilterPattern) -and $item -notmatch $FilterPattern) {
        if ($DebugOutput) {
            Write-Host "  Skipping (filtered): $item" -ForegroundColor DarkGray
        } else {
            $filteredSkipCount++
        }
        continue
    }

    $localModified = ((Get-Item $item).LastWriteTime).ToString('o')
    $manifestEntry = $manifest[$item]
    if (-not $Force -and $null -ne $manifestEntry -and $manifestEntry -eq $localModified) {
        if ($DebugOutput) {
            Write-Host "  Skipping (unchanged timestamp): $item" -ForegroundColor DarkGray
        } else {
            $timestampSkipCount++
        }
        continue
    }

    Write-Host "  Copying file: $item" -ForegroundColor Cyan
    Invoke-Mpremote cp -v $item $remotePath
    if (-not $DryRun) {
        $manifest[$item] = $localModified
    }
}

if (-not $DebugOutput) {
    if ($filteredSkipCount -gt 0) {
        Write-Host "  Skipped $filteredSkipCount file(s) due to filter pattern." -ForegroundColor DarkGray
    }
    if ($timestampSkipCount -gt 0) {
        Write-Host "  Skipped $timestampSkipCount file(s) with unchanged timestamp." -ForegroundColor DarkGray
    }
}

if (-not $DryRun) {
    $manifest | ConvertTo-Json | Set-Content $manifestPath
}

# Copy our secrets file if it exists. This file is not checked in to source control.
$secretsSource = "$env:USERPROFILE\source\repos\secrets\secrets-eng-board.py"

if (Test-Path $secretsSource) {
    Invoke-Mpremote cp $secretsSource :secrets.py
    Write-Host "Copied secrets-eng-board.py -> :/secrets.py" -ForegroundColor Green
} else {
    Write-Host "Warning: $secretsSource not found — board will not connect to WiFi" -ForegroundColor Yellow
}

# Step 5: Prune any empty directories left on the device after file removal
if ($Prune) {
    Invoke-PruneScript
}

Write-Host "Deployment complete." -ForegroundColor Green

# Doesn't work:
# # Step 6: Soft-reset the device so it picks up the new files
# Write-Host "Resetting device..." -ForegroundColor Cyan

# mpremote exec "import machine; machine.reset()"
# mpremote

# # Invoke the mpremote REPL, and send a Ctrl-D on STDIN to trigger a soft reset.
# $ctrl_D = [char]0x04

# $psi = New-Object System.Diagnostics.ProcessStartInfo
# $psi.FileName = "mpremote.exe"
# $psi.UseShellExecute = $false #start the process from it's own executable file
# $psi.RedirectStandardInput = $true #enable the process to read from standard input
# $psi.RedirectStandardOutput = $true #enable the process to write to standard output so we can read it

# $mpremote = [System.Diagnostics.Process]::Start($psi)

# Start-Sleep -s 2 #wait 2 seconds so that the process can be up and running

# $mpremote.StandardInput.WriteLine("help()"); #StandardInput property of the Process is a .NET StreamWriter object

# while ($true) {
#     $output = $mpremote.StandardOutput.ReadLine() #StandardOutput property of the Process is a .NET StreamReader object
#     Write-Host $output
# }
