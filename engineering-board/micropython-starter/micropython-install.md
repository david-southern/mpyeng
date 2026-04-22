# Deploying MicroPython to the Adafruit Feather TFT ESP32-S3

These instructions replace CircuitPython with MicroPython.

Board reference: FEATHER ESP32-S3

- <https://www.adafruit.com/product/5483>
- <https://learn.adafruit.com/adafruit-esp32-s3-tft-feather>

Board reference: Raspberry Pi Pico 2 W:

- <https://www.raspberrypi.com/products/raspberry-pi-pico-2>
- <https://www.adafruit.com/product/6243>
- Pinout: <https://pip-assets.raspberrypi.com/categories/1088-raspberry-pi-pico-2-w/documents/RP-008305-DS-1-pico-2-w-pinout.pdf>

---

## Step 1 — Download MicroPython firmware

Go to: <https://micropython.org/download/ESP32_GENERIC_S3/>

Download the latest **`.bin`** release (v1.28.0, 2026-04-06 as of writing).

> **Important:** Do NOT download the `SPIRAM_OCT` variant — that is for Octal SPIRAM
> boards. This Feather TFT has standard (quad) PSRAM.

---

## Step 2 — Install esptool and recover the board

### Install esptool

```powershell
pip install esptool
```

> Note: These instructions are for esptool v5.2.0. You can check your version with `esptool
version`. If necessary, upgrade with `pip install --upgrade esptool`.

### Force the ESP32-S3 into ROM bootloader mode

If the board is unresponsive (no COM port, no UF2 drive), use the hardware method:

1. Hold the **BOOT** button down (the one labelled `BOOT` or `DFU` on the Feather)
2. While holding BOOT, press and release **RESET**
3. Release **BOOT**

The board will now enumerate as a COM port in Device Manager (shown as **USB Serial
Device** or **USB JTAG/serial debug unit**). This is the ESP32-S3 ROM bootloader and
does not require any UF2 bootloader or existing firmware to work — it is burned into
the chip at the factory and cannot be overwritten.

> If the board still does not appear in Device Manager, try a different USB cable
> (some cables are charge-only). The board must be connected directly to the PC,
> not through a hub.

### Identify the COM port

```powershell
Get-PnpDevice -Class Ports | Where-Object Status -eq 'OK' | Select-Object FriendlyName
```

> Note: The esptool should auto-detect the COM port and set a default baud rate. You should only use
> the command above if something isn't working, or if you have multiple ESP32 devices connected at
> the same time.

> Also Note: You do not need to be admin to use esptool. If you get a permissions error, it's likely
> because the COM port is not showing up at all — check Device Manager and try a different USB
> cable.

### Erase all flash

This wipes the chip's firmware completely. Use this to do a factory reset, particularly if your
device appears to be bricked. For a working device, you can skip this step and flash MicroPython
directly — the esptool will overwrite the existing firmware without needing to erase first.

```powershell
esptool erase-flash
```

If you need to specify a port explicitly: (you can also set the baud rate if you are having comms issues)

```powershell
esptool --port COM5 --baud 9600 erase-flash
```

A successful erase ends with:

```
Flash memory erased successfully in 15.5 seconds.

Hard resetting via RTS pin...
```

The board will stay in bootloader mode after erasing.

> Note: By default, the esptool selects 115200 as the baud rate. If you want to try flashing
> firmware faster, you can typically go up to 460800 or even 921600, but if you encounter errors
> during flashing, reduce the baud rate back to 115200 or 9600. AI suggests: Use 921600 for a solid
> balance of speed and reliability

---

## Step 3 — Flash MicroPython

FYI: You can get useful information about your device by running:

```
> esptool flash-id
esptool v5.2.0
Connected to ESP32-S3 on COM10:
Chip type:          ESP32-S3 (QFN56) (revision v0.1)
Features:           Wi-Fi, BT 5 (LE), Dual Core + LP Core, 240MHz, Embedded Flash 4MB (XMC), Embedded PSRAM 2MB (AP_3v3)
Crystal frequency:  40MHz
USB mode:           USB-Serial/JTAG
MAC:                f4:12:fa:59:b3:e0

Stub flasher running.

Flash Memory Information:
=========================
Manufacturer: 20
Device: 4016
Detected flash size: 4MB
Flash type set in eFuse: quad (4 data lines)
Flash voltage set by eFuse: 3.3V

Hard resetting via RTS pin...
```

To install new firmware:

```powershell
esptool --baud 460800 write-flash 0 C:\Users\David\Downloads\ESP32_GENERIC_S3-20260406-v1.28.0.bin
```

At this baud rate, it took around 33 seconds to write the firmware. The output of the command looks
like this:

```
> esptool --baud 460800 write-flash 0 C:\Users\David\Downloads\ESP32_GENERIC_S3-20260406-v1.28.0.bin
esptool v5.2.0
Connected to ESP32-S3 on COM10:
Chip type:          ESP32-S3 (QFN56) (revision v0.1)
Features:           Wi-Fi, BT 5 (LE), Dual Core + LP Core, 240MHz, Embedded Flash 4MB (XMC), Embedded PSRAM 2MB (AP_3v3)
Crystal frequency:  40MHz
USB mode:           USB-Serial/JTAG
MAC:                f4:12:fa:59:b3:e0

Stub flasher running.
Changing baud rate to 460800...
Changed.

Configuring flash size...
Flash will be erased from 0x00000000 to 0x001acfff...
Wrote 1754608 bytes (1148691 compressed) at 0x00000000 in 22.8 seconds (615.2 kbit/s).
Hash of data verified.

Hard resetting via RTS pin...

 Sat 2026-04-18 10:24:51 [ 33.6s ] ~.....\space-sim\engineering-board.....
```

