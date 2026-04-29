# A basic description of the RP2 PIO programming

## Sources

- The Micropython docs on RP2-specific functionality:
  - <https://docs.micropython.org/en/latest/library/rp2.html#pio-related-functions>
- The RP2040 Datasheet (chapter 3)
  - <https://pip-assets.raspberrypi.com/categories/814-rp2040/documents/RP-008371-DS-1-rp2040-datasheet.pdf?disposition=inline>
- The RP C/C++ SDK (Chapter 3.2.2 has a line-by-line explanation of the WS2812 PIO program)
  - <https://pip-assets.raspberrypi.com/categories/609-microcontroller-boards/documents/RP-009085-KB-1-raspberry-pi-pico-c-sdk.pdf?disposition=inline>
- I later found the RP2350 data sheet. Chapter 11 describes the newer PIO model, and the docs in
  this chapter are much better than the RP2040 docs I used to make these notes. The RP2350 has
  additional PIO features, but appears to be backward-compatible with the RP2040 notes in this file.
  - <https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008373-DS-2-rp2350-datasheet.pdf?disposition=inline>

## PIO Architecture Notes

A PIO program defines 4 sets of GPIO pins: in, out, set, and sideset. The initial GPIO pins for each
set is declared in the StateMachine constructor, (this program only declares sideset pins) along
with the frequency (number of PIO cycles per second) of the program execution. The asm_pio decorator
declares: (among other things, check the MP docs)

- the number of consecutive GPIO pins that makes up each set
- the initial GPIO pin direction (input or output) of each set
- the initial GPIO value of each set.
- The direction to shift bits out/in of/to the OSR/ISR (*out_shiftdir*/*in_shiftdir*)
- whether to automatically pull/push new data from/to the FIFO into the OSR/ISR when it is empty
  (*autopull*/*autopush*)
