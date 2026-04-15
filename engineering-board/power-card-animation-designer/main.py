import time
import tkinter as tk
from tkinter import ttk
from power_cards_presentation_specs import CardSpecHelpers, CardCategories
from color_utils import ok_to_css

PIXEL_SIZE = 50
GRID_BORDER = 20
FRAME_INTERVAL_MS = 33  # ~30 fps
LEGEND_SWATCH_SIZE = 30
LEGEND_PAD = 6

GRID_LINE = 1
GRID_WIDTH = CardSpecHelpers.WIDTH * PIXEL_SIZE + (CardSpecHelpers.WIDTH - 1) * GRID_LINE
GRID_HEIGHT = CardSpecHelpers.HEIGHT * PIXEL_SIZE + (CardSpecHelpers.HEIGHT - 1) * GRID_LINE
CANVAS_WIDTH = GRID_WIDTH + 2 * GRID_BORDER
CANVAS_HEIGHT = GRID_HEIGHT + 2 * GRID_BORDER

# Color mask options for the right-click popup and legend
COLOR_MASK_OPTIONS = [
    ("BLACK", CardSpecHelpers.COLOR_MASK_BLACK),
    ("FULL_COLOR", "9"),
    ("MID_COLOR", "5"),
    ("DIM_COLOR", "1"),
    ("WAVE", CardSpecHelpers.COLOR_MASK_WAVE),
    ("RANDOM_BRIGHTNESS", CardSpecHelpers.COLOR_MASK_RANDOM_BRIGHTNESS),
    ("RANDOM_COLOR", CardSpecHelpers.COLOR_MASK_RANDOM_COLOR),
    ("FADE_OUT", CardSpecHelpers.COLOR_MASK_FADE_OUT),
    ("FADE_IN", CardSpecHelpers.COLOR_MASK_FADE_IN),
    ("LIGHTNING", CardSpecHelpers.COLOR_MASK_LIGHTNING),
]

spec = CardSpecHelpers.getCardSpec(CardSpecHelpers.MAIN_COMPUTER_ID)
animation_duration_s = spec.animation_duration

root = tk.Tk()
root.title(spec.name)
root.resizable(False, False)

# Dropdown for card selection
selected_id = tk.StringVar(value=CardSpecHelpers.MAIN_COMPUTER_ID)
dropdown = ttk.Combobox(root, textvariable=selected_id, values=CardSpecHelpers.ALL_CARD_IDS, state="readonly", width=40)
dropdown.grid(row=0, column=0, columnspan=2, pady=(8, 4))

def on_card_selected(event):
    global spec, animation_duration_s, start_time
    spec = CardSpecHelpers.getCardSpec(selected_id.get())
    animation_duration_s = spec.animation_duration
    start_time = time.monotonic()
    root.title(spec.name)

dropdown.bind("<<ComboboxSelected>>", on_card_selected)

# Main grid canvas (left)
canvas = tk.Canvas(
    root,
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    highlightthickness=0,
    bg="white",
)
canvas.grid(row=1, column=0, sticky="n")

# Legend panel (right)
legend_frame = tk.Frame(root, bg="#222222", padx=10, pady=10)
legend_frame.grid(row=1, column=1, sticky="ns", padx=(0, 8), pady=0)

legend_label = tk.Label(legend_frame, text="Color Masks", fg="white", bg="#222222", font=("TkDefaultFont", 10, "bold"))
legend_label.pack(anchor="w", pady=(0, 6))

legend_swatch_ids = []  # list of (canvas_widget, rect_id, mask_char)
for label_text, mask_char in COLOR_MASK_OPTIONS:
    row_frame = tk.Frame(legend_frame, bg="#222222")
    row_frame.pack(anchor="w", pady=2)
    swatch_canvas = tk.Canvas(row_frame, width=LEGEND_SWATCH_SIZE, height=LEGEND_SWATCH_SIZE, highlightthickness=1, highlightbackground="#555555", bg="black")
    swatch_canvas.pack(side="left", padx=(0, LEGEND_PAD))
    rect_id = swatch_canvas.create_rectangle(0, 0, LEGEND_SWATCH_SIZE, LEGEND_SWATCH_SIZE, fill="#000000", outline="")
    legend_swatch_ids.append((swatch_canvas, rect_id, mask_char))
    tk.Label(row_frame, text=f"{label_text}  ({mask_char})", fg="#cccccc", bg="#222222", font=("TkDefaultFont", 9)).pack(side="left")

# Create grid rectangle items once
rect_ids = {}
for y in range(CardSpecHelpers.HEIGHT):
    for x in range(CardSpecHelpers.WIDTH):
        x0 = GRID_BORDER + x * (PIXEL_SIZE + GRID_LINE)
        y0 = GRID_BORDER + y * (PIXEL_SIZE + GRID_LINE)
        rect_id = canvas.create_rectangle(x0, y0, x0 + PIXEL_SIZE, y0 + PIXEL_SIZE, fill="#000000", outline="")
        rect_ids[(x, y)] = rect_id

start_time = time.monotonic()

def color_to_hex(color):
    rgb = ok_to_css(color).to_dict()
    return "#{:02x}{:02x}{:02x}".format(
        int(rgb["coords"][0] * 255),
        int(rgb["coords"][1] * 255),
        int(rgb["coords"][2] * 255),
    )

def update_frame():
    elapsed = time.monotonic() - start_time
    progress = (elapsed % animation_duration_s) / animation_duration_s
    pixels = spec.render_frame(progress)

    for y in range(CardSpecHelpers.HEIGHT):
        for x in range(CardSpecHelpers.WIDTH):
            idx = CardSpecHelpers.xy_to_index(x, y)
            r, g, b = pixels[idx]
            canvas.itemconfig(rect_ids[(x, y)], fill=f"#{r:02x}{g:02x}{b:02x}")

    # Update legend swatches using the current spec's colors
    for swatch_canvas, rect_id, mask_char in legend_swatch_ids:
        colors = CardSpecHelpers.string_mask_to_color_mask(
            [mask_char], spec.bright_color, spec.dim_color, progress
        )
        swatch_canvas.itemconfig(rect_id, fill=color_to_hex(colors[0]))

    root.after(FRAME_INTERVAL_MS, update_frame)

update_frame()

def canvas_to_grid(ex, ey):
    """Convert canvas event coords to grid (x, y), or None if outside the grid."""
    gx = ex - GRID_BORDER
    gy = ey - GRID_BORDER
    cell_step = PIXEL_SIZE + GRID_LINE
    col = gx // cell_step
    row = gy // cell_step
    if gx < 0 or gy < 0:
        return None
    if gx % cell_step >= PIXEL_SIZE or gy % cell_step >= PIXEL_SIZE:
        return None
    if 0 <= col < CardSpecHelpers.WIDTH and 0 <= row < CardSpecHelpers.HEIGHT:
        return int(col), int(row)
    return None

def on_right_click(event):
    pos = canvas_to_grid(event.x, event.y)
    if pos is None:
        return
    col, row = pos
    popup = tk.Menu(root, tearoff=0)
    for label, mask_char in COLOR_MASK_OPTIONS:
        popup.add_command(label=f"{label}  ({mask_char})", command=lambda c=col, r=row, ch=mask_char: set_mask_char(c, r, ch))
    popup.tk_popup(event.x_root, event.y_root)

def set_mask_char(x, y, ch):
    row_str = spec.static_string_mask[y]
    spec.static_string_mask[y] = row_str[:x] + ch + row_str[x + 1:]

canvas.bind("<Button-3>", on_right_click)
root.mainloop()
