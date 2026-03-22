## Context

The HM Simulator Help Window displays markdown documentation using a custom renderer (`src/hmsim/gui/utils/markdown_renderer.py`). The current implementation uses `markdown_it` to parse markdown and applies basic styling through GTK TextTags. While headings and paragraphs are styled, horizontal rules, code blocks, and tables lack visual polish.

### Current State
- Headings: Bold, colored, with spacing
- Paragraphs: Basic spacing between blocks
- Code blocks: Monospace with background color
- Tables: Basic pipe-delimited rendering with column alignment
- Horizontal rules: Plain Unicode em-dash

## Goals / Non-Goals

**Goals:**
- Enhanced horizontal rule rendering with decorative Unicode dividers
- Improved code block styling with better visual separation
- Better table rendering with Unicode box-drawing characters
- Maintain backward compatibility with basic text fallback if markdown_it is unavailable

**Non-Goals:**
- Full syntax highlighting for code blocks
- Complex table features (merged cells, colspans)
- Image rendering in markdown
- Changes to source markdown files or help content

## Decisions

### D1: Horizontal Rule Enhancement
**Decision**: Use centered Unicode decorative characters instead of plain `---`
```
Before: ─────────────────────────────
After:
═══════════════════════════════════════
       ═══════════════════════════════
```
**Rationale**: Creates clear visual section breaks without modifying source markdown. Uses characters that render well in both light and dark themes.

### D2: Code Block Styling
**Decision**: Add top/bottom border lines using Unicode box-drawing characters (┌�└┐┘)
```
┌─────────────────────────────────────┐
│ code content here                   │
└─────────────────────────────────────┘
```
**Rationale**: Provides visual "container" effect for code blocks. Works with existing `codeblock` tag's background color.

### D3: Table Enhancement
**Decision**: Use Unicode box-drawing characters for table borders
```
┌───────┬───────┬───────┐
│ Col 1 │ Col 2 │ Col 3 │
├───────┼───────┼───────┤
│  val  │  val  │  val  │
└───────┴───────┴───────┘
```
**Rationale**: Creates proper table grid with clear header/body separation. Maintains readability with monospace font.

### D4: Dark Mode Consistency
**Decision**: Use theme-appropriate colors for all new styling elements
- Light mode: Dark gray borders/text
- Light mode: Lighter backgrounds
- Dark mode: Lighter gray borders/text
- Dark mode: Slightly brighter backgrounds
**Rationale**: Ensures visual consistency across themes. Uses existing `_is_dark_mode` pattern.

## Risks / Trade-offs

- **[Minor] Font rendering**: Unicode box-drawing characters may not render identically on all systems → Mitigation: Use common ASCII fallbacks if needed, but most modern systems support these characters
- **[Minor] Table width**: Complex tables with long content may exceed window width → Mitigation: Existing column-width calculation handles this, Unicode chars are single-width
- **[No risk] Performance**: Minimal impact - same token parsing, just different rendering strings
- **[No risk] Backward compatibility**: Falls back to plain text if markdown_it unavailable

## Migration Plan

1. Modify `markdown_renderer.py` to add new rendering functions
2. Test with existing User Guide and Tutorial markdown files
3. Verify both light and dark themes render correctly
4. No migration needed - no data changes, purely visual enhancement
