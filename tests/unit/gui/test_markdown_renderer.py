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
    assert "|" in text

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

