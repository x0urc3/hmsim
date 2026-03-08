#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator GUI - Main application entry point."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Gio, GLib
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

if not GTK_AVAILABLE:
    print("Error: PyGObject (GTK 4) is not installed.", file=sys.stderr)
    print("Install with: pip install PyGObject", file=sys.stderr)
    sys.exit(1)

from hmsim.gui.main_window import MainWindow


class HMApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='org.hmsim.simulator',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.connect('startup', self.on_startup)
        self.connect('activate', self.on_activate)

    def on_startup(self, app):
        self._setup_actions()
        self._setup_menus()

    def _setup_actions(self):
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

    def _on_quit(self, action, param):
        print("Action: quit triggered")
        self.quit()

    def _on_about(self, action, param):
        print("Action: about triggered")
        if hasattr(self, 'win'):
            dialog = Gtk.AboutDialog(
                transient_for=self.win,
                modal=True,
                program_name="HM Simulator",
                version="1.0",
                comments="A multi-version simulator for the HM 16-bit processor family (v1-v4)",
                website="https://github.com/hmsim/hmsim",
            )
            dialog.present()

    def _setup_menus(self):
        self.menubar_model = Gio.Menu()

        file_menu = Gio.Menu()
        file_menu.append("New", "win.new")
        file_menu.append("Open...", "win.open")
        file_menu.append("Save", "win.save")
        file_menu.append("Quit", "app.quit")
        self.menubar_model.append_submenu("File", file_menu)

        run_menu = Gio.Menu()
        run_menu.append("Run", "win.run")
        run_menu.append("Step", "win.step")
        run_menu.append("Reset", "win.reset")
        self.menubar_model.append_submenu("Run", run_menu)

        help_menu = Gio.Menu()
        help_menu.append("About", "app.about")
        self.menubar_model.append_submenu("Help", help_menu)

        self.set_menubar(self.menubar_model)

        # Standard GTK shortcut strings
        self.set_accels_for_action("win.new", ["<Control>n"])
        self.set_accels_for_action("win.open", ["<Control>o"])
        self.set_accels_for_action("win.save", ["<Control>s"])
        self.set_accels_for_action("win.run", ["F5"])
        self.set_accels_for_action("win.step", ["F10"])
        self.set_accels_for_action("win.reset", ["F12"])
        self.set_accels_for_action("app.quit", ["<Control>q"])
        self.set_accels_for_action("app.about", ["F1"])

    def on_activate(self, app):
        if not hasattr(self, 'win'):
            self.win = MainWindow(application=app)
        self.win.present()


def main(argv: list[str] | None = None) -> int:
    app = HMApplication()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main())
