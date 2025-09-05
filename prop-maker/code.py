import time
import board
import adafruit_logging as logging
from adafruit_ina219 import ADCResolution, INA219

import displayio
import terminalio

from adafruit_display_text import label
import adafruit_displayio_sh1107

i2c = board.I2C()

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
logger.info(f'Starting Voltector!')

ina219 = INA219(i2c)
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S

displayio.release_displays()

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2

display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

# Draw some label text
current_text = label.Label(terminalio.FONT, text="Current: ", color=0xFFFFFF, x=8, y=4)
voltage_text = label.Label(terminalio.FONT, text="Voltage: ", color=0xFFFFFF, x=8, y=14)
# power_text = label.Label(terminalio.FONT, text="Power: ", color=0xFFFFFF, x=8, y=24)
message_text = label.Label(terminalio.FONT, text="Message: ", color=0xFFFFFF, x=8, y=24)
splash.append(current_text)
splash.append(voltage_text)
# splash.append(power_text)
splash.append(message_text)

# now = 

while True:
    current_text.text = f"Current:  {ina219.current} mA"
    voltage_text.text = f"Voltage:  {ina219.bus_voltage} V"
    # power_text.text =   f"Power:    {ina219.power} W"
    message_text.text = f"Time:     {time.monotonic()}"
    time.sleep(1)


