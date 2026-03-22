## Context

The application currently uses `Gtk.AboutDialog` to display the About dialog. GTK4's AboutDialog has limited customization options and may have compatibility issues across different GTK versions. A custom dialog gives full control over appearance and behavior.

## Goals / Non-Goals

**Goals:**
- Replace Gtk.AboutDialog with a custom dialog implementation
- Display: program name, version, comments, copyright, authors, website, license
- Maintain the same user experience (modal, centered on parent window)
- Make dialog reusable across the application

**Non-Goals:**
- Add new features beyond what's currently displayed
- Refactor other dialogs in the application

## Decisions

1. **Custom Gtk.Dialog subclass** - Use GTK4's standard Dialog class instead of AboutDialog
   - Alternative: Use Adw.AboutWindow (requires libadwaita dependency) - rejected to keep dependencies minimal
   - Rationale: GTK4 Dialog provides full flexibility while staying with core GTK4

2. **Widget placement in `src/hmsim/gui/widgets/`** - Create a new `about_dialog.py` module
   - Rationale: Follows existing project structure for reusable widgets

3. **Keep same visual information** - Display all fields currently shown in Gtk.AboutDialog
   - Rationale: No need to change user-facing content, just the implementation

## Risks / Trade-offs

- **Risk**: Re-creating dialog UI takes more code → **Mitigation**: Simple layout with labels and buttons is straightforward
- **Risk**: Missing GTK AboutDialog features → **Mitigation**: Only implement what's currently used
