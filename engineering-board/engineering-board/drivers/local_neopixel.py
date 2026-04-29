# pyright: reportUndefinedVariable=false
# ruff: noqa: F821

# Code retrieved from:
# <https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/led/neopixel/neopixel.py>

# NeoPixel driver for MicroPython
# MIT license; Copyright (c) 2016 Damien P. George, 2021 Jim Mussared

from utils.color_utils import NEO_PACKED_BPP, buffer_to_neo_packed, copy_buffer_pixels, neo_packed_to_buffer

# Example using the RP2350's Programmable IO to drive a set of WS2812 LEDs.

from machine import Pin
import rp2


# Define the WS2812 LED driver PIO program.
# * sideset_init = the initial value of the sideset pins
# * out_shiftdir = the direction to shift bits out of the output shift register (OSR)
# * autopull = whether to automatically pull a new word from the FIFO into the OSR when it is empty
# * pull_thresh = the number of bits that must be in the OSR before autopull will trigger.
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812_program():

    # Timing for WS2812 pixel strips @ 800K bits/second:
    # * Ref: <https://cdn-shop.adafruit.com/datasheets/WS2812.pdf>
    # * Each pixel expects to receive 24 bits of data, 8 bits each of GRB (in that order)
    # * Each bit is signaled by a high pulse followed by a low pulse. The duration of the high and
    # low pulses determines whether the bit is a 0 or a 1.
    # * The total duration of one bit must be 1250 nanoseconds
    # 
    # Individual logic bits are encoded as:
    # * LOGICAL BIT 0:
    #   * High for 350 nanoseconds
    #   * Low for 800 nanoseconds
    # * LOGICAL BIT 1:
    #   * High for 700 nanoseconds
    #   * Low for 600 nanoseconds
    #
    # Finally, a low signal of at least 50 microseconds is needed at the end of each frame to
    # 'latch' (apply) the pixels and prepare the strip to start a new frame.
    # 
    # Note: each pixel past the first does "internal reshaping amplification" so that the signal
    # doesn't degrade as it travels down the strip.
    # 
    # From the micropython-lib source code for 800kbps timing, the timing values in nanoseconds
    # (400, 850, 800, 450)
    # 
    # At 800Kbps, with 8M PIO cycles per second, the logic timings look like this: (integer cycle
    # counts)
    # * LOGICAL 0: High 2 cycles, Low 8 cycles
    # * LOGICAL 1: High 7 cycles, Low 3 cycles
    # 
    # Thus the timings below:    
    # * T1 = 2 ==> The 2 high cycles of LOGICAL 0, and the first 2 high cycles of LOGICAL 1
    # * T2 = 5 ==> The first 5 low cycles of LOGICAL 0, and the remaining 5 high cycles of LOGICAL 1
    # * T3 = 3 ==> The remaining 3 low cycles of LOGICAL 0, and the 3 low cycles of LOGICAL 1
    # 
    # Note that this program does not appear to enforce the 50 microsecond latch time at the end of
    # each frame. I guess callers are responsible for making sure not to send a new frame within 50
    # microseconds of the previous frame?
    
    T1 = 2
    T2 = 5
    T3 = 3
    
    # This is where the PIO program will resume when the wrap() instruction is reached.
    wrap_target()

    label("bitloop")

    # * out(dest, bit_count) => shift 1 bit out of the OSR to X, for comparison in the next
    #   instruction.
    # * .side(0) sets the side pin value to low. This happens before the instruction is executed.
    #   This happens even if the instruction stalls (i.e. the FIFO is empty), so the side pin will
    #   be driven low while waiting for data to be pushed.
    # * The [T3 - 1] instruction delays for T3-1 cycles after the out() instruction executes. This
    #   means that the side pin will be driven low for a total of T3 cycles, one for the out()
    #   instruction and T3-1 for the delay.
    # * This establishes 3 cycles of LOW to make up the last 3 cycles of both LOGICAL 0 and LOGICAL
    #   1. (This will be prepended to a new frame, but that's okay, as we must have already been low
    #   for at least 50ms, so 3 more cycles won't affect anything)
    #
    # Note: We only consume 24 bits from OSR for each pixel, while the TX FIFO pushes 32 bits at a
    # time. This works because we have set *autopull* and *pull_threshold* to 24, meaning that after
    # 24 bits have been shifted out of the OSR, a new word will automatically be pulled from the
    # FIFO into the OSR. The remaining 8 bits in the OSR will be ignored, and the next 24 bits will
    # be shifted out for the next pixel. (This is why when pushing data into the state machine FIFO,
    # we have to shift the pixel data left by 8 bits, so that the 0xRRGGBB00 data is in the upper 24
    # bits of the word, and the lower 8 bits are just padding that will be ignored)
    out(x, 1).side(0)[T3 - 1]

    # Push the side pin high for T1 (2 cycles) - remember the .side() takes effect before the
    # instruction executes. This establishes the first high cycles of both LOGICAL 0 and LOGICAL 1.
    jmp(not_x, "do_zero").side(1)[T1 - 1]

    # If X was 1 in the jmp instruction, then keep the pin high for another T2 (5 cycles) for a
    # total of 7 cycles high for a LOGICAL 1, then jump to "bitloop" to push the pin low for T3 (3
    # cycles), making up the full LOGICAL 1 timing of 7 cycles high and 3 cycles low.
    jmp("bitloop").side(1)[T2 - 1]
    
    label("do_zero")

    # If X was 0 in the jmp instruction, then the pin has been high for 2 cycles, so drive it low
    # for T2 (5 cycles), then wrap() back up the the out, which adds T3 (3 cycles) of additional
    # low, to make a total of 8 low cycles, establishing the full LOGICAL 0 timing of 2 high cycles
    # and 8 low cycles
    nop().side(0)[T2 - 1]
    
    wrap()


