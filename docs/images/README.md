# docs/images/

Reference photos of the engineering-board rig, checked in for future human
collaborators and our own reference.

Claude-specific instructions for this folder are in [`CLAUDE.md`](CLAUDE.md).

Dimensions in the notes below are approximate — the frame and other physical
parts are pre-existing objects we won't be modifying. The functional facts
that matter for the firmware / executive design are: the frame is deep
enough to hold all the electronics behind the board, and the MDF board sits
flush in the front opening.

## Index

- **Frame Back** — `frame-back.jpeg`
  - An oblique shot of the back of the exterior sheet metal (2mm thick) frame. Note the flat flange
    around the perimeter - this will be used to mount the frame to the wall, and is 10cm wide. Outer
    dimensions of this frame are 108cm tall, and 78cm wide.
- **Frame Front** — `frame-front.jpeg`
  - An oblique shot of the front of the exterior sheet metal frame. Note the approx 10mm channel
    around the inside of the front opening. Each board panel will be mounted to the frame using this
    channel, with the board's back face flush with the frame. Decorative piping will hide the
    attachment. Dimensions of the channel are approx 92cm tall, 62cm wide. (Designed to hold a 3'
    tall by 2' wide MDF panel)
- **Left Board Front** — `left-board-front.jpeg`
  - A nearly straight on shot of the front (patron facing) side of the Left Engineering Board. This
    board was complete at one time, but as you can see, it has been partially disassembled to
    collect parts and specs for the right panel work. The board is 3' tall by 2' wide, and is made
    of 5mm MDF.
  - Components of the board include:
    - The two large 16x16 pixel grids on the left are the "Left Wing" (top) and "Right Wing"
      (bottom) animated power source displays. The current placeholder animation shows a "power
      supplied over time" bar graph where the bottom two rows are green, the next two are blue, then
      yellow, then red. I believe the graph shifts to the left one pixel per second. This animation
      is only for demoing the grid capability. It will likely remain, as we all have way too much
      work to do, but the fact is that I can't think of any scenario/puzzle where the wing power
      would fluctuate that much. I expect it will usually remain constant until combat damage or an
      emergency happens.
    - In between them, are two seven-segment displays showing the current power supplied by each
      wing. Current thought for puzzle design is that power numbers for each wing may be 0
      (damaged), or in the range of 500-5000 each. As I recall, these seven segs should be a
      "neutral" color, probably blue or green, but I can't power the board right now, so that is not
      authoritative.
    - Immediately to the right of each wing display you can see a column of four "switchboard"
      sources. These are 1/4" audio jacks, which make up part of the "Switchboard" subsystem. They
      will be used to connect each wing to one or more of the transformers on the right side, using
      bright red electric guitar cables.
    - On the right side of the board, we have four "Transformers" top to bottom. Each transformer
      has several physical elements. From board inside to outside, we have:
    - Four Switchboard sinks. These are also 1/4" audio jacks, and will be used to connect the
      transformers to the switchboard sources on the left side. As you can see from the switchboard
      design, each wing can be connected to 0-4 transformers, but each transformer can be connected
      to only 0-1 wings.
    - The display portion of the transformer. From top-to-bottom:
    - A seven segment display that represents the "max power that this transformer can provide over
      all (2) connected Power Busses". If I recall, this seven-seg is red.
    - An 8x8 pixel grid showing the animated power output of the transformer. Will likely be the
      same as the wing power animation, but not guaranteed.
    - Finally two Switchboard Sources that drive Power Busses on the right board.
- **Left Board Back** — `left-board-back.jpeg`
  - The wiring side of the Left Engineering Board — a hand-built rat's nest from the prior
    incarnation, with masking-tape labels and freehand wire runs. Cleanup is parked under
    [TODO § Long-range](../../TODO.md#re-route-the-left-board-wiring-on-its-back-side).
- **Right Board Layout** — `right-board-layout.jpeg`
  - This board is still very much WIP. This image shows the MDF panel cut to receive the bus
    controls and the Power Card Trays for each Power Bus.
  - The board hosts six Power Busses, each a row that starts with the Bus Control cluster, and then
    lays out 5 Power Card Trays.
  - Each Bus control cluster (extreme left column) has (top-to-bottom)
  - A seven segment display showing the current power available to the the bus. I expect this seven
    seg to be red.
  - The Switchboard Sink for the Bus
  - A seven segment display showing the current power consumed by the bus. Probably will be yellow.
    Depending on puzzle difficulty level and scenario design, if consumption exceeds supply, there
    may be any number of problems: (this is all speculative, puzzle design hasn't started yet) for
    the 3rd graders, probably the power card trays start showing blinking red status bars with no
    actual in-game effect, while for the 10th graders, the bus may "overload" and cause damage to
    the ship or a puzzle failure.
  - Next are the five Power Card Trays. Each tray has a 5 pixel "status bar" across the top and
    bottom that shows whether the executive considers that tray empty, in use (powered), in use
    (brownout), damaged, etc.
  - The middle of each tray contains an 8x8 pixel grid that shows an animation indicating the
    currently loaded Power Card, if any. These are the animations that the content kids will be designing.
- **Power Card Tray Placement** — `power-card-tray-placement.jpeg`
  - This image shows how the Power Card Tray will sit in one of the bus slots. The tray sits in the
    slots you see, and the exposed flat front of the card sits flush with the board. The exposed
    wiring you see is just me being lazy, all hardware will project through the panel and be
    connected in the frame space behind the board.
  - Power Cards are a clear acrylic rectangle with a 3D printed frame around the edge. The frame
    includes a place to hold two pogo pins connected to a resistor that will be used to identify
    which Power Card is in which tray, per the voltage divider scheme described elsewhere.
- **Power Card Tray Hardware** — `power-card-tray-hardware.jpeg`
  - Shows the back of the Power Card tray with the LED hardware described above. Difficult to see in
    this shot, but there is also a well for two pogo-pins that will make contact with the Power
    Card. When completed, there will be wires running from the pogo pins to the microcontroller
    (data-out) and to a shared +3.3V power-in line.
