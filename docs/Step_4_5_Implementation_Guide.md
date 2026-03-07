# Implementation Guide: Step 4.5 - Menus, Shortcuts, and Toolbar

This document provides a technical roadmap for implementing the MenuBar, Keyboard Shortcuts, and Toolbar in the HM Simulator. This refactor moves the application from a simple HeaderBar-only interface to a more comprehensive IDE-like layout.

---

## 1. Objective
- **MenuBar:** Implement a standard `GMenu` model for File, Run, and Help.
- **Keyboard Shortcuts:** Bind standard keys (Ctrl+S, F5, etc.) to engine and file actions.
- **Toolbar:** Create a dedicated horizontal control bar below the HeaderBar for Version Selection and Simulation Controls.
- **Refactor:** Move existing logic from `main_window.py` buttons into a centralized `Gio.Action` system.

---

## 2. Technical Strategy

### 2.1 Action Mapping
Convert existing button callbacks into `Gio.SimpleAction` instances. This allows the same logic to be triggered by a Menu item, a Toolbar button, or a Keyboard shortcut.

| Action Name | Target | Shortcut | Logic |
|:--- |:--- |:--- |:--- |
| `win.new` | MainWindow | `Ctrl+N` | `self._on_new()` |
| `win.open` | MainWindow | `Ctrl+O` | `self._on_open()` |
| `win.save` | MainWindow | `Ctrl+S` | `self._on_save()` |
| `win.step` | MainWindow | `F10` | `self._on_step()` |
| `win.run` | MainWindow | `F5` | `self._on_run()` |
| `win.reset` | MainWindow | `F12` | `self._on_reset()` |
| `app.quit` | HMApplication | `Ctrl+Q` | `self.quit()` |
| `app.about` | HMApplication | `F1` | Show About Dialog |

### 2.2 UI Layout Changes
1. **HeaderBar:** Strip all buttons; keep only the window title and window controls (Close/Min/Max).
2. **MenuBar:** Enabled via `Gtk.Application.set_menubar` and `Gtk.ApplicationWindow.set_show_menubar(True)`.
3. **Toolbar:** A `Gtk.Box` added to the top of the main vertical container, styled with the `toolbar` CSS class.

---

## 3. Step-by-Step Instructions

### Step 1: Define the Menu Model (`src/hmsim/gui/hm_gui.py`)
In the `HMApplication` class, define the `GMenu` structure.

```python
def _setup_menus(self):
    menubar = Gio.Menu()

    # File Menu
    file_menu = Gio.Menu()
    file_menu.append("New", "win.new")
    file_menu.append("Open...", "win.open")
    file_menu.append("Save", "win.save")
    file_menu.append("Quit", "app.quit")
    menubar.append_submenu("File", file_menu)

    # Run Menu
    run_menu = Gio.Menu()
    run_menu.append("Run", "win.run")
    run_menu.append("Step", "win.step")
    run_menu.append("Reset", "win.reset")
    menubar.append_submenu("Run", run_menu)

    self.set_menubar(menubar)

    # Bind Accels
    self.set_accels_for_action("win.new", ["<Ctrl>n"])
    self.set_accels_for_action("win.open", ["<Ctrl>o"])
    self.set_accels_for_action("win.save", ["<Ctrl>s"])
    self.set_accels_for_action("win.run", ["F5"])
    self.set_accels_for_action("win.step", ["F10"])
    self.set_accels_for_action("app.quit", ["<Ctrl>q"])
```

### Step 2: Implement Actions and Toolbar (`src/hmsim/gui/main_window.py`)
1. **Remove buttons from `_create_header_bar`**.
2. **Create `_create_toolbar`**:
   - Use `Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)`.
   - Re-add the `version_dropdown`.
   - Add `Gtk.Button` widgets for Reset, Run, and Step.
   - **Crucial:** Use `set_action_name("win.step")` on buttons instead of `connect("clicked", ...)`.
3. **Initialize Actions**:
   ```python
   def _add_action(self, name, callback):
       action = Gio.SimpleAction.new(name, None)
       action.connect("activate", callback)
       self.add_action(action)
   ```

### Step 3: Update CSS styling
Ensure the Toolbar looks distinct. Add a simple CSS provider if needed to add padding and a subtle bottom border to the toolbar box.

---

## 4. Verification

### 4.1 Functional Check
1. **Shortcuts:** Press `Ctrl+O`; the File Open dialog should appear.
2. **Simulation:** Press `F10`; the PC should increment and memory should update.
3. **Sync:** Verify that the "Run" state is reflected in both the Menu (label might change to "Pause") and the Toolbar button.

### 4.2 UI Check
- HeaderBar should be clean (Title only).
- Toolbar should be visible above the Paned editor/state area.
- MenuBar should appear at the top of the window (standard GTK behavior).

---

## 6. Comprehensive Test Cases

The following test cases must be verified to ensure the refactor to the `Gio.Action` system is robust and that UI components are correctly synchronized.

### 6.1 Action Group Validation
- **Action Existence:** Verify that `win.has_action("save")`, `win.has_action("run")`, and `app.has_action("quit")` all return true.
- **Enabled State:**
    - Verify that `win.run` and `win.step` are disabled when an execution error is active.
    - Verify that `win.save` is disabled if the simulator state is empty/initial (optional, but good for UX).

### 6.2 Shortcut & Accelerator Verification
- **Standard Shortcuts:**
    - Trigger `Ctrl+O`: Verify the file selection dialog opens.
    - Trigger `Ctrl+S`: Verify the save dialog opens.
    - Trigger `Ctrl+N`: Verify the engine resets and the editor clears.
- **Function Keys:**
    - Trigger `F10` (Step): Verify the Program Counter (PC) increments by exactly 1 (for non-jump instructions).
    - Trigger `F5` (Run): Verify the simulator starts continuous execution.
    - Trigger `F12` (Reset): Verify all registers return to `0x0000`.

### 6.3 UI Synchronization (Crucial)
- **Label Sync:** Start the simulation (Run). Verify that the `Run` menu item in the `Run` menu and the `Run` button in the Toolbar both change their label/icon to `Pause` or `Stop`.
- **Sensitivity Sync:** Start the simulation. Verify that the `Step` and `Reset` items in the Menu and Toolbar are grayed out (insensitive) while the engine is running.
- **Global Actions:** Minimize the window. Trigger `Ctrl+Q`. The application should terminate immediately, proving the action is correctly bound to the `Gtk.Application` scope.

### 6.4 Regression Testing
- **Round-Trip Preservation:** Load a `.hm` file, modify a value, save it using `Ctrl+S`, and reload it. Ensure the changes are persisted.
- **Error State Recovery:** Trigger an "Unknown Opcode" error. Verify that the `Step` button remains disabled until `Reset` or `New` is triggered.
