# Phase 4 Implementation Plan: GTK 4 Graphical Interface

This document outlines the step-by-step implementation plan for Phase 4 of the HM-Series Integrated Development Suite.

---

## Overview

**Objective:** Provide a visual debugger for real-time architectural exploration with verifiable milestones at each step.

**Approach:** "UI-First, Logic-Second" - Build and verify the visual skeleton before connecting complex engine logic.

---

## Step 4.1: Foundation & Header Bar

### Actions
1. Create `src/hmsim/gui/__init__.py` - Package init with optional GTK check
2. Create `src/hmsim/gui/hm_gui.py` - Main application entry point
   - Initialize `Gtk.Application` with app ID `com.hmsim.app`
   - Create main window with `Gtk.ApplicationWindow`
3. Create `src/hmsim/gui/main_window.py` - Main window container
   - Setup `Gtk.HeaderBar` with title "HM Simulator"
   - Add Version Selector (`Gtk.DropDown`) for HMv1/HMv2
   - Add basic menu (About, Quit)

### Verification
```bash
pip install -e ".[gui]"
python3 src/hmsim/gui/hm_gui.py
```
**Expected:** Window appears with HeaderBar and functional version dropdown.

---

## Step 4.2: Register & Status Panel

### Actions
1. Create `src/hmsim/gui/widgets/__init__.py` - Widgets package init
2. Create `src/hmsim/gui/widgets/register_view.py` - `Gtk.Box` containing:
   - Labels for PC, AC, IR, SR (16-bit registers)
   - Monospace font for hex values
   - Update method to refresh values from engine

### Verification
- Launch GUI
- Observe register panel on the right side
- Default values should show `0x0000`

---

## Step 4.3: Memory Visualization Grid

### Actions
1. Create `src/hmsim/gui/widgets/memory_view.py`
   - Use `Gtk.ColumnView` with columns: Address (Hex), Value (Hex), Mnemonic
   - Implement virtual scrolling for 65536 rows (lazy loading)
   - Add "Go to Address" entry field

### Verification
- Launch GUI
- Scroll through memory grid
- All rows show `0x0000` initially

---

## Step 4.4: Engine Integration & Step Control

### Actions
1. Update `src/hmsim/engine/cpu.py`:
   - Add `observers: List[Callable]` to `HMEngine.__init__`
   - Add `register_observer(callback)` method
   - Create `_notify_observers()` called after `step()`, `execute()`, and memory writes
2. Update `src/hmsim/gui/main_window.py`:
   - Instantiate `HMEngine(version)` in MainWindow
   - Connect HeaderBar buttons to engine actions:
     - **Step:** Call `engine.step()`, refresh UI
     - **Reset:** Re-initialize engine, refresh UI

### Verification
```python
# Hardcode test in main_window.py:
engine._memory[0] = 0x1100  # LOAD 0x000
engine._memory[1] = 0x0005  # Data: 5
```
- Launch GUI
- Click "Step"
- **Expected:** AC changes to `0x0005`, PC changes to `0x0002`

---

## Step 4.x: File I/O (JSON State) - COMPLETED

### Actions
1. Add File menu to HeaderBar with: New, Open, Save buttons
2. Create `src/hmsim/gui/widgets/file_dialog.py`:
   - GTK4 FileDialog utilities
3. Implement sparse JSON state format (only non-zero memory):
   ```json
   {
     "version": "HMv1",
     "pc": 0,
     "ac": 0,
     "ir": 0,
     "sr": 0,
     "memory": {
       "0": 4352,
       "256": 5
     }
   }
   ```
4. Add save functionality:
   - Serialize engine state to JSON
   - Only store non-zero memory values
5. Add load functionality:
   - Read JSON file, validate version
   - Update UI after load
   - Show "Loaded HMv1 state" or "Warning: HMv3 state loaded as HMv2" in status bar

### Verification
```bash
python3 src/hmsim/gui/hm_gui.py
# File > Open > tests/fixtures/sample_state.json
# Verify memory shows instructions at addresses 0 and 256
# Click Step - AC changes to 5, PC changes to 1
# File > Save > save.json
# Verify JSON contains only non-zero memory entries
```

---

## Step 4.x: Error Handling - COMPLETED

### Actions
1. Add status bar to main window (below memory grid)
2. Update `_on_step()` to catch exceptions:
   - Show error message in status bar: "Error at 0x<addr>: <message>"
   - Highlight error address in memory grid
3. Clear errors on: Step, Reset, New, Open, Save

### Verification
- Launch GUI with empty memory
- Click Step - error message appears, address 0 highlighted in memory
- Click Reset - error clears, "Ready" shown in status bar

---

## Step 4.x: Version Switch Preserves State - COMPLETED

### Actions
1. Update `_on_version_changed()` to:
   - Save current engine state (memory, PC, AC, IR, SR)
   - Create new engine with different version
   - Restore saved state to new engine

### Verification
- Open a JSON file with instructions
- Switch version dropdown from HMv1 to HMv2
- Verify memory and registers remain unchanged

---

## Step 4.5: Dual-Mode Editor (Assembly & Hex)

### Actions
1. Create `src/hmsim/gui/widgets/editor_view.py`
   - `Gtk.Notebook` with two tabs:
     - **Assembly Tab:** `Gtk.TextView` for mnemonics
     - **Machine Code Tab:** `Gtk.TextView` for hex values
2. Implement sync logic:
   - **ASM → HEX:** On text change, parse each line, use `hmsim.tools.hmasm.assemble()`, update hex view
   - **HEX → ASM:** On text change, parse hex, use `hmsim.tools.hmdas.disassemble()`, update asm view
3. Link editor changes to memory:
   - Changes in ASM/HEX view update engine memory at corresponding addresses

### Verification
- Type `LOAD 0x100` in ASM pane
- **Expected:** HEX pane shows `0x1100`, Memory Grid reflects change at address 0x0000

---

## Step 4.6: Continuous Execution & File I/O - COMPLETED

### Actions
1. Add execution controls to HeaderBar:
   - **Run/Pause Toggle:** Uses `GLib.idle_add` for continuous execution with batch processing
   - **Batch Size:** 1000 instructions per GUI tick for high-speed simulation (~60K instructions/sec)
   - Implements `total_cycles` counter for accurate cycle statistics
2. Implement File Operations:
   - **New:** Clear memory and registers
   - **Open:** Use `Gtk.FileDialog` to load `.json` state files into memory
   - **Save:** Export memory to `.json` file (sparse format)

### Verification
- Load a sample `.json` file
- Click "Run"
- **Expected:** PC advances automatically, Cycles counter increments rapidly
- Click "Stop" - execution pauses
- Save file, reopen - content preserved

---

## File Structure After Phase 4

```text
src/hmsim/gui/
├── __init__.py
├── hm_gui.py              # Entry point
├── main_window.py         # Main window + HeaderBar + file I/O
└── widgets/
    ├── __init__.py
    ├── register_view.py  # PC, AC, IR, SR display
    ├── memory_view.py    # Scrollable memory grid + highlighting
    ├── file_dialog.py    # File dialog utilities
    └── editor_view.py    # (Future) Dual-mode editor
```

---

## Dependencies

- `PyGObject>=3.44`
- `hmsim.engine` (no GUI deps)
- `hmsim.tools.hmasm` (for assembly)
- `hmsim.tools.hmdas` (for disassembly)

---

## Testing Strategy

1. **Manual UI Testing:** Each step includes manual verification commands
2. **Regression Testing:** Existing `pytest` tests must continue to pass
3. **Integration Testing:** Future tests in `tests/integration/` will verify GUI/Engine interaction
