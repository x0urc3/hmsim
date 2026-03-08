#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Markdown Renderer - Convert Markdown to GTK TextBuffer with rich styling."""

import sys
import os

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gdk', '4.0')
    from gi.repository import Gtk, Pango, Gdk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None


def create_text_tags(buffer: Gtk.TextBuffer) -> dict:
    """Create and return a dictionary of Gtk.TextTags for markdown styling."""
    tags = {}

    # Headings with more balanced sizes
    tags["h1"] = buffer.create_tag("h1",
                                  weight=Pango.Weight.BOLD,
                                  size=20 * Pango.SCALE,
                                  foreground="#2c3e50",
                                  pixels_above_lines=12,
                                  pixels_below_lines=6)

    tags["h2"] = buffer.create_tag("h2",
                                  weight=Pango.Weight.BOLD,
                                  size=16 * Pango.SCALE,
                                  foreground="#34495e",
                                  pixels_above_lines=10,
                                  pixels_below_lines=5)

    tags["h3"] = buffer.create_tag("h3",
                                  weight=Pango.Weight.BOLD,
                                  size=14 * Pango.SCALE,
                                  foreground="#465b6e",
                                  pixels_above_lines=8,
                                  pixels_below_lines=4)

    # Basic formatting
    tags["bold"] = buffer.create_tag("bold", weight=Pango.Weight.BOLD)
    tags["italic"] = buffer.create_tag("italic", style=Pango.Style.ITALIC)

    # Links
    tags["link"] = buffer.create_tag("link",
                                    foreground="#0066cc",
                                    underline=Pango.Underline.SINGLE)

    # Monospaced blocks with theme-adaptive background (semi-transparent grey)
    bg_rgba = Gdk.RGBA()
    bg_rgba.parse("rgba(128, 128, 128, 0.1)")

    tags["code"] = buffer.create_tag("code",
                                    family="monospace",
                                    background_rgba=bg_rgba)

    tags["codeblock"] = buffer.create_tag("codeblock",
                                         family="monospace",
                                         background_rgba=bg_rgba,
                                         left_margin=20,
                                         right_margin=20,
                                         pixels_above_lines=5,
                                         pixels_below_lines=5)

    # Table formatting
    tags["table"] = buffer.create_tag("table", family="monospace")
    tags["table_header"] = buffer.create_tag("table_header",
                                            weight=Pango.Weight.BOLD,
                                            family="monospace")

    # List formatting
    tags["list"] = buffer.create_tag("list", left_margin=20)

    # Paragraph spacing
    tags["p"] = buffer.create_tag("p", pixels_below_lines=8)

    return tags


def _get_plain_text(token) -> str:
    """Helper to extract plain text from a token and its children."""
    if not token:
        return ""
    if not token.children:
        return token.content or ""

    text = ""
    for child in token.children:
        if child.type in ("text", "code_inline"):
            text += child.content or ""
        elif child.children:
            text += _get_plain_text(child)
    return text


def _render_tokens(tokens, buffer, iter_pos, tags, tag_stack):
    """Recursively render inline tokens into the buffer."""
    if not tokens:
        return

    for token in tokens:
        if token.type == "strong_open":
            tag_stack.append(tags["bold"])
        elif token.type == "strong_close":
            if tag_stack: tag_stack.pop()
        elif token.type == "em_open":
            tag_stack.append(tags["italic"])
        elif token.type == "em_close":
            if tag_stack: tag_stack.pop()
        elif token.type == "link_open":
            tag_stack.append(tags["link"])
        elif token.type == "link_close":
            if tag_stack: tag_stack.pop()
        elif token.type == "code_inline":
            buffer.insert_with_tags(iter_pos, token.content, tags["code"], *tag_stack)
        elif token.type == "text":
            buffer.insert_with_tags(iter_pos, token.content, *tag_stack)
        elif token.type == "softbreak":
            buffer.insert(iter_pos, " ")
        elif token.type == "hardbreak":
            buffer.insert(iter_pos, "\n")
        elif token.type == "image":
            alt = ""
            if token.attrs:
                for attr in token.attrs:
                    if attr[0] == "alt":
                        alt = attr[1]
                        break
            buffer.insert(iter_pos, f"[Image: {alt}]")

        if token.children:
            _render_tokens(token.children, buffer, iter_pos, tags, tag_stack)


