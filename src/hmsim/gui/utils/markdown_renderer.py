#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Markdown Renderer - Convert Markdown to GTK TextBuffer with rich styling."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Pango
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None


def create_text_tags(buffer: Gtk.TextBuffer) -> dict:
    tags = {}

    tag = buffer.create_tag("h1", weight=Pango.Weight.BOLD, size=24 * 1024)
    tags["h1"] = tag

    tag = buffer.create_tag("h2", weight=Pango.Weight.BOLD, size=18 * 1024)
    tags["h2"] = tag

    tag = buffer.create_tag("h3", weight=Pango.Weight.BOLD, size=14 * 1024)
    tags["h3"] = tag

    tag = buffer.create_tag("bold", weight=Pango.Weight.BOLD)
    tags["bold"] = tag

    tag = buffer.create_tag("italic", style=Pango.Style.ITALIC)
    tags["italic"] = tag

    tag = buffer.create_tag("code", family="monospace", background="#f0f0f0")
    tags["code"] = tag

    tag = buffer.create_tag("codeblock", family="monospace", background="#f5f5f5", left_margin=20, right_margin=20)
    tags["codeblock"] = tag

    tag = buffer.create_tag("link", foreground="#0066cc", underline=Pango.Underline.SINGLE)
    tags["link"] = tag

    tag = buffer.create_tag("list", left_margin=20)
    tags["list"] = tag

    return tags


def apply_markdown_to_buffer(buffer: Gtk.TextBuffer, markdown_text: str):
    if MarkdownIt is None:
        buffer.set_text(markdown_text)
        return

    md = MarkdownIt()
    tokens = md.parse(markdown_text)

    tags = create_text_tags(buffer)

    iter_pos = buffer.get_start_iter()

    for token in tokens:
        if token.type == "heading_open":
            continue
        elif token.type == "heading_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "h1":
            buffer.insert_with_tags(iter_pos, token.content + "\n", tags["h1"])
        elif token.type == "h2":
            buffer.insert_with_tags(iter_pos, token.content + "\n", tags["h2"])
        elif token.type == "h3":
            buffer.insert_with_tags(iter_pos, token.content + "\n", tags["h3"])
        elif token.type == "inline":
            _process_inline(token.content, buffer, iter_pos, tags)
        elif token.type == "code_block":
            buffer.insert_with_tags(iter_pos, token.content + "\n", tags["codeblock"])
        elif token.type == " fence":
            buffer.insert_with_tags(iter_pos, token.content + "\n", tags["codeblock"])
        elif token.type == "bullet_list_open":
            pass
        elif token.type == "bullet_list_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "ordered_list_open":
            pass
        elif token.type == "ordered_list_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "list_item_open":
            buffer.insert(iter_pos, "  • ")
        elif token.type == "list_item_close":
            pass
        elif token.type == "paragraph_open":
            pass
        elif token.type == "paragraph_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "hr":
            buffer.insert(iter_pos, "─" * 40 + "\n")
        elif token.type == "table_open":
            pass
        elif token.type == "table_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "thead_open":
            pass
        elif token.type == "thead_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "tbody_open":
            pass
        elif token.type == "tbody_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "tr_open":
            pass
        elif token.type == "tr_close":
            buffer.insert(iter_pos, "\n")
        elif token.type == "th_open":
            pass
        elif token.type == "th_close":
            buffer.insert(iter_pos, " | ")
        elif token.type == "td_open":
            pass
        elif token.type == "td_close":
            buffer.insert(iter_pos, " | ")
        elif token.type == "softbreak":
            buffer.insert(iter_pos, " ")
        elif token.type == "br":
            buffer.insert(iter_pos, "\n")
        elif token.type == "strong_open":
            pass
        elif token.type == "strong_close":
            pass
        elif token.type == "em_open":
            pass
        elif token.type == "em_close":
            pass
        elif token.type == "link_open":
            pass
        elif token.type == "link_close":
            pass
        elif token.type == "code_inline":
            buffer.insert_with_tags(iter_pos, token.content, tags["code"])
        elif token.type == "image":
            buffer.insert(iter_pos, f"[Image: {token.get('alt', '')}]")
        else:
            if token.content:
                buffer.insert(iter_pos, token.content)


def _process_inline(content: str, buffer: Gtk.TextBuffer, iter_pos: Gtk.TextIter, tags: dict):
    import re

    patterns = [
        (r'\*\*(.+?)\*\*', 'bold'),
        (r'\*(.+?)\*', 'italic'),
        (r'`([^`]+)`', 'code'),
    ]

    pos = 0
    while pos < len(content):
        earliest_match = None
        earliest_tag = None
        earliest_start = len(content)

        for pattern, tag_name in patterns:
            match = re.search(pattern, content[pos:])
            if match and match.start() < earliest_start:
                earliest_match = match
                earliest_tag = tags.get(tag_name)
                earliest_start = match.start()

        if earliest_match:
            if earliest_match.start() > 0:
                buffer.insert(iter_pos, content[pos:pos + earliest_match.start()])

            buffer.insert_with_tags(iter_pos, earliest_match.group(1), earliest_tag)
            pos = pos + earliest_match.end()
        else:
            buffer.insert(iter_pos, content[pos:])
            break
