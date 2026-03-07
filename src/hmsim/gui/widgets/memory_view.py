#!/usr/bin/env python3
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

        self._model = Gtk.ListStore.new([str, str])
        self.tree_view.set_model(self._model)

        headers = [("Address", 80), ("Value", 100)]
        for i, (header, width) in enumerate(headers):
            col = Gtk.TreeViewColumn()
            col.set_title(header)
            col.set_fixed_width(width)
            col.set_resizable(True)
            self.tree_view.append_column(col)
            renderer = Gtk.CellRendererText()
            col.pack_start(renderer, True)
            col.add_attribute(renderer, "text", i)

        self._populate_model()

    def _populate_model(self):
        self._model.clear()
        for addr in range(65536):
            value = self._memory[addr]
            self._model.append([f"0x{addr:04X}", f"0x{value:04X}"])

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
            self._model[address] = [f"0x{address:04X}", f"0x{value:04X}"]
