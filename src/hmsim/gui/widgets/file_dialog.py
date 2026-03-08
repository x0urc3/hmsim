#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - File Dialog Widget."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
except ImportError:
    pass


class FileDialog:
    @staticmethod
    def open_dialog(parent, title="Open File"):
        dialog = Gtk.FileDialog(title=title)
        dialog.set_initial_name("program.hm")

        filter_hm = Gtk.FileFilter()
        filter_hm.set_name("HM State Files (*.hm)")
        filter_hm.add_pattern("*.hm")
        dialog.set_default_filter(filter_hm)

        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Files")
        filter_all.add_pattern("*")

        return dialog

    @staticmethod
    def save_dialog(parent, title="Save File"):
        dialog = Gtk.FileDialog(title=title)
        dialog.set_initial_name("program.hm")

        filter_hm = Gtk.FileFilter()
        filter_hm.set_name("HM State Files (*.hm)")
        filter_hm.add_pattern("*.hm")
        dialog.set_default_filter(filter_hm)

        return dialog
