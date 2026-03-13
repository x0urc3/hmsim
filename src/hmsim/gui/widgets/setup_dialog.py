#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - Setup Dialog Widget."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False


from hmsim.engine.cpu import HMEngine

class SetupDialog(Gtk.Dialog):
    def __init__(self, parent, current_text_region, current_data_region, current_arch):
        super().__init__(
            title="Simulator Setup",
            transient_for=parent,
            modal=True
        )
        self.set_default_size(400, 400)

        self._text_start = current_text_region[0]
        self._text_end = current_text_region[1]
        self._data_start = current_data_region[0]
        self._data_end = current_data_region[1]
        self._arch = current_arch
        self._is_dark_mode = self._detect_dark_mode()

        self._setup_ui()

    def _detect_dark_mode(self) -> bool:
        try:
            settings = Gtk.Settings.get_default()
            return settings.get_property("gtk-application-prefer-dark-theme")
        except Exception:
            return False

    def _setup_ui(self):
        main_box = self.get_content_area()

        header = Gtk.Label(label="Engine Configuration")
        header.set_css_classes(["title", "heading"])
        header.set_margin_bottom(10)
        main_box.append(header)

        arch_frame = Gtk.Frame()
        arch_label = Gtk.Label(label="Processor Architecture")
        arch_frame.set_label_widget(arch_label)
        arch_frame.set_margin_bottom(10)
        main_box.append(arch_frame)

        arch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        arch_box.set_margin_top(10)
        arch_box.set_margin_bottom(10)
        arch_box.set_margin_start(10)
        arch_box.set_margin_end(10)
        arch_frame.set_child(arch_box)

        arch_box.append(Gtk.Label(label="Architecture:"))
        self._arch_dropdown = Gtk.DropDown.new_from_strings(list(HMEngine.VALID_ARCHITECTURES))
        try:
            self._arch_dropdown.set_selected(list(HMEngine.VALID_ARCHITECTURES).index(self._arch))
        except ValueError:
            self._arch_dropdown.set_selected(0)
        arch_box.append(self._arch_dropdown)

        header_mem = Gtk.Label(label="Define Memory Regions")
        header_mem.set_css_classes(["title", "heading"])
        header_mem.set_margin_bottom(10)
        main_box.append(header_mem)

        text_frame = Gtk.Frame()
        text_label = Gtk.Label()
        text_color = "#27ae60" if self._is_dark_mode else "#2ECC71"
        text_label.set_markup(f"<span foreground='{text_color}'>█</span> Text Section (Executable Code)")
        text_frame.set_label_widget(text_label)
        text_frame.set_margin_bottom(10)
        main_box.append(text_frame)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        text_box.set_margin_top(10)
        text_box.set_margin_bottom(10)
        text_box.set_margin_start(10)
        text_box.set_margin_end(10)
        text_frame.set_child(text_box)

        text_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        text_box.append(text_row)

        text_row.append(Gtk.Label(label="Start:"))
        self._text_start_entry = Gtk.Entry()
        self._text_start_entry.set_text(f"0x{self._text_start:04X}")
        self._text_start_entry.set_placeholder_text("0x0000")
        self._text_start_entry.set_width_chars(10)
        text_row.append(self._text_start_entry)

        text_row.append(Gtk.Label(label="End:"))
        self._text_end_entry = Gtk.Entry()
        self._text_end_entry.set_text(f"0x{self._text_end:04X}")
        self._text_end_entry.set_placeholder_text("0x00FF")
        self._text_end_entry.set_width_chars(10)
        text_row.append(self._text_end_entry)

        data_frame = Gtk.Frame()
        data_label = Gtk.Label()
        data_color = "#2980b9" if self._is_dark_mode else "#3498DB"
        data_label.set_markup(f"<span foreground='{data_color}'>█</span> Data Section")
        data_frame.set_label_widget(data_label)
        data_frame.set_margin_bottom(10)
        main_box.append(data_frame)

        data_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        data_box.set_margin_top(10)
        data_box.set_margin_bottom(10)
        data_box.set_margin_start(10)
        data_box.set_margin_end(10)
        data_frame.set_child(data_box)

        data_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        data_box.append(data_row)

        data_row.append(Gtk.Label(label="Start:"))
        self._data_start_entry = Gtk.Entry()
        self._data_start_entry.set_text(f"0x{self._data_start:04X}")
        self._data_start_entry.set_placeholder_text("0x0101")
        self._data_start_entry.set_width_chars(10)
        data_row.append(self._data_start_entry)

        data_row.append(Gtk.Label(label="End:"))
        self._data_end_entry = Gtk.Entry()
        self._data_end_entry.set_text(f"0x{self._data_end:04X}")
        self._data_end_entry.set_placeholder_text("0xFFFF")
        self._data_end_entry.set_width_chars(10)
        data_row.append(self._data_end_entry)

        self._error_label = Gtk.Label()
        self._error_label.set_markup("<span foreground='red'>Invalid region configuration</span>")
        self._error_label.set_margin_bottom(10)
        self._error_label.set_visible(False)
        main_box.append(self._error_label)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        main_box.append(button_box)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: self.close())
        button_box.append(cancel_btn)

        apply_btn = Gtk.Button(label="Apply")
        apply_btn.connect("clicked", self._on_apply)
        button_box.append(apply_btn)

    def _parse_hex(self, text: str) -> int:
        text = text.strip()
        if text.startswith("0x") or text.startswith("0X"):
            return int(text, 16)
        return int(text, 0)

    def _on_apply(self, button):
        try:
            ts = self._parse_hex(self._text_start_entry.get_text())
            te = self._parse_hex(self._text_end_entry.get_text())
            ds = self._parse_hex(self._data_start_entry.get_text())
            de = self._parse_hex(self._data_end_entry.get_text())
            arch_idx = self._arch_dropdown.get_selected()
            arch = list(HMEngine.VALID_ARCHITECTURES)[arch_idx]

            if not (0 <= ts <= te <= 0xFFFF and 0 <= ds <= de <= 0xFFFF):
                self._show_error("All addresses must be within 0x0000-0xFFFF and start <= end")
                return

            if not (te < ds or ts > de):
                self._show_error("Text and Data regions cannot overlap")
                return

            self._text_start = ts
            self._text_end = te
            self._data_start = ds
            self._data_end = de
            self._arch = arch

            self.response(Gtk.ResponseType.APPLY)
            self.close()

        except ValueError as e:
            self._show_error(f"Invalid address format: {e}")

    def _show_error(self, message: str):
        self._error_label.set_markup(f"<span foreground='red'>{message}</span>")
        self._error_label.set_visible(True)

    def get_regions(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return ((self._text_start, self._text_end), (self._data_start, self._data_end))

    def get_architecture(self) -> str:
        return self._arch
