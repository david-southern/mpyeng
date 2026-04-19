# mpremote will usually detect the COM port the MicroPython devcice is on, but if you have multiple
# devices connecte, you can enumerate them with this command:
# Get-PnpDevice -Class Ports | Where-Object Status -EQ 'OK' | Where-Object DeviceId -Match 'PID'

$ignoreDirectories = @(
    '__pycache__',
    '\.vscode',
    '\.git',
    'host_comms'
)

$ignoreFiles = @(
    '\.txt',
    'secrets-eng-board.py',
    '\.jpg',
    '\.png',
    '\.ps1',
    '\.sln',
    '\.pyproj',
    '\.ttf',
    'pylintrc'
)

$ignoreRE = ($ignoreDirectories + $ignoreFiles) -join '|'

$copyFiles = @(Get-ChildItem -Recurse | Where-Object { $_.FullName -notmatch $ignoreRE } | ForEach-Object { Resolve-Path -Relative $_.FullName })

$existingFiles = mpremote ls : | ForEach-Object { $_.Name }

mpremote cp -rv @(Get-ChildItem -Recurse | Where-Object { $_.FullName -notmatch $ignoreRE } | ForEach-Object { Resolve-Path -Relative $_.FullName }) :

$secretsSource = "$env:USERPROFILE\source\repos\secrets\secrets-eng-board.py"

if (Test-Path $secretsSource) {
    mpremote cp $secretsSource :secrets.py
    Write-Host "Copied secrets-eng-board.py -> $cpyDrive\secrets.py" -ForegroundColor Green
} else {
    Write-Host "Warning: $secretsSource not found — board will not connect to WiFi" -ForegroundColor Yellow
}
