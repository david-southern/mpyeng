function install-circuit-python-to-board {
    # Auto-detect the board by finding the first removable USB drive
    $cpyDrive = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType = 2" |
        Select-Object -First 1 -ExpandProperty DeviceID

    if (-not $cpyDrive) {
        Write-Host "MicroPython board not found. Make sure the board is connected and mounted as a drive." -ForegroundColor Red
        return
    }

    $ignoreDirectories = @(
        '__pycache__',
        '.vscode',
        '.git',
        'host_comms'
    )

    $ignoreFiles = @(
        'boot_out.txt',
        'secrets-eng-board.py',
        '*.jpg',
        '*.png',
        '*.ps1',
        '*.sln',
        '*.pyproj',
        '*.ttf',
        'pylintrc'
    )

    $secretsSource = "$env:USERPROFILE\source\repos\secrets\secrets-eng-board.py"
    if (Test-Path $secretsSource) {
        Copy-Item $secretsSource "$cpyDrive\secrets.py"
        Write-Host "Copied secrets-eng-board.py -> $cpyDrive\secrets.py" -ForegroundColor Green
    } else {
        Write-Host "Warning: $secretsSource not found — board will not connect to WiFi" -ForegroundColor Yellow
    }

    Write-Host "Copying to MicroPython board at $cpyDrive" -ForegroundColor Green
    robocopy . $cpyDrive /MIR /XD @ignoreDirectories /XF @ignoreFiles

}

install-circuit-python-to-board