If flashing fails partway through, retry without `--baud 460800` to use the slower
default speed.

Troubleshooting reference: <https://docs.micropython.org/en/latest/esp32/tutorial/intro.html#troubleshooting-installation-problems>

---

## Step 4 — Verify MicroPython is running

The last step will have left the device in bootloader mode. To run the newly flashed MicroPython
firmware, press the RESET button to get the device out of bootloader mode, then open a serial
terminal with Putty.

- VS Code's Serial Monitor sort of works, but it seems pretty flaky
- mpremote can also do a serial terminal with `mpremote repl` - this will not interrupt a running program

If you don't see the REPL prompt '>>> ' then try pressing ENTER.

---

## Step 5 — Install a file transfer tool

[mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) is the
official MicroPython tool for copying files to the board:

```powershell
pip install mpremote
```

Copy project files to the board. mpremote does not support wildcarding natively, and for some
reason, Powershell is not expanding \*.py on its own, so you have to do it manually:

```powershell
mpremote cp @(dir *.py) :
```

mpremote will only copy files that have changed since the last copy, which is very convenient for development. If you want to force a copy, use `mp cp -f`.

Other useful mpremote commands: (I have aliased mpremote to mp for convenience)

- Ctrl-x will exit the REPL
- mpremote cp -f local.yp :/ - to force a copy even if the file is unchanged
- mpremote df - show free space remaining
- mpremote ls [-r] :path - list files on the board
- mpremote cat :main.py - print the contents of main.py on the board (useful for debugging)
- mpremote repl - open a serial terminal to the board (alternative to Putty)
- mpremote rm [-rv] :path
- mpremote mkdir/rmdir/touch
- mpremote tree -s <dirs> prints a tree of dirs

---

## Heads-up: install script needs updating

MicroPython on ESP32-S3 does **not** mount as a USB drive during normal operation
(unlike CircuitPython). The current `install-circuit-python-to-board.ps1` uses `robocopy`
which requires a mounted drive — it will not work as-is.

The `robocopy` call needs to be replaced with `mpremote` commands, for example:

```powershell
mpremote connect COM? cp *.py :
mpremote connect COM? cp secrets-eng-board.py :secrets.py
```

AI suggested [rshell](https://github.com/dhylands/rshell) as a tool to copy files, but got a bunch
of crashes trying to use it, when PuTTY was displaying the REPL just fine. From a comment I saw in
the repo, I suspect it is not maintained, and not longer compatible with modern MicroPython
firmware.

---

## VS Code Setup for MicroPython Development

### Extensions

#### MicroPython / Embedded

| Extension     | ID                   | Purpose                                                                                                                                      |
| ------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **MicroPico** | `paulober.pico-w-go` | MicroPython REPL, file sync, run-on-device — the closest VS Code gets to Thonny. Works with any MicroPython board via serial, not just Pico. |

#### Python (host-side)

| Extension   | ID                         | Purpose                                                                                                                               |
| ----------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Python**  | `ms-python.python`         | Core Python extension: interpreter selection, debugger, test runner. Required.                                                        |
| **Pylance** | `ms-python.vscode-pylance` | Language server: fast IntelliSense, type checking, go-to-definition, auto-imports. Installed automatically with the Python extension. |
| **Ruff**    | `charliermarsh.ruff`       | Fast all-in-one linter and formatter (replaces Pylint + Black/isort). Recommended over Pylint for new projects.                       |

---

### Workspace settings

Create `.vscode/settings.json` in the project root with the following. The key entries
are the `python.analysis.extraPaths` stubs and the Pylance type checking mode:

```json
{
    "python.analysis.extraPaths": ["./stubs"],
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.ignore": ["lib/**"],
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    },
    "ruff.lint.args": ["--config=pylintrc"],
    "microPico.syncFolder": "",
    "microPico.syncFileTypes": ["py"],
    "microPico.syncAllFileTypes": false
}
```

---

### MicroPython stubs (critical for IntelliSense)

MicroPython modules (`machine`, `network`, `neopixel`, etc.) don't exist on the host,
so Pylance will show errors on every import. Fix this by installing MicroPython stubs:

```powershell
pip install micropython-esp32-stubs
```

Then point Pylance at them by adding the stubs path to `python.analysis.extraPaths`
in `.vscode/settings.json` (already included in the template above). The stubs package
installs to your Python environment's `site-packages` — find the path with:

```powershell
python -c "import micropython_esp32_stubs; print(micropython_esp32_stubs.__file__)"
```

Alternatively, use the community stub package which covers more boards:

```powershell
pip install micropython-stubs
```

Stub reference: <https://github.com/Josverl/micropython-stubs>

---

### Creating a VS Code Profile

To keep this setup isolated from your other Python work, create a named profile:

1. Open the Command Palette (`Ctrl+Shift+P`) → **Profiles: Create Profile**
2. Name it `MicroPython`
3. Choose **Copy from Current Profile** so your existing theme/keybindings carry over
4. Install the extensions listed above into this profile
5. Switch profiles via the bottom-left gear icon → **Profiles**

Profile documentation: <https://code.visualstudio.com/docs/editor/profiles>
