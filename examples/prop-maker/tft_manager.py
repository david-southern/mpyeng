# import board
# import terminalio
# from adafruit_display_text import label
# from displayio import Group
# from eng_utils import logger

# logger.info("Initializing TFT Manager")

# class TFTManagerClass:
#     def __init__(self):
#         self.timeValue = ""
#         self.voltageValue = ""

#         self.display = board.DISPLAY
#         self.display.rotation = 180

#         self.timeLabel = label.Label(terminalio.FONT, text="Time:", scale=2)
#         self.timeLabel.anchor_point = (0, 0)
#         self.timeLabel.anchored_position = (0, 0)

#         self.voltageLabel = label.Label(terminalio.FONT, text="Volt:", scale=2)
#         self.voltageLabel.anchor_point = (0, 0)
#         self.voltageLabel.anchored_position = (0, 14)

#         self.main_group = Group()
#         self.main_group.append(self.timeLabel)
#         self.main_group.append(self.voltageLabel)

#         self.display.root_group = self.main_group

#     @property
#     def Time(self):
#         return self.timeValue

#     @Time.setter
#     def Time(self, value):
#         self.timeValue = value
#         self.timeLabel.text = f"Time: {self.timeValue}" 

#     @property
#     def Voltage(self):
#         return self.voltageValue

#     @Voltage.setter
#     def Voltage(self, value):
#         self.voltageValue = value
#         self.voltageLabel.text = f"Volt: {self.voltageValue}" 

#     def __str__(self):
#         return f"TFTManager:{self.timeValue}"

# TFTManager = TFTManagerClass()
