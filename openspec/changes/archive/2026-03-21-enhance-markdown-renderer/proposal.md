## Why

The Help Window markdown renderer displays user documentation (User Guide, Tutorial) in the HM Simulator GUI. Currently, it has basic styling for headings and paragraphs, but lacks visual polish for horizontal rules, code blocks, and tables. The rendered documentation looks plain and doesn't leverage GTK's styling capabilities to create a more readable, professional appearance.

## What Changes

- **Horizontal Rules**: Replace plain `---` with decorative Unicode dividers (━, ═, ◆) for visual separation between sections
- **Code Blocks**: Add styled backgrounds with rounded corners, improved monospace font rendering, and optional line numbers
- **Tables**: Add Unicode box-drawing characters (┌─┬┐│└┘├┼┤) for proper table borders, header row differentiation, and alternating row styling

## Capabilities

### New Capabilities
- `enhanced-markdown-styling`: Enhanced visual rendering of horizontal rules, code blocks, and tables in the Help Window markdown display

### Modified Capabilities
- None - this is purely a visual enhancement to existing rendering

## Impact

- **Modified**: `src/hmsim/gui/utils/markdown_renderer.py`
- **No new dependencies**: Uses existing Pango/Gtk styling capabilities
- **No breaking changes**: Source markdown files remain unchanged, renderer falls back gracefully if markdown_it is unavailable
