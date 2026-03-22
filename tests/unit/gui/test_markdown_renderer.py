import pytest
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango
from hmsim.gui.utils.markdown_renderer import apply_markdown_to_buffer

def test_markdown_headers():
    buffer = Gtk.TextBuffer()
    markdown = "# Header 1\n## Header 2"
    apply_markdown_to_buffer(buffer, markdown)

    # Check if tags were applied
    # Note: Gtk.TextBuffer.get_text() returns plain text.
    # To check tags, we need to iterate over the buffer.

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Header 1" in text
    assert "Header 2" in text

    # Verify tags at specific positions
    it = buffer.get_start_iter()
    # Skip potential leading whitespace/newlines if any
    while it.get_char() == '\n' and not it.is_end():
        it.forward_char()

    tags = it.get_tags()
    tag_names = [t.get_property("name") for t in tags]
    assert "h1" in tag_names

def test_markdown_table():
    buffer = Gtk.TextBuffer()
    markdown = "| Col 1 | Col 2 |\n|---|---|\n| Val 1 | Val 2 |"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Col 1" in text
    assert "Col 2" in text
    assert "Val 1" in text
    assert "│" in text
    assert "┌" in text
    assert "└" in text

    # Tables should be in monospace
    it = buffer.get_start_iter()
    while it.get_char() != 'C' and not it.is_end():
        it.forward_char()

    tags = it.get_tags()
    tag_names = [t.get_property("name") for t in tags]
    assert "table_header" in tag_names or "table" in tag_names

def test_markdown_bold_italic():
    buffer = Gtk.TextBuffer()
    markdown = "**Bold** and *Italic*"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Bold" in text
    assert "Italic" in text

    it = buffer.get_start_iter()
    while it.get_char() != 'B' and not it.is_end():
        it.forward_char()

    tags = it.get_tags()
    tag_names = [t.get_property("name") for t in tags]
    assert "bold" in tag_names

    while it.get_char() != 'I' and not it.is_end():
        it.forward_char()

    tags = it.get_tags()
    tag_names = [t.get_property("name") for t in tags]
    assert "italic" in tag_names


def test_markdown_horizontal_rule():
    buffer = Gtk.TextBuffer()
    markdown = "Text before\n\n---\n\nText after"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Text before" in text
    assert "Text after" in text
    assert "═" in text


def test_markdown_code_block():
    buffer = Gtk.TextBuffer()
    markdown = """```
LOAD 10
ADD 11
```"""
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "LOAD 10" in text
    assert "ADD 11" in text
    assert "┌" in text
    assert "└" in text
    assert "│" in text


def test_markdown_code_block_single_line():
    buffer = Gtk.TextBuffer()
    markdown = "```python\nprint('hello')\n```"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "print('hello')" in text
    assert "┌" in text
    assert "└" in text


def test_markdown_table_single_column():
    buffer = Gtk.TextBuffer()
    markdown = "| Col |\n|---|\n| A |\n| B |"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Col" in text
    assert "A" in text
    assert "B" in text
    assert "┌" in text
    assert "┬" in text
    assert "└" in text
    assert "┘" in text


def test_markdown_table_long_content():
    buffer = Gtk.TextBuffer()
    markdown = "| Short | Very Long Content |\n|---|---|\n| A | This is a much longer text that should still render properly |"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Short" in text
    assert "Very Long Content" in text
    assert "A" in text
    assert "This is a much longer text" in text
    assert "│" in text


def test_markdown_table_empty_cell():
    buffer = Gtk.TextBuffer()
    markdown = "| A | B |\n|---|---|\n| Only A | |"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "A" in text
    assert "B" in text
    assert "Only A" in text
    assert "│" in text


def test_markdown_list_bullet():
    buffer = Gtk.TextBuffer()
    markdown = "- Item 1\n- Item 2\n- Item 3"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Item 1" in text
    assert "Item 2" in text
    assert "Item 3" in text
    assert "•" in text


def test_markdown_list_ordered():
    buffer = Gtk.TextBuffer()
    markdown = "1. First\n2. Second\n3. Third"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "First" in text
    assert "Second" in text
    assert "Third" in text


def test_markdown_inline_code():
    buffer = Gtk.TextBuffer()
    markdown = "Use `LOAD 10` to load data"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Use" in text
    assert "LOAD 10" in text
    assert "to load data" in text

    it = buffer.get_start_iter()
    while it.get_char() != 'L' and not it.is_end():
        it.forward_char()

    tags = it.get_tags()
    tag_names = [t.get_property("name") for t in tags]
    assert "code" in tag_names


def test_markdown_link():
    buffer = Gtk.TextBuffer()
    markdown = "[HM Simulator](https://example.com)"
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "HM Simulator" in text


def test_markdown_empty():
    buffer = Gtk.TextBuffer()
    apply_markdown_to_buffer(buffer, "")

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert text == ""


def test_markdown_mixed_content():
    buffer = Gtk.TextBuffer()
    markdown = """# Title

Some text with **bold** and *italic*.

- List item 1
- List item 2

```
code block
```

| A | B |
|---|---|
| 1 | 2 |

---

End text."""
    apply_markdown_to_buffer(buffer, markdown)

    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    assert "Title" in text
    assert "bold" in text
    assert "italic" in text
    assert "List item 1" in text
    assert "code block" in text
    assert "A" in text
    assert "B" in text
    assert "1" in text
    assert "2" in text
    assert "End text" in text
    assert "═" in text