# Configure the number of WS2812 LEDs.
NUM_LEDS = 8
# Create the PIO StateMachine with the ws2812 program, outputting on Pin(22) (as a side-set pin).
STATE_MACHINE_ID = 0
WORD_SHIFT = 8
sm = rp2.StateMachine(STATE_MACHINE_ID, ws2812_program, freq=8_000_000, sideset_base=Pin(22))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

# Cycle colours.
for i in range(4 * NUM_LEDS):
    for j in range(NUM_LEDS):
        r = j * 100 // (NUM_LEDS - 1)
        b = 100 - j * 100 // (NUM_LEDS - 1)
        if j != i % NUM_LEDS:
            r >>= 3
            b >>= 3
        ar[j] = r << 16 | b
    sm.put(
        ar, WORD_SHIFT
    )  # Push 32 bit words onto the state machine's FIFO input, shifting each word left by WORD_SHIFT (word << WORD_SHIFT) bits. This is necessary because the RGB packing in each word of the array is 0x00RRGGBB, while the ws2812_program expects the data to be left-aligned in the 32-bit word (0xRRGGBB00).
    time.sleep_ms(50)

# Fade out.
for i in range(24):
    for j in range(NUM_LEDS):
        ar[j] >>= 1
    sm.put(ar, WORD_SHIFT)
    time.sleep_ms(50)


class LocalNeoPixel:
    # G R B W
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, timing=1):
        self.pin = pin
        self.n = n
        self.buf = bytearray(n * NEO_PACKED_BPP)
        self.pin.init(pin.OUT)
        # Timing arg can either be 1 for 800kHz or 0 for 400kHz,
        # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).
        self.timing = (
            ((400, 850, 800, 450) if timing else (800, 1700, 1600, 900)) if isinstance(timing, int) else timing
        )

    def __len__(self):
        return self.n

    def __setitem__(self, pixel_index, neo_packed: int):
        """Set the pixel at <pixel_index> to neo_packed color value."""
        neo_packed_to_buffer(neo_packed, self.buf, pixel_index, 1)

    def __getitem__(self, pixel_index):
        buf_offset = pixel_index * NEO_PACKED_BPP
        return buffer_to_neo_packed(self.buf, buf_offset)

    def fill(self, neo_packed: int, dest_pixel_offset: int, pixel_count: int):
        neo_packed_to_buffer(neo_packed, self.buf, dest_pixel_offset, pixel_count)

    def set_buf(self, source_buf: bytes, dest_pixel_offset: int, pixel_count: int):
        """Set the internal NeoPixel buffer to the provided bytearray starting at buf_offset for
        len(buf) bytes."""
        copy_buffer_pixels(source_buf, self.buf, dest_pixel_offset, pixel_count)

    def write(self):
        # BITSTREAM_TYPE_HIGH_LOW = 0
        # bitstream(self.pin, 0, self.timing, self.buf)
