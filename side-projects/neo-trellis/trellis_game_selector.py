from collections import namedtuple
from adafruit_led_animation import color as AdaColors
from neotrellis_manager import NeoTrellisManager
from eng_utils import eng_logger
from trellis_game_base import Coord, TrellisGame

from font_junction_regular_10 import FONT as BITMAP_FONT

def get_pixel_color(bitmap, x, y):
    return bitmap[ y * bitmap.width + x ]

def render_glyph(glyphChar, color):
    glyph = BITMAP_FONT.get_glyph(ord(glyphChar)) # pyright: ignore
    for row in range(glyph.height):
        for col in range(glyph.width):
            NeoTrellisManager.setButtonColor(col, row, color if get_pixel_color(glyph.bitmap, col, row) else AdaColors.BLACK)

GameSelection = namedtuple('GameSelection', ['name', 'glyphChar', 'color', 'gameClass'])

nextButton = Coord(7, 0)
nextButtonColor = AdaColors.GOLD
selectButton = Coord(7, 7)
selectButtonColor = AdaColors.GREEN

class TrellisGameSelector(TrellisGame):
    def __init__(self):
        super()
        self.name = "Selector"
        self.game_index = -1
        self.AvailGames = []
        self._selectedGameClass = None

    def addGame(self, name, glyphChar, color, gameClass):
        self.AvailGames.append(GameSelection(name, glyphChar, color, gameClass))

    def renderGame(self):
        NeoTrellisManager.fill(AdaColors.BLACK)
        NeoTrellisManager.setButtonColor(nextButton.x, nextButton.y, nextButtonColor)
        NeoTrellisManager.setButtonColor(selectButton.x, selectButton.y, selectButtonColor)
        render_glyph(self.AvailGames[self.game_index].glyphChar, self.AvailGames[self.game_index].color)

    def buttonPressed(self, x, y, event):
        eng_logger.info(f"Selector: Button Pressed: {x}, {y}, Event: {event}")
        button = Coord(x, y)
        if button == nextButton:
            self.game_index = (self.game_index + 1) % len(self.AvailGames)
            self.renderGame()
            return

        if button == selectButton:
            self.selectedGameClass = self.AvailGames[self.game_index].gameClass
            return

    @property
    def selectedGameClass(self) -> TrellisGame | None:
        return self._selectedGameClass

    @selectedGameClass.setter
    def selectedGameClass(self, gameClass: TrellisGame) -> None:
        self._selectedGameClass = gameClass

    def Update(self):
        super().Update()
        if self.game_index == -1:
            self.game_index = 0
            self.renderGame()
