#!/usr/bin/env python3
"""HM Simulator - Main Window."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gio', '2.0')
    from gi.repository import Gtk, Gio, GLib
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

if not GTK_AVAILABLE:
    print("Error: PyGObject (GTK 4) is not installed.", file=sys.stderr)
    print("Install with: pip install PyGObject", file=sys.stderr)
    sys.exit(1)

from hmsim.gui.widgets.register_view import RegisterView


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

        content = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        content.set_hexpand(True)
        content.set_vexpand(True)
        main_box.append(content)

        left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        content.set_start_child(left_pane)
        content.set_resize_start_child(True)

        label = Gtk.Label(label="Welcome to HM Simulator")
        label.set_hexpand(True)
        label.set_vexpand(True)
        left_pane.append(label)

        right_pane = RegisterView()
        content.set_end_child(right_pane)
        content.set_resize_end_child(False)

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