- the number of bits that must be in the OSR before autopull will trigger
  (*pull_thresh*/*push_thresh*)

The State Machine constructor also declares: (fields that are used in the current WS2812 program,
check the MPY docs for others)

- *freq* - the number of PIO cycles per second. The constructor automatically calculates the clock
  divider based on the system clock frequency and the requested PIO frequency.
- *sideset_base* - the first GPIO pin of the sideset pin group.

## State machine architecture

The PIO "word size" is 32 bits. The PIO assembly language works on the incoming/outgoing words one
bit at a time. Each PIO instance has:

### TX FIFO

A 4 word input stream "TX FIFO" that can be written to by the main CPU and read by the PIO program by
shifting words from the FIFO into the OSR (Output Shift Register)

- pull instructions remove a 32-bit word from the TX FIFO and place it into the OSR
- out instructions shift data from the OSR to other destinations, 1..32 bits at a time
- the OSR fills with zeros as data is shifted out
- If *autopull* is enabled, the state machine will automatically refill the OSR from the FIFO once
  *autopull_threshold* number of bits have been shifted out
- Shift direction can be LEFT or RIGHT, per *out_shiftdir*

### RX FIFO

A 4 word output stream "RX FIFO" that can be written to by the PIO program by shifting words from the
ISR (Input Shift Register) into the RX FIFO, and read by the main CPU

- Same parameters as the TX FIFO

### Scratch Registers

Two 32 bit scratch registers (x and y) that can be read/written by the PIO program and used for
conditional branching and temporary storage.

### Control logic

- The asm_pio program that the PIO runs
- A PC (Program Counter) that tracks which instruction of the asm_pio program is currently
  executing, and is manipulated by the jmp/wrap instructions.

On every system clock cycle, each state machine fetches, decodes and executes one instruction. Each
instruction takes precisely one cycle, unless it explicitly stalls (such as the WAIT instruction).
Instructions may also insert a delay of up to 31 cycles before the next instruction is executed to
aid the writing of cycle-exact programs.

The program counter, or PC, points to the location in the instruction memory being executed on this
cycle. Generally, the PC increments by one each cycle, wrapping at the end of the instruction memory.
Jump instructions are an exception and explicitly provide the next value that PC will take.

Each PIO instruction is 16 bits in size. Generally, 5 of those bits in each instruction are used for
the "delay" which is usually 0 to 31 cycles (after the instruction completes and before moving to
the next instruction).

If you have read the PIO chapter of the RP2350 Datasheet, you may have already know that these 5
bits can be used for a different purpose:

> .side_set 1

This directive says we’re stealing one of those delay bits to use for "side-set". The state machine
will use this bit to drive the values of some pins, once per instruction, in addition to what the
instructions are themselves doing. This is very useful for high frequency use cases (e.g. pixel
clocks for DPI panels)

## Python asm_pio code notes

The Python asm_pio code has the following instructions:

- wrap() - causes the PIO execution to jump to the wrap_target(). This instruction is
  automatically appended to the end of a PIO program if it is not already present.
- wrap_target() - marks the target of the wrap() instruction
- label("name") - marks the target of a any of the jmp() instructions. The value of the label()
  can also be an integer, probably to be used with the word() command below?
- word(value, label) - Inserts a **16 bit** *value* into the assembled output. If *label* is
  provided, the PIO looks up the label's value and logical-ORs it with *value* before inserting it
  into the assembled output.
  - I think this means the assembly program that is being defined, rather than the RX FIFO output of
      the program. This would indicate that the *label* concept could be used in combination with the
      WORD value of a JMP instruction to define the jump offset, assuming that the JMP WORD has empty
      bits where the *label* value is ORed in?
- jmp(label) - an unconditional jump to the indicated label
- jmp(cond, label) - a conditional jump to the indicated label. The condition can be one of:
  - *not_x*, *not_y* : true if the register is zero
  - *x_dec*, *y_dec* : true if the register is non-zero, then post-decrement the register value by 1
  - *x_not_y* : True if X is not equal to Y
  - *pin* : true if the input pin is set
  - *not_osre* : true if the OSR is not empty
- wait(polarity, src, index) - Blocking wait for a high/low condition on the indicated PIN or IRQ
  line.
  - *polarity* => 0 for low, 1 for high
  - *src* => *gpio* (absolute pin), *pin* (relative to the SM's *in_base* pins), or *irq*
  - *index* => range of [0-31] - the index for *src*
- in(src, bit_count) - shift *bit_count* bits from the indicated *src* (*pins*, *x*, *y*, *null*, *isr*, *osr*) to
  the ISR
- out(dest, bit_count) - shift *bit_count* bits from the OSR to the indicated *dest* (*pins*, *x*, *y*,
  *pindirs*, *pc*, *isr*, *exec*)
- push(...) - Push the ISR to the RX FIFO, then clear the ISR to zero. Can take these forms:
  - push()
  - push(block) - the instruction stalls if the RX FIFO is full. This is the default.
  - push(noblock)
  - push(iffull) - only push if the input shift count has reached its threshold
  - push(iffull, block)
  - push(iffull, noblock)
- pull(...) - Pull a word from the TX FIFO to the OSR. Can take these forms:
  - pull()
  - pull(block) - the instruction stalls if the TX FIFO is empty. This is the default.
  - pull(noblock)
  - pull(ifempty) - only pull if the output shift count has reached its threshold
  - pull(ifempty, block)
  - pull(ifempty, noblock)
- mov(dest, src) - Moves *dest* (*pins*, *x*, *y*, *exec*, *pc*, *isr*, *osr*) to *src* (*pins*,
  *x*, *y*, *null*, *status*, *isr*, *osr*). This argument can be optionally modified by wrapping it
  in invert() or reverse() (but not both together). -- Whatever that means
- irq(index) or irq(mode, index) - Set or clear the IRQ flag where *index* is in the range [0-7] or
  rel(0) to rel(7), and *mode* is one of: *block* (the instruction stalls until the flag is cleared by
  another entity), *clear* (clears the flag). Relative IRQ indices add the State Machine's ID to the
  IRQ index with modulo-4 addition. IRQs 0-3 are visible to the processor, while 4-7 are internal
  to state machines.
- set(dest, data) Set *dest* (*pins*, *x*, *y*, *pindirs*) to *data* (0-31).
- nop() - does nothing for one cycle. (assembled to mov(y, y) with no side effects)
- .side(value) - This is a modifier that can be applied to any instructions, and controls the
  side-set pin values. The *value* is the bits to be output on the side-set pins. -- Possibly a
  bitmask applied to the sequential side-set pins??
- .delay(value) - This is a modifier that can be applied to any instructions, and specifies how
  many cycles to delay after the instruction executes. *value* can be [0-31]
- [value] - a modifier that is equivalent to .delay(value)
