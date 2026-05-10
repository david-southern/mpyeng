"""Generate docs/ws2812-timing.xlsx — a wire-time and max-FPS calculator for WS2812 chains.

Run this with `python docs/generate-ws2812-timing.py` from the repo root to regenerate the
spreadsheet. The XLSX itself is editable in Excel; this script is for reproducibility and to
record where the numbers come from.
"""

from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill


HERE = Path(__file__).parent
OUT = HERE / "ws2812-timing.xlsx"


wb = openpyxl.Workbook()
ws = wb.active
ws.title = "WS2812 Wire Time"

# Styles
bold = Font(bold=True)
header = Font(bold=True, size=14)
input_fill = PatternFill("solid", fgColor="FFF2CC")  # light yellow
calc_fill = PatternFill("solid", fgColor="E2EFDA")  # light green


# Title block
ws["A1"] = "WS2812 Wire-Time Calculator"
ws["A1"].font = header
ws.merge_cells("A1:H1")

ws["A2"] = (
    "Per-frame wire time and theoretical max FPS for a WS2812 chain. "
    "Yellow cells are inputs; green cells are calculated."
)
ws.merge_cells("A2:H2")


# INPUTS
row = 4
ws.cell(row, 1, "INPUTS").font = bold
row += 1

ws.cell(row, 1, "Total pixels:")
cell = ws.cell(row, 2, 2220)
cell.fill = input_fill
ws.cell(row, 3, "Right board: 30 trays × 74 pixels = 2220. Left board: ~768.")
PIXELS = f"$B${row}"
row += 1

ws.cell(row, 1, "Bit rate (kbps):")
cell = ws.cell(row, 2, 800)
cell.fill = input_fill
ws.cell(row, 3, "WS2812 nominal: 800. WS2812B may tolerate higher (see notes).")
BITRATE = f"$B${row}"
row += 1

ws.cell(row, 1, "Latch time (µs):")
cell = ws.cell(row, 2, 50)
cell.fill = input_fill
ws.cell(row, 3, "Min low time at end of frame. WS2812 spec: 50 µs.")
LATCH = f"$B${row}"
row += 1

ws.cell(row, 1, "Bits per pixel:")
cell = ws.cell(row, 2, 24)
cell.fill = input_fill
ws.cell(row, 3, "Fixed by WS2812 protocol (8 bits each of G, R, B). Editable for what-if.")
BPP = f"$B${row}"
row += 2


# CALCULATIONS
ws.cell(row, 1, "CALCULATIONS").font = bold
row += 1

ws.cell(row, 1, "Time per bit (µs):")
ws.cell(row, 2, f"=1000/{BITRATE}").fill = calc_fill
ws.cell(row, 3, f"= 1000 / bit_rate_kbps")
TBIT = f"$B${row}"
row += 1

ws.cell(row, 1, "Time per pixel (µs):")
ws.cell(row, 2, f"={BPP}*{TBIT}").fill = calc_fill
ws.cell(row, 3, f"= bits_per_pixel × time_per_bit")
TPIXEL = f"$B${row}"
row += 1

ws.cell(row, 1, "Wire time (ms):")
ws.cell(row, 2, f"={PIXELS}*{TPIXEL}/1000").fill = calc_fill
ws.cell(row, 3, f"= total_pixels × time_per_pixel / 1000")
WIRE = f"$B${row}"
row += 1

ws.cell(row, 1, "Latch time (ms):")
ws.cell(row, 2, f"={LATCH}/1000").fill = calc_fill
ws.cell(row, 3, "= latch_us / 1000")
LATCHMS = f"$B${row}"
row += 1

ws.cell(row, 1, "Total frame time (ms):")
ws.cell(row, 2, f"={WIRE}+{LATCHMS}").fill = calc_fill
ws.cell(row, 3, "= wire + latch")
TOTAL = f"$B${row}"
row += 1

ws.cell(row, 1, "Max FPS:").font = bold
fps_cell = ws.cell(row, 2, f"=1000/{TOTAL}")
fps_cell.fill = calc_fill
fps_cell.font = bold
ws.cell(row, 3, "= 1000 / total_frame_ms")
row += 2


# COMPARISON TABLE
ws.cell(row, 1, "MAX FPS — pixel count × bit rate").font = bold
row += 1
ws.cell(row, 1, "(Uses input latch and bits-per-pixel from above; varies pixels and bit rate)")
row += 2

# Header row
ws.cell(row, 1, "Pixel count ↓  /  Bit rate kbps →").font = bold
bit_rates = [800, 1000, 1200, 1600, 2400, 3200]
for i, br in enumerate(bit_rates):
    cell = ws.cell(row, 2 + i, br)
    cell.font = bold
row += 1

pixel_configs = [
    (74, "1 tray"),
    (370, "5 trays / 1 bus row"),
    (768, "Left panel (David's est.)"),
    (1110, "Half right panel"),
    (2220, "Full right panel"),
]
for n_pixels, label in pixel_configs:
    ws.cell(row, 1, f"{n_pixels} px — {label}")
    for i, br in enumerate(bit_rates):
        # max_fps = 1000 / (n_pixels * bpp / br + latch / 1000)
        formula = f"=1000/({n_pixels}*{BPP}/{br}+{LATCH}/1000)"
        ws.cell(row, 2 + i, formula).number_format = "0.0"
    row += 1

row += 2


# NOTES
ws.cell(row, 1, "NOTES").font = bold
row += 1
notes = [
    "WS2812 nominal data rate is 800 kbps with strict timing (~150 ns pulse-width tolerance).",
    "WS2812B variants (most modern chains) tolerate higher rates — community reports of 1.0–1.6",
    "Mbps working with short cable runs and WS2812B-V5 chips.",
    "Above ~1.6 Mbps, signal integrity becomes the limiting factor: cable length, termination,",
    "and driver impedance all matter. Verify on the actual chain with an oscilloscope.",
    "SK6812 chips generally tolerate higher rates than WS2812. WS2813 (dual-data-line variant)",
    "tends to be more forgiving still. Mileage varies by manufacturer batch.",
    "Latch time dominates total frame time on short chains. For 74-pixel single-tray chains the",
    "latch is ~2% of total; for 2220-pixel chains it's <0.1%.",
    "",
    "RP2 PIO-side note: the PIO program in drivers/local_neopixel.py uses 10 PIO cycles per",
    "WS2812 bit (T1=2, T2=5, T3=3). To run at 1.6 Mbps the PIO clock would need to be raised",
    "from 8 MHz to 16 MHz; for 3.2 Mbps it'd be 32 MHz. RP2350 system clock is 150 MHz default,",
    "so the PIO clock has plenty of headroom — the limit is the LED chain, not the controller.",
]
for note in notes:
    ws.cell(row, 1, note)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    row += 1


# Column widths
ws.column_dimensions["A"].width = 35
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 65
for col_letter in "DEFGH":
    ws.column_dimensions[col_letter].width = 12


wb.save(OUT)
print(f"Wrote {OUT}")
