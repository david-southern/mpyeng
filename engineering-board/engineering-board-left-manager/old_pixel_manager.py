# from __future__ import annotations

# import random
# from math import floor
# import time
# import board

# from neopixel import NeoPixel  # pyright: ignore[reportMissingImports]
# from eng_utils import ENABLE_LEFT_PIXELS, ENABLE_RIGHT_PIXELS, SlowLog, disabledString, logger, ENABLE_PIXELS

# # Power Consumption notes: Powering 768 red (255,0,0) pixels at 10% brightness pulls 1.35 amps, according to my
# # multimeter.  Increasing the brightness to 0.2 draws 2.3 amps.  If you increase the brightness, make sure that your
# # power supply can handle the current draw
# PIXEL_BRIGHTNESS = 0.1
# #  #px | Color         | Current Draw @ brightness = 0.1
# #  768 |   0,   0,  0  | 0.64
# #  768 | 255,   0,  0  | 1.35
# #  768 |   0, 255,  0  | 1.33
# #  768 |   0,   0, 255 | 1.33
# #  768 | 255, 255,   0 | 2.04
# #  768 | 255,   0, 255 | 2.04
# #  768 |   0, 255, 255 | 2.02
# #  768 | 255, 255, 255 | 2.55

# # Usually the component color updaters will send the pixel data as part of the update.  The PixelManager will
# # automatically re-send the pixel data this often, in case an update is missed
# PIXEL_REFRESH_SECONDS = 0.25
# PIXEL_HEARTBEAT_SECONDS = 2
# LOG_PIXEL_LAYOUT = True

# LED_DATA_PIN = None

# if board.board_id == "adafruit_feather_rp2040":
#     LED_DATA_PIN = board.D25

# if board.board_id == "grandcentral_m4_express":
#     LED_DATA_PIN = board.D13


# if LED_DATA_PIN is None:
#     logger.error(f"LED_DATA_PIN is not defined for board id {board.board_id}.")
#     ENABLE_PIXELS = False
#     ENABLE_LEFT_PIXELS = False
#     ENABLE_RIGHT_PIXELS = False

# if ENABLE_LEFT_PIXELS:
#     PIXEL_GRID_COUNT = 6
#     LARGE_GRID_COUNT = 2
#     SMALL_GRID_COUNT = 4
# else:
#     PIXEL_GRID_COUNT = 0
#     LARGE_GRID_COUNT = 0
#     SMALL_GRID_COUNT = 0

# LARGE_GRID_SIZE = 16
# LEDS_PER_LARGE_GRID = LARGE_GRID_SIZE * LARGE_GRID_SIZE
# LARGE_GRID_LED_BASE_INDEX = 0

# SMALL_GRID_SIZE = 8
# LEDS_PER_SMALL_GRID = SMALL_GRID_SIZE * SMALL_GRID_SIZE
# SMALL_GRID_LED_BASE_INDEX = (
#     LARGE_GRID_LED_BASE_INDEX + LEDS_PER_LARGE_GRID * LARGE_GRID_COUNT
# )

# LEFT_BOARD_LED_COUNT = (
#     SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * SMALL_GRID_COUNT
# )

# if ENABLE_RIGHT_PIXELS:
#     CARD_BUS_COUNT = 6
#     CARDS_PER_BUS = 5
#     TRAYS_PER_BUS = 2

#     # Mini test
#     CARD_BUS_COUNT = 1
#     CARDS_PER_BUS = 1
#     TRAYS_PER_BUS = 2
    
# else:
#     CARD_BUS_COUNT = 0
#     CARDS_PER_BUS = 0
#     TRAYS_PER_BUS = 0

# LEDS_PER_CARD = 25
# TRAY_LEDS_PER_CARD = 4
# LEDS_PER_TRAY = TRAY_LEDS_PER_CARD * CARDS_PER_BUS

# CARDS_LED_BASE_INDEX = LEFT_BOARD_LED_COUNT
# CARD_TRAYS_LED_BASE_INDEX = (
#     CARDS_LED_BASE_INDEX + CARD_BUS_COUNT * CARDS_PER_BUS * LEDS_PER_CARD
# )

# RIGHT_BOARD_LED_COUNT = (
#     CARD_TRAYS_LED_BASE_INDEX
#     + CARD_BUS_COUNT * TRAYS_PER_BUS * LEDS_PER_TRAY
#     - LEFT_BOARD_LED_COUNT
# )

# TOTAL_LED_COUNT = LEFT_BOARD_LED_COUNT + RIGHT_BOARD_LED_COUNT

