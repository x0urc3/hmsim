#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Assembly Editor Widget for HM Simulator."""

import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, GLib
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

from hmsim.tools.hmasm import assemble


class EditorView(Gtk.ScrolledWindow):
    DEBOUNCE_DELAY = 300

    def __init__(self, version: str = "HMv1"):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self._version = version
        self._change_callback = None
        self._debounce_source_id = None
        self._max_addr_touched = -1

        self._text_view = Gtk.TextView()
        self._text_view.set_monospace(True)
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text_view.set_editable(True)
        self._text_view.set_cursor_visible(True)
        self._text_view.set_accepts_tab(True)
        self._text_view.set_indent(0)
        self._text_view.set_left_margin(5)
        self._text_view.set_right_margin(5)

        self._buffer = self._text_view.get_buffer()
        self._buffer.connect("changed", self._on_text_changed)

        self.set_child(self._text_view)

    def set_change_callback(self, callback):
        self._change_callback = callback

    def set_version(self, version: str):
        self._version = version

    def _on_text_changed(self, buffer):
        if self._debounce_source_id is not None:
            GLib.source_remove(self._debounce_source_id)

        self._debounce_source_id = GLib.timeout_add(
            self.DEBOUNCE_DELAY,
            self._emit_change_signal
        )

    def _emit_change_signal(self):
        self._debounce_source_id = None
        if self._change_callback:
            text = self.get_text()
            self._change_callback(text)
        return False

    def set_text(self, text: str):
        self._buffer.set_text(text)
        self._max_addr_touched = max(self._max_addr_touched, len(text.split('\n')) - 1)

    def get_text(self) -> str:
        return self._buffer.get_text(
            self._buffer.get_start_iter(),
            self._buffer.get_end_iter(),
            True
        )

    def get_text_dict(self) -> dict:
        text = self.get_text()
        lines = text.split('\n')
        result = {}
        for i, line in enumerate(lines):
            if line.strip():
                result[i] = line
        return result

    def parse_and_assemble(self, version: str = None):
        if version is None:
            version = self._version
        text = self.get_text()
        lines = text.split('\n')
        memory = {}
        comments = {}
        errors = []

        for i, line in enumerate(lines):
            original_line = line
            code_part = line.split(';', 1)[0].strip()

            if code_part:
                if ';' in original_line:
                    comments[i] = original_line.split(';', 1)[1].strip()

                try:
                    machine_code = assemble(code_part, version)
                    memory[i] = machine_code
                except (ValueError, KeyError) as e:
                    errors.append((i, str(e)))
                    memory[i] = 0
            else:
                # Explicitly set empty line to machine code 0
                memory[i] = 0
                if ';' in original_line:
                    comments[i] = original_line.split(';', 1)[1].strip()

        return memory, comments, errors

    def assemble_to_engine(self, engine):
        memory, comments, errors = self.parse_and_assemble(engine.version)

        # Track which addresses we are updating to handle deletions
        num_lines = len(memory)

        # If the program got shorter, clear the tail from previously touched range
        if num_lines < self._max_addr_touched + 1:
            for addr in range(num_lines, self._max_addr_touched + 1):
                if 0 <= addr < 65536:
                    engine._memory[addr] = 0
                    engine.comments.pop(addr, None)

        # Update engine memory and comments for all lines in editor
        for addr in range(num_lines):
            engine._memory[addr] = memory.get(addr, 0)
            if addr in comments:
                engine.comments[addr] = comments[addr]
            else:
                # Clear comment if it was removed
                engine.comments.pop(addr, None)

        # Update our tracking of the max address
        self._max_addr_touched = max(self._max_addr_touched, num_lines - 1)

        return errors
