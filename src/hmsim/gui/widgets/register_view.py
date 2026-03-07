#!/usr/bin/env python3
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

        title = Gtk.Label(label="Registers")
        title.set_css_classes(["title", "heading"])
        self.append(title)

        self.registers = {}

        for name in ["PC", "AC", "IR", "SR"]:
            row = self._create_register_row(name)
            self.registers[name] = row["value"]
            self.append(row["box"])

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(separator)

        stats_title = Gtk.Label(label="Statistics")
        stats_title.set_css_classes(["title", "heading"])
        self.append(stats_title)

        for name in ["Cycles", "Instructions"]:
            row = self._create_register_row(name)
            self.registers[name] = row["value"]
            self.append(row["box"])

    def _create_register_row(self, name: str) -> dict:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=f"{name}:")
        label.set_width_chars(4)
        label.set_xalign(1)
        box.append(label)

        value = Gtk.Label(label="0x0000")
        value.set_width_chars(7)
        value.set_xalign(0)
        value.add_css_class("monospace")
        box.append(value)

        return {"box": box, "value": value}

    def update(self, pc: int, ac: int, ir: int, sr: int, cycles: int = 0, instructions: int = 0):
        self.registers["PC"].set_label(f"0x{pc:04X}")
        self.registers["AC"].set_label(f"0x{ac:04X}")
        self.registers["IR"].set_label(f"0x{ir:04X}")
        self.registers["SR"].set_label(f"0x{sr:04X}")
        self.registers["Cycles"].set_label(str(cycles))
        self.registers["Instructions"].set_label(str(instructions))
