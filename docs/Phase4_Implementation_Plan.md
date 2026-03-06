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

## Step 4.x: File I/O (JSON State)

### Actions
1. Add File menu to HeaderBar with: New, Open, Save
2. Create `src/hmsim/gui/widgets/file_dialog.py`:
   - `save_dialog(parent_window)` - Returns file path or None
   - `open_dialog(parent_window)` - Returns file path or None
3. Implement JSON state format:
   ```json
   {
     "version": "HMv1",
     "pc": 0,
     "ac": 0,
     "ir": 0,
     "sr": 0,
     "memory": [0, 0, 1234, 0, ...]  // 65536 values
   }
   ```
4. Add save functionality in main_window.py:
   - Serialize engine state to JSON
   - Write to file
5. Add load functionality in main_window.py:
   - Read JSON file, validate, load into engine
   - Update UI after load

### Verification
```bash
# Create sample.json with test program
# Launch GUI: python3 src/hmsim/gui/hm_gui.py
# File > Open > select sample.json
# Verify memory grid shows instructions
# Click Step, observe register updates
# File > Save > save to new file
# Verify saved JSON contains correct state
```

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

## Step 4.6: Continuous Execution & File I/O

### Actions
1. Add execution controls to HeaderBar:
   - **Run/Pause Toggle:** Use `GLib.timeout_add` for continuous `step()` execution
   - **Speed Slider:** 1Hz to 100Hz frequency control
2. Implement File Operations:
   - **New:** Clear memory and registers
   - **Open:** Use `Gtk.FileDialog` to load `.bin` files into memory
   - **Save:** Export memory to `.bin` file
3. Add Assembly file support:
   - Parse `.asm` files using `hmasm` logic
   - Save editor content to `.asm`

### Verification
- Load a sample `.bin` file
- Click "Run" at 10Hz
- **Expected:** PC advances automatically through memory
- Click "Pause" - execution stops
- Save file, reopen - content preserved

---

## File Structure After Phase 4

```text
src/hmsim/gui/
├── __init__.py
├── hm_gui.py              # Entry point
├── main_window.py         # Main window + HeaderBar
└── widgets/
    ├── __init__.py
    ├── register_view.py  # PC, AC, IR, SR display
    ├── memory_view.py    # Scrollable memory grid
    └── editor_view.py    # Dual-mode editor
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
