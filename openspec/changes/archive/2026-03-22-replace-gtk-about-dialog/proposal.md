## Why

The GTK4 AboutDialog has compatibility issues and limited customization. Replacing it with a custom dialog gives more control over the UI and avoids potential GTK-specific quirks.

## What Changes

- Replace `Gtk.AboutDialog` usage in `hm_gui.py` with a custom dialog implementation
- Create a reusable `AboutDialog` class in the GUI widgets module
- Include similar information: program name, version, comments, copyright, authors, website, license

## Capabilities

### New Capabilities
- `about-dialog`: A custom about dialog implementation that displays application information without relying on GTK's built-in AboutDialog

### Modified Capabilities
- (none)

## Impact

- Code: `src/hmsim/gui/hm_gui.py` - replace AboutDialog usage
- New file: `src/hmsim/gui/widgets/about_dialog.py` - custom dialog implementation
