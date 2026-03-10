#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - Register View Widget."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
except ImportError:
    pass


class RegisterView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self._register_changed_callback = None
        self._updating = False
        self._current_values = {"PC": 0, "AC": 0, "IR": 0, "SR": 0}

        self.arch_label = Gtk.Label(label="Arch: HMv1")
        self.arch_label.set_css_classes(["title", "heading"])
        self.arch_label.set_xalign(0.5)
        self.append(self.arch_label)

        separator0 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(separator0)

        title = Gtk.Label(label="Registers")
        title.set_css_classes(["title", "heading"])
        self.append(title)

        # TreeView for Registers
        self._model = Gtk.ListStore.new([str, str])
        self.tree_view = Gtk.TreeView()
        self.tree_view.set_model(self._model)
        self.tree_view.set_headers_visible(False)
        self.tree_view.set_show_expanders(False)

        # Col 1: Name
        name_col = Gtk.TreeViewColumn()
        name_renderer = Gtk.CellRendererText()
        name_col.pack_start(name_renderer, True)
        name_col.add_attribute(name_renderer, "text", 0)
        self.tree_view.append_column(name_col)

        # Col 2: Value
        val_col = Gtk.TreeViewColumn()
        self.val_renderer = Gtk.CellRendererText()
        self.val_renderer.set_property("editable", True)
        self.val_renderer.set_property("font", "monospace")
        self.val_renderer.connect("edited", self._on_cell_edited)
        val_col.pack_start(self.val_renderer, True)
        val_col.add_attribute(self.val_renderer, "text", 1)
        self.tree_view.append_column(val_col)

        # Scrolled window for TreeView
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_child(self.tree_view)
        scroll.set_min_content_height(120)
        self.append(scroll)

        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(separator1)

        stats_title = Gtk.Label(label="Statistics")
        stats_title.set_css_classes(["title", "heading"])
        self.append(stats_title)

        # Statistics Box
        self.stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.append(self.stats_box)

        self.stat_labels = {}
        for name in ["Cycles", "Instructions"]:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=f"{name}:")
            label.set_width_chars(12)
            label.set_xalign(1)
            row.append(label)

            value = Gtk.Label(label="0")
            value.set_xalign(0)
            value.add_css_class("monospace")
            row.append(value)
            self.stat_labels[name] = value
            self.stats_box.append(row)

        self._populate_model()

    def _populate_model(self):
        self._model.clear()
        for name in ["PC", "AC", "IR", "SR"]:
            self._model.append([f"{name}:", "0x0000"])

    def set_architecture(self, arch: str):
        self.arch_label.set_label(f"Arch: {arch}")

    def update(self, pc: int, ac: int, ir: int, sr: int, cycles: int = 0, instructions: int = 0):
        self._current_values = {"PC": pc, "AC": ac, "IR": ir, "SR": sr}
        self._updating = True
        try:
            # Update TreeView Model
            values = [f"0x{pc:04X}", f"0x{ac:04X}", f"0x{ir:04X}", f"0x{sr:04X}"]
            it = self._model.get_iter_first()
            for val in values:
                if it:
                    self._model.set_value(it, 1, val)
                    it = self._model.iter_next(it)

            # Update Stats
            self.stat_labels["Cycles"].set_label(str(cycles))
            self.stat_labels["Instructions"].set_label(str(instructions))
        finally:
            self._updating = False

    def set_register_changed_callback(self, callback):
        self._register_changed_callback = callback

    def _on_cell_edited(self, renderer, path, new_text):
        if self._updating:
            return

        names = ["PC", "AC", "IR", "SR"]
        idx = int(path)
        if idx >= len(names):
            return

        name = names[idx]

        try:
            if new_text.startswith("0x") or new_text.startswith("0X"):
                value = int(new_text, 16)
            else:
                value = int(new_text, 0)
            value = value & 0xFFFF

            if self._register_changed_callback:
                self._register_changed_callback(name, value)
        except ValueError:
            # The update() will revert it if the callback isn't called or engine doesn't change
            # But we should probably force a refresh here if invalid
            pass

        # Trigger UI refresh anyway to ensure it's either the new value or reverted
        # Actually MainWindow observer will trigger update()
