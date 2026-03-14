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
    from gi.repository import Gtk, GLib
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
        self._modified_addresses = set()
        self._is_populated = False
        self._is_dark_mode = False
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
        self.tree_view.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        scroll.set_child(self.tree_view)

        # Model columns: icon, dummy (was bg_color), address_str, value_str
        self._model = Gtk.ListStore.new([str, str, str, str])

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

        def region_cell_data_func(column, renderer, model, iter, data):
            # This is called on-demand as the cell is drawn.
            # Efficiently apply colors based on address without storing them in model.
            path = model.get_path(iter)
            addr = int(path.get_indices()[0])
            color = self._get_region_color(addr)
            renderer.set_property("background", color)
            renderer.set_property("background-set", bool(color))

        region_col.set_cell_data_func(region_renderer, region_cell_data_func)

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

    def set_theme(self, is_dark: bool):
        self._is_dark_mode = is_dark
        if self._is_populated:
            # Trigger a redraw to re-run the data function for colors
            self.tree_view.queue_draw()

    def _get_region_color(self, addr: int) -> str:
        if self._text_region[0] <= addr <= self._text_region[1]:
            if self._is_dark_mode:
                return "#27ae60"
            return "#2ECC71"
        if self._data_region[0] <= addr <= self._data_region[1]:
            if self._is_dark_mode:
                return "#2980b9"
            return "#3498DB"
        return ""

    def _populate_model(self):
        if self._is_populated:
            return

        self._model.clear()
        self._is_populated = "populating"

        # Populating 64k rows in batches to keep UI responsive
        batch_size = 3000
        current_addr = 0

        def populate_batch():
            nonlocal current_addr
            end_addr = min(current_addr + batch_size, 65536)

            for addr in range(current_addr, end_addr):
                # We no longer store the color hex in index 1.
                value = self._memory[addr]
                self._model.append(["", "", f"0x{addr:04X}", f"0x{value:04X}"])

            current_addr = end_addr

            if current_addr < 65536:
                return GLib.SOURCE_CONTINUE
            else:
                self._is_populated = True
                self.tree_view.set_model(self._model)
                if self._last_pc >= 0:
                    self.set_pc(self._last_pc)
                return GLib.SOURCE_REMOVE

        GLib.idle_add(populate_batch)

    def reset_modified_rows(self):
        """Reset only rows that were modified (had non-zero values) to zero."""
        for addr in self._modified_addresses:
            if 0 <= addr < 65536 and addr < len(self._model):
                # Only update the value column
                self._model[addr][3] = "0x0000"
        self._modified_addresses.clear()

    def ensure_populated(self):
        """Ensure the model is populated (called once at startup)."""
        self._populate_model()

    def _on_search(self, entry):
        text = entry.get_text()
        try:
            if text.startswith("0x") or text.startswith("0X"):
                addr = int(text, 16)
            else:
                addr = int(text, 0)
            if 0 <= addr < 65536:
                if self._is_populated is not True or addr >= len(self._model):
                    return
                path = Gtk.TreePath.new_from_string(str(addr))
                self.tree_view.scroll_to_cell(path, None, True, 0.5)
                self.tree_view.get_selection().select_path(path)
        except ValueError:
            pass

    def set_memory(self, memory, state_data=None):
        self._memory = memory
        if not self._is_populated:
            self._populate_model()
        else:
            self.refresh_all()
        self._highlighted_path = None

        if state_data:
            for addr, value in state_data.items():
                self.update(addr)
                self._modified_addresses.add(addr)

    def set_pc(self, address):
        old_pc = self._last_pc
        self._last_pc = address

        if self._is_populated is not True:
            return

        if 0 <= old_pc < len(self._model):
            self._model[old_pc][0] = ""

        if 0 <= address < len(self._model):
            self._model[address][0] = "go-next-symbolic"

    def set_regions(self, text_range: tuple[int, int], data_range: tuple[int, int]) -> None:
        self._text_region = text_range
        self._data_region = data_range
        if self._is_populated is True:
            self.tree_view.queue_draw()

    def highlight_address(self, address):
        if 0 <= address < 65536:
            if self._is_populated is True and address < len(self._model):
                path = Gtk.TreePath.new_from_string(str(address))
                self.tree_view.scroll_to_cell(path, None, True, 0.5)
                self.tree_view.get_selection().select_path(path)
                self._highlighted_path = path

    def clear_highlight(self):
        self._highlighted_path = None
        if self._is_populated is True:
            self.tree_view.get_selection().unselect_all()

    def update(self, address=None):
        if address is not None and 0 <= address < 65536:
            if self._is_populated is True and address < len(self._model):
                value = self._memory[address]
                icon = self._model[address][0]
                # Column 1 is no longer used for color hex, data_func handles it
                self._model[address] = [icon, "", f"0x{address:04X}", f"0x{value:04X}"]

    def refresh_addresses(self, addresses):
        """Refresh specific memory addresses in the display."""
        if self._is_populated is not True:
            return
        for addr in addresses:
            if 0 <= addr < 65536 and addr < len(self._model):
                value = self._memory[addr]
                icon = self._model[addr][0]
                self._model[addr] = [icon, "", f"0x{addr:04X}", f"0x{value:04X}"]
                self._modified_addresses.add(addr)


    def refresh_all(self):
        """Refresh all memory values in the display in batches."""
        if not self._is_populated:
            return

        batch_size = 5000
        current_addr = 0

        def refresh_batch():
            nonlocal current_addr
            end_addr = min(current_addr + batch_size, 65536)

            for addr in range(current_addr, end_addr):
                if addr < len(self._model):
                    value = self._memory[addr]
                    icon = self._model[addr][0]
                    self._model[addr] = [icon, "", f"0x{addr:04X}", f"0x{value:04X}"]

            current_addr = end_addr
            if current_addr < 65536:
                return GLib.SOURCE_CONTINUE
            return GLib.SOURCE_REMOVE

        GLib.idle_add(refresh_batch)

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
            if self._is_populated is not True or address >= len(self._model):
                return
            self._memory[address] = value
            icon = self._model[address][0]
            self._model[address] = [icon, "", f"0x{address:04X}", f"0x{value:04X}"]
            if self._memory_changed_callback:
                self._memory_changed_callback(address, value)
        except ValueError:
            pass