# BLACK: tuple[int, int, int] = (0, 0, 0)
# RED: tuple[int, int, int] = (255, 0, 0)
# YELLOW: tuple[int, int, int] = (255, 150, 0)
# GREEN: tuple[int, int, int] = (0, 255, 0)
# BLUE: tuple[int, int, int] = (0, 0, 255)


# class PixelManagerClass:
#     PixelGridLEDStartIndex = [
#         LARGE_GRID_LED_BASE_INDEX,
#         LARGE_GRID_LED_BASE_INDEX + LEDS_PER_LARGE_GRID,
#         SMALL_GRID_LED_BASE_INDEX,
#         SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID,
#         SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * 2,
#         SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * 3,
#     ]

#     PixelGridLEDLength = [
#         LEDS_PER_LARGE_GRID,
#         LEDS_PER_LARGE_GRID,
#         LEDS_PER_SMALL_GRID,
#         LEDS_PER_SMALL_GRID,
#         LEDS_PER_SMALL_GRID,
#         LEDS_PER_SMALL_GRID,
#     ]

#     PixelGridSize = [
#         LARGE_GRID_SIZE,
#         LARGE_GRID_SIZE,
#         SMALL_GRID_SIZE,
#         SMALL_GRID_SIZE,
#         SMALL_GRID_SIZE,
#         SMALL_GRID_SIZE,
#     ]

#     CardLEDStartIndex: list[list[int]] = []
#     CardTrayLEDStartIndex: list[list[list[int]]] = []

#     @classmethod
#     def classInitialize(cls):
#         if len(cls.CardLEDStartIndex) < 1:
#             PixelManagerClass.CardLEDStartIndex = [
#                 [
#                     CARDS_LED_BASE_INDEX + (bus * CARDS_PER_BUS + card) * LEDS_PER_CARD
#                     for card in range(CARDS_PER_BUS)
#                 ]
#                 for bus in range(CARD_BUS_COUNT)
#             ]

#         if len(cls.CardTrayLEDStartIndex) < 1:
#             PixelManagerClass.CardTrayLEDStartIndex = [
#                 [
#                     [
#                         CARD_TRAYS_LED_BASE_INDEX
#                         + (bus * TRAYS_PER_BUS + tray) * LEDS_PER_TRAY
#                         + card * TRAY_LEDS_PER_CARD
#                         for card in range(CARDS_PER_BUS)
#                     ]
#                     for tray in range(TRAYS_PER_BUS)
#                 ]
#                 for bus in range(CARD_BUS_COUNT)
#             ]

#     def __init__(self):
#         PixelManagerClass.classInitialize()
#         self.__nextPixelUpdate = time.monotonic() + PIXEL_REFRESH_SECONDS
#         self.__nextHeartbeat = time.monotonic() + PIXEL_HEARTBEAT_SECONDS
#         self.heartbeatColor = RED

#         logger.info(
#             f"Creating PixelManager{disabledString(ENABLE_PIXELS)} on LED_DATA_PIN {LED_DATA_PIN} with {TOTAL_LED_COUNT} pixels"
#         )

#         if LOG_PIXEL_LAYOUT:
#             self.LogPixelLayout()

#         SlowLog(
#             f"PixelManager initialized. Pixels disabled: {disabledString(ENABLE_PIXELS)}"
#         )

#         if ENABLE_PIXELS:
#             self.enabledString = ""
#             self.pixels = NeoPixel(
#                 LED_DATA_PIN,
#                 TOTAL_LED_COUNT,
#                 brightness=PIXEL_BRIGHTNESS,
#                 auto_write=False,
#                 pixel_order="GRB",
#             )

#             logger.info(
#                 f"PixelManager{disabledString(ENABLE_PIXELS)}: Clearing {TOTAL_LED_COUNT} total pixels"
#             )

#             self.pixels.fill(BLACK)
#             self.pixels.show()

#     def SetTrayColor(self, bus: int, card: int, color: tuple):
#         if not ENABLE_RIGHT_PIXELS:
#             return

#         if bus < 0 or bus >= CARD_BUS_COUNT:
#             logger.error(f"Pixel Bus index {bus} is out of range.")
#             return

#         if card < 0 or card >= CARDS_PER_BUS:
#             logger.error(f"Pixel Card index {card} is out of range.")
#             return

#         logger.info(
#             f"PixelManager{disabledString(ENABLE_PIXELS)}: Setting Tray B{bus}/C{card} to color: {color}"
#         )

