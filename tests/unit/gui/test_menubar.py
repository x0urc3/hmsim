#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details

import pytest
import sys
import os
import uuid
from gi.repository import Gtk, Gio, GLib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from hmsim.gui.hm_gui import HMApplication

class TestMenuBar:
    @pytest.fixture
    def app(self):
        """Create an instance of HMApplication and initialize it."""
        application = HMApplication()
        unique_id = f"{os.getpid()}{uuid.uuid4().hex[:8]}"
        application.set_application_id(f"com.hmsim.test{unique_id}")
        application.register(None)
        application.emit('startup')
        application.emit('activate')
        yield application

    def test_actions_exist(self, app):
        """Verify that essential actions are present in the application and window."""
        assert app.lookup_action("quit") is not None
        assert app.lookup_action("about") is not None

        win = app.win
        assert win.lookup_action("new") is not None
        assert win.lookup_action("open") is not None
        assert win.lookup_action("save") is not None
        assert win.lookup_action("step") is not None
        assert win.lookup_action("run") is not None
        assert win.lookup_action("reset") is not None

    def test_menubar_structure(self, app):
        """Verify that the menubar model is correctly populated."""
        menubar = getattr(app, 'menubar_model', app.get_menubar())
        assert menubar is not None

        # Check menus exist (File, Run, Help)
        assert menubar.get_n_items() == 3

        # Check items in first menu (File)
        file_menu_item = menubar.get_item_link(0, Gio.MENU_LINK_SUBMENU)
        assert file_menu_item is not None
        # File: New, Open, Save, Quit
        assert file_menu_item.get_n_items() == 4

        # Verify action names for some items
        # New
        value = file_menu_item.get_item_attribute_value(0, "action", GLib.VariantType.new("s"))
        assert value.get_string() == "win.new"
        # Quit
        value = file_menu_item.get_item_attribute_value(3, "action", GLib.VariantType.new("s"))
        assert value.get_string() == "app.quit"

    def test_accelerators(self, app):
        """Verify that accelerators are correctly set."""
        # Use get_accels_for_action from Gtk.Application
        accels = app.get_accels_for_action("app.quit")
        assert "<Control>q" in accels

        accels = app.get_accels_for_action("win.run")
        assert "F5" in accels

    def test_menubar_visibility_explicit(self, app):
        """Verify that the PopoverMenuBar is added to the window layout."""
        win = app.win
        main_box = win.get_child()
        assert isinstance(main_box, Gtk.Box)

        def find_popover_menubar(widget):
            if isinstance(widget, Gtk.PopoverMenuBar):
                return True
            if isinstance(widget, Gtk.Box):
                child = widget.get_first_child()
                while child:
                    if find_popover_menubar(child):
                        return True
                    child = child.get_next_sibling()
            return False

        found_menubar = find_popover_menubar(main_box)
        assert found_menubar, "PopoverMenuBar was not found in the window layout"
