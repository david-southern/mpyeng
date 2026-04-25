# Programming Notes

## My Devices

- Adafruit Feather TFT ESP32-S3
- Pimoroni Pico Plus 2 W - RP2350

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

## Getting a REPL on the device

VS Code Serial monitor works.

If you want to make sure of the COM port of the device:

Get-PnpDevice -Class Ports | Where-Object Status -eq 'OK' | Where-Object DeviceId -Match 'PID' |
Select-Object FriendlyName,DeviceID

As of April 2026, none of my other connected USB devices report a PID, so hopefully that is sufficient.

## Pre-installed modules

From a clean flash of the firmware, open the repl() and run `help('modules')` to see the pre-installed modules:

```
MicroPython v1.28.0 on 2026-04-06; Generic ESP32S3 module with ESP32S3
Type "help()" for more information.
>>> help('modules')
__main__          btree             io                ssl
_asyncio          builtins          json              struct
_boot             cmath             machine           sys
_espnow           collections       machine           time
_onewire          cryptolib         math              tls
_thread           deflate           micropython       uasyncio
_webrepl          dht               mip/__init__      uctypes
aioespnow         ds18x20           neopixel          umqtt/robust
apa106            errno             network           umqtt/simple
array             esp               ntptime           upysh
asyncio/__init__  esp32             onewire           urequests
asyncio/core      espnow            os                vfs
asyncio/event     flashbdev         platform          webrepl
asyncio/funcs     framebuf          random            webrepl_setup
asyncio/lock      gc                re                websocket
asyncio/stream    hashlib           requests/__init__
binascii          heapq             select
bluetooth         inisetup          socket
Plus any modules on the filesystem
```