#         for tray in range(TRAYS_PER_BUS):
#             readerPixelIndexStart = PixelManagerClass.CardTrayLEDStartIndex[bus][tray][
#                 card
#             ]
#             readerPixelIndexEnd = readerPixelIndexStart + LEDS_PER_TRAY

#             if ENABLE_PIXELS:
#                 for pixelIndex in range(readerPixelIndexStart, readerPixelIndexEnd):
#                     self.pixels[pixelIndex] = color

#     def SetCardColor(self, bus: int, card: int, color: tuple):
#         if not ENABLE_RIGHT_PIXELS:
#             return

#         if bus < 0 or bus >= CARD_BUS_COUNT:
#             logger.error(f"Pixel Bus index {bus} is out of range.")
#             return

#         if card < 0 or card >= CARDS_PER_BUS:
#             logger.error(f"Pixel Card index {card} is out of range.")
#             return

#         logger.info(
#             f"PixelManager{disabledString(ENABLE_PIXELS)}: Setting Card B{bus}/C{card} to color: {color}"
#         )

#         readerPixelIndexStart = PixelManagerClass.CardLEDStartIndex[bus][card]
#         readerPixelIndexEnd = readerPixelIndexStart + LEDS_PER_CARD

#         if ENABLE_PIXELS:
#             for pixelIndex in range(readerPixelIndexStart, readerPixelIndexEnd):
#                 self.pixels[pixelIndex] = color

#     def SetPowerGridColor(self, gridIndex: int, x: int, y: int, color: tuple):
#         if not ENABLE_LEFT_PIXELS:
#             return

#         SlowLog(f"Setting Pixel Grid #{gridIndex} color")
#         if gridIndex < 0 or gridIndex >= PIXEL_GRID_COUNT:
#             logger.error(f"Pixel Grid index {gridIndex} is out of range.")
#             return

#         gridSize = PixelManagerClass.PixelGridSize[gridIndex]

#         if x < 0 or x >= gridSize or y < 0 or y >= gridSize:
#             logger.error(
#                 f"Pixel Grid index {gridIndex} coordinates ({x}, {y}) is out of range."
#             )
#             return

#         gridPixelIndex = (
#             PixelManagerClass.PixelGridLEDStartIndex[gridIndex] + y * gridSize
#         )

#         # The pixel grids that we are using map the pixels as a zig-zag linear string: Pixel zero starts at the
#         # bottom-left of the grid, and the pixels increment to the right until the string reaches the edge of the grid.
#         # Then the string moves up one pixel, and proceeds incrementing to the left.
#         if y % 2 == 0:
#             gridPixelIndex += x
#         else:
#             gridPixelIndex += (gridSize - 1) - x

#         if ENABLE_PIXELS:
#             self.pixels[gridPixelIndex] = color

#     def ShowPixels(self):
#         SlowLog("Showing pixel data")
#         if ENABLE_PIXELS:
#             self.pixels.show()

#     def UpdatePixelData(self):
#         SlowLog("Updating pixel data")
#         if not ENABLE_PIXELS:
#             return

#         if time.monotonic() > self.__nextHeartbeat:
#             self.heartbeatColor = BLACK if self.heartbeatColor == RED else RED
#             self.pixels[0] = self.heartbeatColor
#             self.__nextHeartbeat = time.monotonic() + PIXEL_HEARTBEAT_SECONDS

#             # Disco cards - each heartbeat, pick a random card and set it to a random color
#             bus = random.randint(0, CARD_BUS_COUNT - 1)
#             card = random.randint(0, CARDS_PER_BUS - 1)
#             color = (
#                 random.randint(0, 255),
#                 random.randint(0, 255),
#                 random.randint(0, 255),
#             )
#             self.SetCardColor(bus, card, color)

#             # Pick the negative of that color, and set the card's tray to that color
#             negColor = (255 - color[0], 255 - color[1], 255 - color[2])
#             self.SetTrayColor(bus, card, negColor)

#         if time.monotonic() > self.__nextPixelUpdate:
#             self.__nextPixelUpdate = time.monotonic() + PIXEL_REFRESH_SECONDS
#             self.pixels.show()

#     def CylonTest(self):
#         logger.info("Running Cylon Pixel Test")

#         testCount = 768
#         brightness = 0.1

#         CYLON_COLOR = (255, 0, 0)
#         BASE_COLOR = (0, 0, 0)
#         self.pixels.fill(BASE_COLOR)

