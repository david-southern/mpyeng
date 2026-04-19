# Plan: Reorganize project into subdirectories

## Critical Constraint: Python Import Naming

**Hyphens in filenames/directory names break Python imports.** `from card-reader import ...` and `from card-reader.module import ...` are syntax errors. Only standalone scripts that are never imported (like `repl-functions.py`) can use hyphens.

**Recommendation:** Use underscores for all importable module files and package directories.

## Proposed Directory Structure

```
engineering-board/
├── main.py
├── AGENTS.md, ruff.toml, requirements.txt
├── boot_out*.txt, *.jpg, *.png
├── convert_animations.py          (standalone CPython script)
├── repl-functions.py              (standalone REPL script)
├── *.ps1, *.md                    (build scripts, docs)
│
├── utils/
│   ├── __init__.py                (empty)
│   ├── eng_utils.py               (LoggerClass, timers, SlowLog, disabledString)
│   ├── device_manager.py          (DeviceManager class + singleton)
│   ├── color_utils.py             (Color class, color constants)
│   ├── profiling.py               (profiling system)
│   ├── protocol_resources.py      (shared data structures: EnginePower, SystemPower, etc.)
│   ├── demo_data_manager.py       (DemoDataManager, Debouncer, demo data constants)
│   ├── pixel_strip_manager.py     (PixelStripManager - shared hw driver)
│   ├── dave_tm1637.py             (TM1637 driver - keep original name)
│   ├── tm1637.py                  (unused backup driver - keep, don't delete)
│   └── mcp3008.py                 (split from card_manager: _MCP3008, _AnalogIn)
│
├── power_cards/
│   ├── __init__.py                (empty)
│   ├── power_card.py              (PowerCard class only)
│   ├── animation.py               (animation data + CardAnimation, was power_card_animation.py)
│   ├── card_ids.py                (ID constants, was power_card_ids.py)
│   └── categories.py             (category data, was power_card_categories.py)
│
├── card_tray/
│   ├── __init__.py                (empty)
│   ├── constants.py               (PIXEL_CARD_TRAYS, TRAY_BRIGHTNESS, PowerStateEnum, CARD_TRAY_COLORS, etc.)
│   ├── power_card_tray.py         (PowerCardTray class only)
│   └── tray_manager.py            (PowerTrayManagerClass + singleton)
│
├── card_reader/
│   ├── __init__.py                (empty)
│   ├── constants.py               (VOLTAGE_CHECK_FREQUENCY, P0..P7, etc.)
│   ├── card_reader.py             (CardReader class only)
│   └── reader_manager.py          (CardReaderManagerClass + singleton)
│
├── power_grid/
│   ├── __init__.py                (empty)
│   ├── constants.py               (GRID_REFRESH_SECONDS, grid sizes, etc.)
│   ├── power_grid.py              (PowerGrid class only)
│   ├── grid_manager.py            (PowerGridManagerClass + singleton)
│   └── random_grid_generator.py   (standalone/utility)
│
├── power_display/
│   ├── __init__.py                (empty)
│   ├── constants.py               (SHOW_POWER_DISPLAY_DIAGS, etc.)
│   ├── power_display.py           (PowerDisplay class only)
│   └── display_manager.py         (PowerDisplayManagerClass + singleton)
│
├── switchboard/
│   ├── __init__.py                (empty)
│   ├── constants.py               (SWITCHBOARD_SCAN_FREQ etc.)
│   ├── switchboard.py             (Switchboard, SwitchboardEndpoint classes)
│   └── switchboard_manager.py     (SwitchboardManagerClass + singleton)
│
├── comms/
│   ├── __init__.py                (empty)
│   ├── constants.py               (protocol constants: SER_PROTO_*, etc.)
│   └── protocol_manager.py        (ProtocolManagerClass + singleton)
│
├── host_comms/                    (existing C# project, unchanged)
└── lib/                           (CircuitPython libraries, unchanged)
```

## Key changes from original plan (per user feedback)

- `pixel_strip_manager.py` → `utils/` (was `card_tray/`)
- `dave_tm1637.py` → `utils/` (keep original name, was renamed to `tm1637_driver.py` in `power_display/`)
- `tm1637.py` → `utils/` (keep, not deleted)
- `mcp3008.py` (split from card_manager.py) → `utils/` (was `card_reader/`)
- **No files deleted** — all files are moved, none removed
- `power_display/` no longer has a TM1637 driver (it imports from `utils.dave_tm1637`)
- `card_tray/` no longer has `pixel_strip_manager.py` (it imports from `utils.pixel_strip_manager`)
- `card_reader/` no longer has `mcp3008.py` (it imports from `utils.mcp3008`)

