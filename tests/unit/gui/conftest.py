#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Shared fixtures for GUI tests."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk

from hmsim.gui.main_window import MainWindow


@pytest.fixture
def app():
    """Create a Gtk.Application for testing."""
    application = Gtk.Application()
    return application


@pytest.fixture
def main_window(app):
    """Create a MainWindow instance for testing."""
    window = MainWindow(application=app)
    yield window
    window.close()


@pytest.fixture
def examples_dir():
    """Return the path to the examples directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "examples")
