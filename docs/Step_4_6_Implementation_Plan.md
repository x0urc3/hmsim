# Implementation Plan: Step 4.6 - Assembly Editor

This document outlines the implementation details for the Assembly Editor in the HM Simulator GUI.

---

## 1. Objective
- **Assembly Editor:** Provide a `Gtk.TextView` where users can write HM assembly code.
- **Real-time Assembly:** Automatically assemble the code and update the engine's memory as the user types.
- **Comment Support:** Preserve and display comments from the assembly code in the engine state.

---

## 2. Components

### 2.1 Editor Widget (`src/hmsim/gui/widgets/editor_view.py`)
- **Base Class:** `Gtk.ScrolledWindow`
- **Internal Widget:** `Gtk.TextView` with a `Gtk.TextBuffer`.
- **Styling:** Use a monospace font (e.g., "Monospace 11").
- **Features:**
  - Line numbers (optional but recommended).
  - Debounced "changed" signal handler (250-500ms delay).
  - `set_text(text_dict)`: Populates the buffer from a dictionary of address-to-instruction mapping.
  - `get_text()`: Returns the full text of the buffer.

### 2.2 Assembly Logic
- The editor will split the text into lines.
- Each line index `i` corresponds to memory address `i`.
- For each line:
  - Strip comments (text after `;`).
  - If the line is not empty, use `hmsim.tools.hmasm.assemble(line, version)` to get the machine code.
  - Update `engine._memory[i]` with the result.
  - Store the comment in `engine.comments[i]`.
- If assembly fails for a line, the error should be reported via a callback to the `MainWindow` to be shown in the status bar.

### 2.3 Integration (`src/hmsim/gui/main_window.py`)
- Replace the placeholder label in the `left_pane` with `EditorView`.
- Update `_update_ui` to sync the engine's `text` data to the editor when a file is loaded.
- Handle version changes by re-assembling the editor content with the new ISA.

---

## 3. Step-by-Step Implementation

### Step 1: Create the Editor Widget
Implement the `EditorView` class. Ensure it handles the text buffer and provides a way to notify the main window of changes.

### Step 2: Implement the Assembly Parser
Create a method in `EditorView` (or a helper) that iterates through the text buffer, assembles instructions, and updates a temporary memory buffer.

### Step 3: Integrate with MainWindow
Add the `EditorView` to the layout and connect its change signal to the engine update logic.

### Step 4: Handle File I/O
Update `_load_state` and `_save_state` to ensure the `text` section of the `.hm` file is correctly synchronized with the editor.

---

## 4. Testing Strategy

### 4.0 Regression Tests (Implement BEFORE Step 4.6)
**Purpose:** Ensure existing widget visibility and functionality is not affected by the new EditorView implementation.

#### 4.0.1 Widget Existence Tests (`tests/unit/gui/test_editor.py`)

| Test Case | Description | Expected Outcome |
|:--- |:--- |:--- |
| `test_register_view_exists` | Verify `register_view` widget still exists in main window | `register_view` attribute found |
| `test_memory_view_exists` | Verify `memory_view` widget still exists in main window | `memory_view` attribute found |
| `test_status_bar_exists` | Verify `status_bar` widget still exists in main window | `status_bar` attribute found |
| `test_toolbar_buttons_exist` | Verify toolbar buttons (btn_reset, btn_run, btn_step) still exist | All three buttons found |
| `test_left_pane_exists` | Verify `left_pane` container still exists | `left_pane` attribute found |

#### 4.0.2 Widget Visibility Tests (`tests/unit/gui/test_editor.py`)

| Test Case | Description | Expected Outcome |
|:--- |:--- |:--- |
| `test_register_view_visible` | Verify `register_view` is visible | `register_view.get_visible()` returns True |
| `test_memory_view_visible` | Verify `memory_view` is visible | `memory_view.get_visible()` returns True |
| `test_status_bar_visible` | Verify `status_bar` is visible | `status_bar.get_visible()` returns True |
| `test_buttons_visible` | Verify all toolbar buttons are visible | All buttons return True for `get_visible()` |
| `test_left_pane_visible` | Verify `left_pane` is visible | `left_pane.get_visible()` returns True |

#### 4.0.3 Layout Integrity Tests (`tests/unit/gui/test_editor.py`)

| Test Case | Description | Expected Outcome |
|:--- |:--- |:--- |
| `test_left_pane_child_count` | Verify left_pane has exactly 1 child (EditorView) | `len(list(left_pane)) == 1` |
| `test_right_pane_child_count` | Verify right_pane still has 3 children | `len(list(right_pane)) == 3` |
| `test_editor_replaces_placeholder` | Verify the placeholder label is removed | No placeholder label in left_pane |

#### 4.0.4 Functional Regression Tests (`tests/unit/gui/test_editor.py`)

| Test Case | Description | Expected Outcome |
|:--- |:--- |:--- |
| `test_registers_update_after_step` | Execute a step instruction and verify register view updates | PC increments correctly |
| `test_memory_view_displays_memory` | Verify memory view shows memory contents | TreeView populated |
| `test_status_bar_shows_message` | Trigger an error and verify status bar displays it | Error message visible |
| `test_version_dropdown_functional` | Verify version dropdown still changes engine version | Version changes correctly |

### 4.1 Editor Feature Tests (`tests/unit/gui/test_editor.py`)
Implement the following test cases using `pytest` and the `main_window` fixture:

| Test Case | Description | Expected Outcome |
|:--- |:--- |:--- |
| `test_editor_presence` | Verify `EditorView` is a child of the main window. | `EditorView` instance found. |
| `test_realtime_assembly` | Type `LOAD 0x100` into the editor. | `engine._memory[0]` becomes `0x1100`. |
| `test_multiple_lines` | Type `LOAD 0x10` and `ADD 0x20`. | `memory[0]=0x1010`, `memory[1]=0x3020`. |
| `test_comments` | Type `STORE 0x50 ; Save result`. | `engine.comments[0]` is "Save result". |
| `test_invalid_instruction` | Type `INVALID 123`. | Status bar shows error; memory at that address remains unchanged or zeroed. |
| `test_version_switch` | Change version from HMv1 to HMv2 with `SUB` instruction. | Assembly succeeds if `SUB` is valid in HMv2. |
| `test_file_load` | Load a `.hm` file with assembly. | `EditorView` buffer matches the file's `text` section. |

### 4.2 Manual Verification
1. Launch the GUI.
2. Type a simple program (e.g., `LOAD 10`, `ADD 11`, `OUT 0`).
3. Observe the Memory View updating in real-time.
4. Click "Step" and verify the AC updates as expected.
5. Save the file and verify the `.hm` JSON contains the `text` section.