def render_table(rows, buffer, iter_pos, tags):
    """Render a table as aligned text with pipes and borders."""
    if not rows:
        return

    # Find max width for each column based on plain text content
    num_cols = max(len(row) for row in rows)
    col_widths = [0] * num_cols
    for row in rows:
        for i, token in enumerate(row):
            if i < num_cols:
                plain_text = _get_plain_text(token)
                col_widths[i] = max(col_widths[i], len(plain_text))

    # Add padding to widths (1 space each side)
    col_widths = [w + 2 for w in col_widths]

    def render_row(row, is_header=False):
        buffer.insert(iter_pos, "|")
        for i in range(num_cols):
            token = row[i] if i < len(row) else None
            plain_text = _get_plain_text(token) if token else ""

            # Left padding
            buffer.insert_with_tags(iter_pos, " ", tags["table_header"] if is_header else tags["table"])

            # Content with formatting
            if token and token.children:
                tag_stack = [tags["table_header"] if is_header else tags["table"]]
                _render_tokens(token.children, buffer, iter_pos, tags, tag_stack)
            elif token:
                buffer.insert_with_tags(iter_pos, token.content, tags["table_header"] if is_header else tags["table"])

            # Right padding to align columns
            padding_needed = col_widths[i] - len(plain_text) - 1
            buffer.insert_with_tags(iter_pos, " " * padding_needed, tags["table_header"] if is_header else tags["table"])
            buffer.insert(iter_pos, "|")
        buffer.insert(iter_pos, "\n")

    # Header Row
    render_row(rows[0], is_header=True)

    # Separator Row
    buffer.insert(iter_pos, "|")
    for w in col_widths:
        buffer.insert_with_tags(iter_pos, "-" * w, tags["table"])
        buffer.insert(iter_pos, "|")
    buffer.insert(iter_pos, "\n")

    # Body Rows
    for row in rows[1:]:
        render_row(row)

    buffer.insert(iter_pos, "\n")


def apply_markdown_to_buffer(buffer: Gtk.TextBuffer, markdown_text: str):
    """Parse markdown and apply styled text to the Gtk.TextBuffer."""
    if MarkdownIt is None:
        buffer.set_text(markdown_text)
        return

    # Clear existing content
    buffer.set_text("")

    # Configure MarkdownIt with table support
    md = MarkdownIt("commonmark", {"breaks": True, "html": True}).enable("table")
    tokens = md.parse(markdown_text)

    tags = create_text_tags(buffer)
    iter_pos = buffer.get_start_iter()

    tag_stack = []

    # Table state
    in_table = False
    table_rows = []
    current_row = []

    for token in tokens:
        # Table tokens handling
        if token.type == "table_open":
            in_table = True
            table_rows = []
            continue
        elif token.type == "table_close":
            render_table(table_rows, buffer, iter_pos, tags)
            in_table = False
            continue
        elif token.type == "tr_open":
            current_row = []
            continue
        elif token.type == "tr_close":
            table_rows.append(current_row)
            continue
        elif token.type in ("th_open", "td_open", "th_close", "td_close", "thead_open", "thead_close", "tbody_open", "tbody_close"):
            continue

        if in_table:
            if token.type == "inline":
                current_row.append(token)
            continue

        # Header tokens handling
        if token.type == "heading_open":
            header_tag = tags.get(token.tag)
            if header_tag:
                tag_stack.append(header_tag)
            continue
        elif token.type == "heading_close":
            if tag_stack:
                tag_stack.pop()
            buffer.insert(iter_pos, "\n")
            continue

        # List tokens handling
        if token.type == "list_item_open":
            buffer.insert(iter_pos, "  • ")
            continue
        elif token.type in ("bullet_list_close", "ordered_list_close"):
            buffer.insert(iter_pos, "\n")
            continue

        # Code block and fence handling
        if token.type in ("code_block", "fence"):
            buffer.insert_with_tags(iter_pos, token.content.strip() + "\n", tags["codeblock"])
            buffer.insert(iter_pos, "\n")
            continue

        # Paragraph tokens handling
        if token.type == "paragraph_open":
            tag_stack.append(tags["p"])
            continue
        elif token.type == "paragraph_close":
            if tag_stack: tag_stack.pop()
            buffer.insert(iter_pos, "\n")
            continue

        # Horizontal rule handling
        if token.type == "hr":
            buffer.insert(iter_pos, "─" * 40 + "\n\n")
            continue

        # Inline content rendering
        if token.type == "inline":
            _render_tokens(token.children, buffer, iter_pos, tags, tag_stack)
            continue

        # Fallback for other content
        if token.content and not in_table:
            buffer.insert_with_tags(iter_pos, token.content, *tag_stack)
