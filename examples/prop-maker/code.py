import time
from neoslider_manager import NeoSliderManager
from pixgrid_manager import PixGridManager
from rotary_encoder_manager import RotaryEncoderManager
from seven_segment_display_manager import SevenSegmentDisplayManager
from eng_utils import lerp_color, logger

# Other cool Adafruit props:
# 12 key macropad - https://www.adafruit.com/product/5128
# Prop Maker Feather - https://www.adafruit.com/product/5768

logger.info("Initializing PropMaker example")

HEARTBEAT_FREQUENCY_SEC = 2
next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

PIX_GRID_UPDATE_FREQUENCY_SEC = 0.1
next_pixgrid_update = time.monotonic() + PIX_GRID_UPDATE_FREQUENCY_SEC

SLIDER_COLOR_MIN = (0, 250, 0)
SLIDER_COLOR_MID = (128, 250, 0)
SLIDER_COLOR_MAX = (250, 0, 0)

ROTARY_COLOR_MIN = (0, 128, 0)
ROTARY_COLOR_MID = (196, 128, 0)
ROTARY_COLOR_MAX = (250, 0, 0)

rotary_button_held = False
rotary_last_position = None

rotary_position_range = 24
rotary_position_half_range = rotary_position_range / 2

slider_last_value = None

while True:
    if time.monotonic() > next_pixgrid_update:
        next_pixgrid_update = time.monotonic() + PIX_GRID_UPDATE_FREQUENCY_SEC
        PixGridManager.UpdateRainbow()
    
    if NeoSliderManager.Value != slider_last_value:
        slider_last_value = NeoSliderManager.Value

        for powerDisplay in SevenSegmentDisplayManager.AllDisplays():
            powerDisplay.Value = slider_last_value


        if slider_last_value < 512:
            slider_lerp_position = slider_last_value / 512
            slider_color = lerp_color(SLIDER_COLOR_MIN, SLIDER_COLOR_MID, slider_lerp_position)
            NeoSliderManager.SetPixelColor(slider_color)
        else:
            slider_lerp_position = (slider_last_value - 512) / 512
            slider_color = lerp_color(SLIDER_COLOR_MID, SLIDER_COLOR_MAX, slider_lerp_position)
            NeoSliderManager.SetPixelColor(slider_color)

        # logger.info(f"NeoSlider: value: {slider_last_value}, "
        #             + f"lerp_position: {slider_lerp_position}, color: {slider_color}")


    normalized_rotary_position = abs(RotaryEncoderManager.Position) % rotary_position_range

    if normalized_rotary_position != rotary_last_position:
        rotary_last_position = normalized_rotary_position

        if rotary_last_position < rotary_position_half_range:
            lerp_position = rotary_last_position / (rotary_position_half_range - 1)
            RotaryEncoderManager.SetPixelColor(lerp_color(ROTARY_COLOR_MIN, ROTARY_COLOR_MID, lerp_position))
        else:
            lerp_position = (rotary_last_position - rotary_position_half_range) / (rotary_position_half_range - 1)
            RotaryEncoderManager.SetPixelColor(lerp_color(ROTARY_COLOR_MID, ROTARY_COLOR_MAX, lerp_position))

        # logger.info(f"Rotary Encoder Position: {RotaryEncoderManager.Position}, "
        #             + f"normalized: {normalized_rotary_position}, lerp_position: {lerp_position}")


    if time.monotonic() > next_heartbeat:
        logger.info(f"Heartbeat: Slider Value: {slider_last_value}, "
                    + f"Rotary Position: {rotary_last_position}")
        next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

 

 