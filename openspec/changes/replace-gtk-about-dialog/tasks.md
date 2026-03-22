## 1. Create custom AboutDialog widget

- [x] 1.1 Create `src/hmsim/gui/widgets/about_dialog.py` with AboutDialog class extending Gtk.Dialog
- [x] 1.2 Implement UI layout with labels for program name, version, comments, copyright, authors, website, license
- [x] 1.3 Add Close button that closes the dialog

## 2. Update main GUI to use custom dialog

- [x] 2.1 Import the new AboutDialog in `hm_gui.py`
- [x] 2.2 Replace Gtk.AboutDialog usage in `_on_about` method with custom AboutDialog
- [x] 2.3 Ensure dialog is modal and centered on parent window

## 3. Verify and test

- [x] 3.1 Run the application and verify About dialog works correctly
- [x] 3.2 Run existing tests to ensure no regressions
