# pyright: reportUndefinedVariable=false
# ruff: noqa: F821

# WS2812 NeoPixel driver for MicroPython on the RP2350, using a PIO state machine.
#
# PIO program adapted from:
#   <https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/led/neopixel/neopixel.py>
#   NeoPixel driver for MicroPython
#   MIT license; Copyright (c) 2016 Damien P. George, 2021 Jim Mussared

import array

from machine import Pin
import rp2

from utils.color_utils import copy_buffer_pixels, neo_packed_to_buffer


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
    # Note that this program does not enforce the 50-microsecond latch time at the end of each
    # frame. Callers must avoid sending a new frame within 50 microseconds of the previous one. In
    # practice the periodic refresh in PixelStripManager handles this.

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
    # we have to shift the pixel data left by 8 bits, so that the 0xGGRRBB00 data is in the upper 24
    # bits of the word, and the lower 8 bits are just padding that will be ignored.)
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


# WS2812 spec is 800 kbps (10 PIO cycles/bit × 8 MHz). 16 MHz (1.6 Mbps) was tried 2026-05-09
# on a single ~80-pixel card grid and produced no output at all — the chips didn't latch the
# signal. The card grids in use are cheap, likely original WS2812 (not WS2812B-V5), which have
# tighter timing tolerance and don't run above spec. Don't bother retrying overclock without
# different hardware. Higher FPS path: split the chain across multiple state machines.
WS2812_PIO_FREQ = 8_000_000

# Each FIFO word is one packed pixel int (0x00GGRRBB). sm.put() shifts each word left by this many
# bits before pushing to the FIFO so the GRB triple lands in the upper 24 bits of the word, where
# the PIO program shifts it out MSB-first.
WS2812_PUT_SHIFT = 8


class LocalNeoPixel:
    """WS2812 NeoPixel strip driven by a per-instance RP2 PIO state machine.

    Buffer layout: array.array('I'), one neo-packed int per pixel (0x00GGRRBB). The 4-byte
    alignment matches the PIO autopull width — see color_utils for the wire-format rationale.
    """

    # Class-level counter that hands out a unique state-machine ID per LocalNeoPixel instance.
    # The RP2350 has 12 state machines (3 PIO blocks × 4 SMs); we expect ~3 instances total
    # across the firmware, comfortably within budget.
    _next_sm_id = 0

    def __init__(self, pin: Pin, n: int):
        self.pin = pin
        self.n = n
        self.buf = array.array("I", [0] * n)

        sm_id = LocalNeoPixel._next_sm_id
        LocalNeoPixel._next_sm_id += 1
        self.sm = rp2.StateMachine(sm_id, ws2812_program, freq=WS2812_PIO_FREQ, sideset_base=pin)
        self.sm.active(1)

    def __len__(self) -> int:
        return self.n

    def __setitem__(self, pixel_index: int, neo_packed: int):
        """Set the pixel at <pixel_index> to <neo_packed> (a packed 0x00GGRRBB color int)."""
        self.buf[pixel_index] = neo_packed

    def __getitem__(self, pixel_index: int) -> int:
        return self.buf[pixel_index]

    def fill(self, neo_packed: int, dest_pixel_offset: int, pixel_count: int):
        """Set <pixel_count> pixels starting at <dest_pixel_offset> all to <neo_packed>."""
        neo_packed_to_buffer(neo_packed, self.buf, dest_pixel_offset, pixel_count)

    def set_buf(self, source_buf, dest_pixel_offset: int, pixel_count: int):
        """Copy <pixel_count> pixels from <source_buf> into self.buf at <dest_pixel_offset>.
        <source_buf> must be 4-byte-aligned (array.array('I') is)."""
        copy_buffer_pixels(source_buf, self.buf, dest_pixel_offset, pixel_count)

    def write(self):
        """Push the entire buffer to the PIO state machine for output to the strip."""
        self.sm.put(self.buf, WS2812_PUT_SHIFT)
