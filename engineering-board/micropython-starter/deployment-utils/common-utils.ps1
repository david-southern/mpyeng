# Wrapper that runs an mpremote command, checks the exit code, and aborts on failure.
# In -DryRun mode, prints what would be run without executing it.
function Invoke-Mpremote {
    param(
        [switch]$IgnoreErrors = $false,
        [Parameter(Mandatory, ValueFromRemainingArguments)]
        [string[]]$Arguments
    )

    if ($script:MpDryRun) {
        Write-Host "  [DRY RUN] mpremote $($Arguments -join ' ')" -ForegroundColor Magenta
        return
    }

    if ($IgnoreErrors) {
        mpremote @Arguments 2> $null
    } else {
        mpremote @Arguments

        if ($LASTEXITCODE -ne 0) {
            Write-Host "mpremote $($Arguments -join ' ') failed with exit code $LASTEXITCODE. Aborting." -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }
}

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
# Enumerate all files on the device recursively.
# Returns a hashtable of { remote-path = file-size }, e.g. @{ ':/main.py' = 4994; ':/card_reader/constants.py' = 1234 }
function Get-DeviceFiles {
    param (
        [string]$remotePath = ':/'
    )

    $files = @{}
    $output = @(mpremote ls $remotePath 2>&1)

    foreach ($line in $output) {
        # Match lines like "     1234 filename.py" or "        0 dirname/"
        if ($line -match '^\s*(\d+)\s+(.+)$') {
            $size = [long]$matches[1]
            $entry = $matches[2].Trim()
            $isDir = $entry.EndsWith('/')
            $name = $entry.TrimEnd('/')

            # Build the full remote path, keeping the ':/' root intact
            $base = $remotePath.TrimEnd('/')
            $fullPath = "$base/$name"

            if ($isDir) {
                $subFiles = Get-DeviceFiles $fullPath
                foreach ($kvp in $subFiles.GetEnumerator()) {
                    $files[$kvp.Key] = $kvp.Value
                }
            } else {
                $files[$fullPath] = $size
            }
        }
    }

    return $files
}

# Enumerate all files on the device recursively, computing the MD5 hash and size of each.
# Returns a hashtable of { remote-path = @{ Hash = md5-hex-string; Size = bytes } },
# e.g. @{ ':/main.py' = @{ Hash = 'a1b2c3...'; Size = 4994 } }
function Get-DeviceFileStats {
    $statsScript = @'
import os
import hashlib
import binascii

def _stat_files(path):
    for entry in os.listdir(path):
        full = path.rstrip('/') + '/' + entry
        try:
            os.listdir(full)
            _stat_files(full)
        except OSError:
            size = os.stat(full)[6]
            h = hashlib.md5()
            with open(full, 'rb') as f:
                while True:
                    chunk = f.read(512)
                    if not chunk:
                        break
                    h.update(chunk)
            digest = binascii.hexlify(h.digest()).decode()
            print(digest + ' ' + str(size) + ' ' + full)

_stat_files('/')
'@

    $output = @(mpremote exec $statsScript 2>&1)

    $files = @{}
    foreach ($line in $output) {
        if ($line -match '^([0-9a-f]{32}) (\d+) (.+)$') {
            $path = ':' + $matches[3]
            $files[$path] = @{
                Hash = $matches[1]
                Size = [long]$matches[2]
            }
        }
    }

    return $files
}

function Invoke-PruneScript {
    $pruneScript = @'
import os
def _prune(path):
    for entry in os.listdir(path):
        full = path.rstrip('/') + '/' + entry
        try:
            _prune(full) # this call will throw for files
            if not os.listdir(full):
                os.rmdir(full)
                print('Removed empty directory:', full)
        except OSError:
            pass
_prune('/')
'@

    Write-Host "Pruning empty directories on device..." -ForegroundColor Cyan

    Invoke-Mpremote exec $pruneScript
}