#         cylon = 0
#         prevCylon = 0
#         deltaCylon = 1
#         cylonSpeed = 0.05
#         nextCylonUpdate = time.monotonic() + cylonSpeed

#         cylonCount = 0

#         heartbeatFreq = 2
#         nextHeartbeat = time.monotonic() + heartbeatFreq

#         while True:
#             if time.monotonic() > nextHeartbeat:
#                 logger.info(
#                     f"Cylon Pixel Test color: {BASE_COLOR}, brightness: {brightness} {cylon}/{testCount}"
#                 )
#                 nextHeartbeat = time.monotonic() + heartbeatFreq

#             if nextCylonUpdate > time.monotonic():
#                 nextCylonUpdate = time.monotonic() + cylonSpeed

#                 prevCylon = cylon
#                 cylon += deltaCylon

#                 if cylon < 0 or cylon >= testCount:
#                     deltaCylon = -deltaCylon
#                     cylon += deltaCylon
#                     cylonCount += 1
#                     logger.info(f"Cylon Pixel Test {cylonCount}")

#                 if floor(cylon) != floor(prevCylon):
#                     self.pixels[floor(prevCylon)] = BASE_COLOR
#                     self.pixels[floor(cylon)] = CYLON_COLOR
#                     self.pixels.show()

#     def __str__(self):
#         return f"PixelManager{disabledString(ENABLE_PIXELS)}"

#     def LogPixelLayout(self):
#         logger.info(f"PixelManager{disabledString(ENABLE_PIXELS)}: Pixel Layout:")
#         logger.info(
#             f"  Total Pixels: {TOTAL_LED_COUNT} (Left Board: {LEFT_BOARD_LED_COUNT}, Right Board: {RIGHT_BOARD_LED_COUNT})"
#         )
#         logger.info(
#             f"  Large Grids: {LARGE_GRID_COUNT} of size {LARGE_GRID_SIZE}x{LARGE_GRID_SIZE}, starting at index {LARGE_GRID_LED_BASE_INDEX}, total pixels: {LEDS_PER_LARGE_GRID * LARGE_GRID_COUNT}"
#         )
#         logger.info(
#             f"  Small Grids: {SMALL_GRID_COUNT} of size {SMALL_GRID_SIZE}x{SMALL_GRID_SIZE}, starting at index {SMALL_GRID_LED_BASE_INDEX}, total pixels: {LEDS_PER_SMALL_GRID * SMALL_GRID_COUNT}"
#         )
#         for gridIndex in range(PIXEL_GRID_COUNT):
#             logger.info(
#                 f"    Grid #{gridIndex}: Start Index: {PixelManagerClass.PixelGridLEDStartIndex[gridIndex]}, Length: {PixelManagerClass.PixelGridLEDLength[gridIndex]}, Size: {PixelManagerClass.PixelGridSize[gridIndex]}x{PixelManagerClass.PixelGridSize[gridIndex]}"
#             )

#         logger.info(
#             f"  Cards: {CARD_BUS_COUNT} Buses of {CARDS_PER_BUS} Cards each, each card has {LEDS_PER_CARD} pixels, starting at index {CARDS_LED_BASE_INDEX}, total pixels: {CARD_BUS_COUNT * CARDS_PER_BUS * LEDS_PER_CARD}"
#         )
#         for bus in range(CARD_BUS_COUNT):
#             for card in range(CARDS_PER_BUS):
#                 logger.info(
#                     f"    Bus #{bus} Card #{card}: Start Index: {PixelManagerClass.CardLEDStartIndex[bus][card]}, Length: {LEDS_PER_CARD}"
#                 )

#         logger.info(
#             f"  Card Trays: {CARD_BUS_COUNT} Buses of {TRAYS_PER_BUS} Trays each, each tray has {CARDS_PER_BUS} cards with {LEDS_PER_TRAY} pixels per tray, starting at index {CARD_TRAYS_LED_BASE_INDEX}, total pixels: {CARD_BUS_COUNT * TRAYS_PER_BUS * LEDS_PER_TRAY}"
#         )
#         for bus in range(CARD_BUS_COUNT):
#             for tray in range(TRAYS_PER_BUS):
#                 for card in range(CARDS_PER_BUS):
#                     logger.info(
#                         f"    Bus #{bus} Tray #{tray} Card #{card}: Start Index: {PixelManagerClass.CardTrayLEDStartIndex[bus][tray][card]}, Length: {LEDS_PER_TRAY}"
#                     )


# PixelManager = PixelManagerClass()
