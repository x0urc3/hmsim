#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Tests for SetupDialog widget."""

import pytest
from gi.repository import Gtk
from hmsim.gui.widgets.setup_dialog import SetupDialog

@pytest.fixture
def setup_dialog(main_window):
    dialog = SetupDialog(
        main_window,
        (0x0000, 0x0100),
        (0x0101, 0xFFFF),
        "HMv1"
    )
    return dialog

def test_setup_dialog_has_version_dropdown(setup_dialog):
    assert hasattr(setup_dialog, '_version_dropdown')
    assert isinstance(setup_dialog._version_dropdown, Gtk.DropDown)

def test_setup_dialog_initial_version(setup_dialog):
    assert setup_dialog.get_version() == "HMv1"

def test_setup_dialog_change_version(setup_dialog):
    setup_dialog._version_dropdown.set_selected(1) # HMv2
    # Simulate apply
    setup_dialog._on_apply(None)
    assert setup_dialog.get_version() == "HMv2"
