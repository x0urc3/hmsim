# Phase 4 Implementation Plan: GTK 4 Graphical Interface

This document outlines the step-by-step implementation plan for Phase 4 of the HM-Series Integrated Development Suite.

---

## Overview

**Objective:** Provide a visual debugger for real-time architectural exploration with verifiable milestones at each step.

**Approach:** "UI-First, Logic-Second" - Build and verify the visual skeleton before connecting complex engine logic.

---

## Step 4.1: Foundation & Header Bar - COMPLETED

### Actions
1. Create `src/hmsim/gui/__init__.py` - Package init with optional GTK check
2. Create `src/hmsim/gui/hm_gui.py` - Main application entry point
   - Initialize `Gtk.Application` with app ID `com.hmsim.app`
   - Create main window with `Gtk.ApplicationWindow`
3. Create `src/hmsim/gui/main_window.py` - Main window container
   - Setup `Gtk.HeaderBar` with title "HM Simulator"
   - HeaderBar will primarily act as the title bar, as controls will move to Toolbar/Menus.

### Verification
```bash
pip install -e ".[gui]"
python3 src/hmsim/gui/hm_gui.py
```
**Expected:** Window appears with HeaderBar title.

---

## Step 4.2: Register & Status Panel - COMPLETED

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

## Step 4.3: Memory Visualization Grid - COMPLETED

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

## Step 4.4: Engine Integration & State Metadata - COMPLETED

### Actions
1. Update `src/hmsim/engine/cpu.py`:
   - Add `observers: List[Callable]` to `HMEngine.__init__`
   - Add `register_observer(callback)` method
   - Add `comments: Dict[int, str]` for storing inline comments from `.hm` files
   - Create `_notify_observers()` called after `step()`, `execute()`, and memory writes
2. Update `src/hmsim/gui/main_window.py`:
   - Instantiate `HMEngine(version)` in MainWindow

### Verification
- Launch GUI
- No crashes; engine initializes with default version (HMv1).

---

## Step 4.5: Menus, Keyboard Shortcuts, and Toolbar

### Actions
1. Implement MenuBar using `GMenu` model in `src/hmsim/gui/hm_gui.py`:
   - **File:** New, Open (Ctrl+O), Save (Ctrl+S), Quit (Ctrl+Q)
   - **Run:** Reset, Step (F10), Run (F5)
   - **Help:** About
2. Add a `Gtk.Box` (Toolbar) below the HeaderBar:
   - **Version Selector:** `Gtk.DropDown` for HMv1/HMv2
   - **Execution Controls:** Reset, Step, Run buttons with icons.
3. Use `Gtk.ShortcutController` to map keyboard shortcuts to application actions.

### Verification
- Launch GUI
- Verify MenuBar is functional and keyboard shortcuts (e.g., Ctrl+Q) work.
- Toolbar buttons should be visible and clickable.

---

## Step 4.6: Assembly Editor

### Actions
1. Create `src/hmsim/gui/widgets/editor_view.py`:
   - Single-pane `Gtk.TextView` for assembly mnemonics and comments.
   - Integration with `engine.text` from `.hm` files.
2. Implement parsing logic:
   - When text in the editor changes, attempt to assemble each line using `hmsim.tools.hmasm.assemble()`.
   - Update `engine._memory` and `engine.comments` in real-time (with a slight debounce).

### Verification
- Type `LOAD 0x100 ; initialize` in the editor.
- **Expected:** Memory grid updates at 0x0000 with the correct machine code, and the comment is stored.

---

## Step 4.x: File I/O (.hm State) - COMPLETED

### Actions
1. Create `src/hmsim/gui/widgets/file_dialog.py`:
   - GTK4 FileDialog utilities configured for `.hm` files.
2. Implement structured `.hm` format (Linear Disassembly heuristic):
   ```json
   {
     "version": "HMv1",
     "pc": 0,
     "ac": 0,
     "text": {
       "0x0000": "LOAD 0x00A ; Fetch operand",
       "0x0001": "ADD 0x00B"
     },
     "data": {
       "0x000A": "0x0005"
     }
   }
   ```
3. Add save functionality:
   - Serialize engine state to `.hm` dictionary using heuristic.
4. Add load functionality:
   - Read `.hm` file, re-assemble `text` section, and parse `data` section.
   - Show "Loaded HMv1 state" or "Warning: HMv3 state loaded as HMv2" in status bar.

### Verification
- File > Open > `examples/add_two_numbers.hm`
- Verify assembly text appears in the editor and machine code in memory.
- Click Step - AC updates correctly.

---

## Step 4.7: Continuous Execution & Error Handling - COMPLETED

### Actions
1. Implementation of `Run` logic:
   - **Run/Pause Toggle:** Uses `GLib.timeout_add` or `GLib.idle_add` for continuous execution.
   - **Batch Size:** 1000 instructions per GUI tick for high-speed simulation.
2. Status bar & Error Handling:
   - Catch `ValueError` or `KeyboardInterrupt` during execution.
   - Show error message in status bar and highlight error address in memory grid.

### Verification
- Launch GUI, click "Run".
- Cycles counter increments rapidly.
- Errors (e.g., unknown opcode) appear in status bar.

---

## File Structure After Phase 4

```text
src/hmsim/gui/
├── __init__.py
├── hm_gui.py              # App entry + MenuBar definition
├── main_window.py         # Main window + HeaderBar + Toolbar + status bar
└── widgets/
    ├── __init__.py
    ├── register_view.py  # PC, AC, IR, SR display
    ├── memory_view.py    # Scrollable memory grid + highlighting
    ├── file_dialog.py    # .hm File dialog utilities
    └── editor_view.py    # Assembly editor
```

---

## Dependencies

- `PyGObject>=3.44`
- `hmsim.engine` (no GUI deps)
- `hmsim.tools.hmasm` (for assembly)
- `hmsim.tools.hmdas` (for disassembly)

---

## Testing Strategy

1. **Manual UI Testing:** Verify shortcuts and toolbar interaction.
2. **Regression Testing:** Existing `pytest` tests must pass.
3. **Round-trip Test:** Open `.hm` → edit assembly → save → reopen and verify state.
