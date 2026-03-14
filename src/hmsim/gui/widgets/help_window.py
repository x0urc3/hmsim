#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Help Window Widget - Displays Markdown documentation."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

from hmsim.gui.utils.markdown_renderer import apply_markdown_to_buffer, set_dark_mode


class HelpWindow(Gtk.Window):
    def __init__(self, title: str = "Help"):
        super().__init__(
            title=title,
            default_width=600,
            default_height=800
        )
        self.set_resizable(True)
        self._is_dark_mode = False
        self._css_provider = Gtk.CssProvider()
        self._setup_ui()

    def set_theme(self, is_dark: bool):
        self._is_dark_mode = is_dark
        set_dark_mode(is_dark)

        bg = "#2d2d2d" if is_dark else "#fafafa"
        fg = "#e0e0e0" if is_dark else "#2c3e50"

        css_data = f"""
            textview {{ font-size: 14px; background-color: {bg}; color: {fg}; }}
            textview text {{ background-color: {bg}; color: {fg}; }}
        """.encode()
        self._css_provider.load_from_data(css_data)

        if self.text_view.get_buffer().get_char_count() > 0:
            self._reload_content()

    def _reload_content(self):
        if hasattr(self, '_last_file_path'):
            self.load_markdown(self._last_file_path)

    def _setup_ui(self):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.set_child(scrolled_window)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_top_margin(20)
        self.text_view.set_bottom_margin(20)
        self.text_view.set_left_margin(20)
        self.text_view.set_right_margin(20)

        self.text_view.get_style_context().add_provider(
            self._css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.set_theme(self._is_dark_mode)

        scrolled_window.set_child(self.text_view)

    def load_markdown(self, file_path: str) -> bool:
        self._last_file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            buffer = self.text_view.get_buffer()
            apply_markdown_to_buffer(buffer, content)
            return True
        except FileNotFoundError:
            buffer = self.text_view.get_buffer()
            buffer.set_text(f"Error: File not found\n{file_path}")
            return False
        except Exception as e:
            buffer = self.text_view.get_buffer()
            buffer.set_text(f"Error loading file: {e}")
            return False
