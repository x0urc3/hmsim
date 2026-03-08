#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - Memory View Widget."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
except ImportError:
    pass


class MemoryView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self._memory = [0] * 65536
        self._memory_changed_callback = None
        self._highlighted_path = None
        self._last_pc = -1
        self._text_region = (0x0000, 0x0100)
        self._data_region = (0x0101, 0xFFFF)
        self._setup_ui()

    def _setup_ui(self):
        title = Gtk.Label(label="Memory")
        title.set_css_classes(["title", "heading"])
        self.append(title)

        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.append(search_box)

        search_label = Gtk.Label(label="Go to Address:")
        search_box.append(search_label)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("0x0000")
        self.search_entry.set_width_chars(8)
        self.search_entry.connect("activate", self._on_search)
        search_box.append(self.search_entry)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        self.append(scroll)

        self.tree_view = Gtk.TreeView()
        self.tree_view.set_show_expanders(False)
        scroll.set_child(self.tree_view)

        self._model = Gtk.ListStore.new([str, str, str, str])
        self.tree_view.set_model(self._model)

        icon_col = Gtk.TreeViewColumn()
        icon_col.set_title("")
        icon_col.set_fixed_width(25)
        self.tree_view.append_column(icon_col)
        icon_renderer = Gtk.CellRendererPixbuf()
        icon_col.pack_start(icon_renderer, False)
        icon_col.add_attribute(icon_renderer, "icon-name", 0)

        region_col = Gtk.TreeViewColumn()
        region_col.set_title("")
        region_col.set_fixed_width(6)
        self.tree_view.append_column(region_col)
        region_renderer = Gtk.CellRendererText()
        region_col.pack_start(region_renderer, False)
        region_col.add_attribute(region_renderer, "background", 1)

        headers = [("Address", 80), ("Value", 100)]
        for i, (header, width) in enumerate(headers):
            col = Gtk.TreeViewColumn()
            col.set_title(header)
            col.set_fixed_width(width)
            col.set_resizable(True)
            self.tree_view.append_column(col)
            renderer = Gtk.CellRendererText()
            col.pack_start(renderer, True)
            col.add_attribute(renderer, "text", i + 2)
            if i == 1:
                renderer.set_property("editable", True)
                renderer.connect("edited", self._on_cell_edited)

        self._populate_model()

    def _get_region_color(self, addr: int) -> str:
        if self._text_region[0] <= addr <= self._text_region[1]:
            return "#2ECC71"
        if self._data_region[0] <= addr <= self._data_region[1]:
            return "#3498DB"
        return ""

    def _populate_model(self):
        self._model.clear()
        for addr in range(65536):
            value = self._memory[addr]
            region_color = self._get_region_color(addr)
            self._model.append(["", region_color, f"0x{addr:04X}", f"0x{value:04X}"])
        if self._last_pc >= 0:
            self.set_pc(self._last_pc)

    def _on_search(self, entry):
        text = entry.get_text()
        try:
            if text.startswith("0x") or text.startswith("0X"):
                addr = int(text, 16)
            else:
                addr = int(text, 0)
            if 0 <= addr < 65536:
                path = Gtk.TreePath.new_from_string(str(addr))
                self.tree_view.scroll_to_cell(path, None, True, 0.5)
                self.tree_view.get_selection().select_path(path)
        except ValueError:
            pass

    def set_memory(self, memory):
        self._memory = memory
        self._populate_model()
        self._highlighted_path = None

    def set_pc(self, address):
        if not 0 <= address < 65536:
            return
        if self._last_pc >= 0 and self._last_pc < len(self._model):
            self._model[self._last_pc][0] = ""
        self._model[address][0] = "go-next-symbolic"
        self._last_pc = address

    def set_regions(self, text_range: tuple[int, int], data_range: tuple[int, int]) -> None:
        self._text_region = text_range
        self._data_region = data_range
        self._populate_model()

    def highlight_address(self, address):
        if 0 <= address < 65536:
            path = Gtk.TreePath.new_from_string(str(address))
            self.tree_view.scroll_to_cell(path, None, True, 0.5)
            self.tree_view.get_selection().select_path(path)
            self._highlighted_path = path

    def clear_highlight(self):
        self._highlighted_path = None
        self.tree_view.get_selection().unselect_all()

    def update(self, address=None):
        if address is not None and 0 <= address < 65536:
            value = self._memory[address]
            icon = self._model[address][0]
            region_color = self._get_region_color(address)
            self._model[address] = [icon, region_color, f"0x{address:04X}", f"0x{value:04X}"]

    def set_memory_changed_callback(self, callback):
        self._memory_changed_callback = callback

    def _on_cell_edited(self, renderer, path, new_text):
        try:
            if new_text.startswith("0x") or new_text.startswith("0X"):
                value = int(new_text, 16)
            else:
                value = int(new_text, 0)
            if not 0 <= value <= 0xFFFF:
                value = value & 0xFFFF
            address = int(path)
            self._memory[address] = value
            icon = self._model[address][0]
            region_color = self._get_region_color(address)
            self._model[address] = [icon, region_color, f"0x{address:04X}", f"0x{value:04X}"]
            if self._memory_changed_callback:
                self._memory_changed_callback(address, value)
        except ValueError:
            pass
