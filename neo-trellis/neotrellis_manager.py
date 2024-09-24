import board
from eng_utils import eng_logger
from adafruit_led_animation import color as AdaColors
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

ENABLE_NEO_TRELLIS = True

eng_logger.info("Initializing NeoTrellis Manager")

class NeoTrellisManagerClass:
    TRELLIS_WIDTH = 8
    TRELLIS_HEIGHT = 8

    def __init__(self):
        self.neoTrellis:MultiTrellis = None # pyright: ignore[reportAttributeAccessIssue]

        self.subscribers = set()

        self.buttonColor = [ 
            [ AdaColors.BLACK ] * NeoTrellisManagerClass.TRELLIS_WIDTH
            for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT) 
        ]

        if not ENABLE_NEO_TRELLIS:
            return
        
        try:
            #create the i2c object for the trellis
            i2c_bus = board.I2C()

            # create the individual trellis controllers
            self.trelli = [
                [
                    NeoTrellis(i2c_bus, False, addr=0x30, auto_write=False), 
                    NeoTrellis(i2c_bus, False, addr=0x31, auto_write=False)
                ],
                [
                    NeoTrellis(i2c_bus, False, addr=0x2E, auto_write=False), 
                    NeoTrellis(i2c_bus, False, addr=0x2F, auto_write=False)
                ]
            ]

            self.neoTrellis = MultiTrellis(self.trelli)
        except Exception as e:
            eng_logger.error(f"Error initializing NeoTrellis: {e}")
            return
        
        self.neoTrellis.brightness = 0.1

        for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT - 1, -1, -1):
            for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
                # Activate rising/falling edge events on all keys
                self.neoTrellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                # self.neoTrellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
                self.neoTrellis.set_callback(x, y, self.buttonEvent)
                self.setButtonColor(x, y, AdaColors.AMBER)
            self.neoTrellis.show()

        for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT):
            for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
                self.setButtonColor(x, y, AdaColors.BLACK)
            self.neoTrellis.show()

        eng_logger.info("NeoTrellisManager Initialized")           

    def adjustCoords(self, x, y):
        # In the orientation that I want to use, with the USB port on the top right,
        # the x any y coordinates need to be rotated 180 degrees. Since they are integers,
        # I can just subtract them from the max value.
        x = NeoTrellisManagerClass.TRELLIS_WIDTH - 1 - x
        y = NeoTrellisManagerClass.TRELLIS_HEIGHT - 1 - y
        return (x, y)

    def subscribe(self, subscriber) -> None:
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber) -> None:
        self.subscribers.remove(subscriber)

    def buttonEvent(self, x, y, edge):
        x, y = self.adjustCoords(x, y)
        eng_logger.info(f"MGR: Button Event: {x}, {y}, {edge}")
        for subscriber in self.subscribers:
            subscriber(x, y, edge)

    def setBrightness(self, brightness):
        if self.neoTrellis is None:
            return
        self.neoTrellis.brightness = brightness

    def getButtonColor(self, x, y):
        x, y = self.adjustCoords(x, y)
        return self.buttonColor[x][y]

    def setButtonColor(self, x, y, color):
        if self.neoTrellis is None:
            return
        
        x, y = self.adjustCoords(x, y)
        self.buttonColor[x][y] = color
        self.neoTrellis.color(x, y, color)

    def Update(self):
        if self.neoTrellis is None:
            return
        self.neoTrellis.sync()
        self.neoTrellis.show()

    def __str__(self):
        return f"NeoTrellis"

NeoTrellisManager = NeoTrellisManagerClass()

