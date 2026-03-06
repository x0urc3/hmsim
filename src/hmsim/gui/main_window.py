#!/usr/bin/env python3
"""HM Simulator - Main Window."""

import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gio, GLib

from . import GTK_AVAILABLE

if not GTK_AVAILABLE:
    print("Error: PyGObject (GTK 4) is not installed.", file=sys.stderr)
    print("Install with: pip install PyGObject", file=sys.stderr)
    sys.exit(1)


VERSIONS = ["HMv1", "HMv2", "HMv3", "HMv4"]


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application=None):
        super().__init__(
            application=application,
            title="HM Simulator",
            default_width=1200,
            default_height=800
        )
        self.current_version = "HMv1"
        self._setup_ui()

    def _setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)

        header = self._create_header_bar()
        main_box.append(header)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        main_box.append(content)

        label = Gtk.Label(label="Welcome to HM Simulator")
        label.set_hexpand(True)
        label.set_vexpand(True)
        content.append(label)

    def _create_header_bar(self) -> Gtk.HeaderBar:
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)

        title_label = Gtk.Label(label="HM Simulator")
        header.set_title_widget(title_label)

        version_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.pack_start(version_box)

        version_label = Gtk.Label(label="Version:")
        version_box.append(version_label)

        self.version_dropdown = Gtk.DropDown.new_from_strings(VERSIONS)
        self.version_dropdown.set_selected(0)
        self.version_dropdown.connect("notify::selected", self._on_version_changed)
        version_box.append(self.version_dropdown)

        return header

    def _on_version_changed(self, dropdown, pspec):
        index = dropdown.get_selected()
        self.current_version = VERSIONS[index]
        print(f"Version changed to: {self.current_version}")
