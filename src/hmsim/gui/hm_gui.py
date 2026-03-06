#!/usr/bin/env python3
"""HM Simulator GUI - Main application entry point."""

import sys
from . import GTK_AVAILABLE

if not GTK_AVAILABLE:
    print("Error: PyGObject (GTK 4) is not installed.", file=sys.stderr)
    print("Install with: pip install PyGObject", file=sys.stderr)
    sys.exit(1)

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

from .main_window import MainWindow


class HMApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='com.hmsim.app',
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


def main(argv: list[str] | None = None) -> int:
    app = HMApplication()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main())