## Steps

### Phase 1: Create directory structure

1. Create all 8 package directories with empty `__init__.py` files

### Phase 2: Split and move files (one source file at a time)

2. **eng_utils.py** → `utils/eng_utils.py` (keep as-is, just move)
3. **device_manager.py** → `utils/device_manager.py`
4. **color_utils.py** → `utils/color_utils.py`
5. **profiling.py** → `utils/profiling.py`
6. **protocol_resources.py** → `utils/protocol_resources.py`
7. **demo_data_manager.py** → `utils/demo_data_manager.py`
8. **pixel_strip_manager.py** → `utils/pixel_strip_manager.py`
9. **dave_tm1637.py** → `utils/dave_tm1637.py` (keep original name)
10. **tm1637.py** → `utils/tm1637.py` (unused backup, keep)
11. **card_manager.py** → split \_MCP3008/\_AnalogIn into `utils/mcp3008.py`, rest splits per step 18
12. **power_card_ids.py** → `power_cards/card_ids.py`
13. **power_card_animation.py** → `power_cards/animation.py`
14. **power_card_categories.py** → `power_cards/categories.py`
15. **power_card.py** → `power_cards/power_card.py`
16. **power_card_tray.py** → split into:
    - `card_tray/constants.py` (PIXEL_CARD_TRAYS, PowerStateEnum, CARD_TRAY_COLORS, etc.)
    - `card_tray/power_card_tray.py` (PowerCardTray class)
    - `card_tray/tray_manager.py` (PowerTrayManagerClass + singleton)
17. **power_grid_manager.py** → split into:
    - `power_grid/constants.py`
    - `power_grid/power_grid.py` (PowerGrid class)
    - `power_grid/grid_manager.py` (PowerGridManagerClass + singleton)
18. **card_manager.py** → split into:
    - `card_reader/constants.py`
    - `card_reader/card_reader.py` (CardReader class)
    - `card_reader/reader_manager.py` (CardReaderManagerClass + singleton)
19. **random_grid_generator.py** → `power_grid/random_grid_generator.py`
20. **power_display_manager.py** → split into:
    - `power_display/constants.py`
    - `power_display/power_display.py` (PowerDisplay class)
    - `power_display/display_manager.py` (PowerDisplayManagerClass + singleton)
21. **switchboard_manager.py** → split into:
    - `switchboard/constants.py` (if any)
    - `switchboard/switchboard.py` (Switchboard, SwitchboardEndpoint)
    - `switchboard/switchboard_manager.py` (SwitchboardManagerClass + singleton)
22. **protocol_manager.py** → split into:
    - `comms/constants.py` (SER*PROTO*\* constants)
    - `comms/protocol_manager.py` (ProtocolManagerClass + singleton)

### Phase 3: Update all imports

23. Update every import statement across all moved files to use dotted package paths
24. Fix the mis-import: power_grid imports PixelStripManager from power_card_tray → `from utils.pixel_strip_manager import PixelStripManager`
25. Update `main.py` imports to use new dotted paths
26. Update `convert_animations.py` sys.path and imports for new locations:
    - Current: `from power_card_animation import CARD_ANIMATION_DEFS, CardAnimationHelpers`
    - New: `from power_cards.animation import CARD_ANIMATION_DEFS, CardAnimationHelpers`
    - Current: `from power_card_categories import PowerCardCategories`
    - New: `from power_cards.categories import PowerCardCategories`
    - Current: `from power_card_ids import PowerCardIds`
    - New: `from power_cards.card_ids import PowerCardIds`
27. Update `device_manager.py` import of eng_utils to `utils.eng_utils`

### Phase 4: Verification (NO deletions)

28. Run ruff/pyright to check for import errors across all files
29. Verify ruff.toml doesn't need path updates
30. Verify micropython-deploy.ps1 doesn't need path updates
31. Verify all original files still exist (no deletions per user instruction)

## Decisions

- Underscore names for directories and importable files (Python requirement)
- Empty `__init__.py` files (no re-exports, minimize MicroPython import overhead)
- Shared hardware drivers (pixel_strip_manager, dave_tm1637, tm1637, mcp3008) go in utils/
- demo_data_manager goes in utils/ (shared data layer)
- protocol_resources goes in utils/ (shared by comms and demo_data)
- One class per file for all Manager classes and their component classes
- No files deleted — all files only moved/split

## Risks

- MicroPython import path: need to verify dotted package imports work on target board
- Deploy script (micropython-deploy.ps1) may need updating if it copies files by path
- convert_animations.py runs on CPython and needs sys.path + import path updates
