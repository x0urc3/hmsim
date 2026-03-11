#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Test for file dialog flows in FileController."""

import pytest
from unittest.mock import MagicMock, patch
from gi.repository import Gtk, Gio
from hmsim.gui.controllers.file_controller import FileController

@pytest.fixture
def mock_file_controller(main_window):
    """Provide a FileController with mocked dependencies for testing flows."""
    # We use the actual main_window but we'll mock some methods
    return main_window.file_controller

def test_check_unsaved_changes_discard(mock_file_controller):
    """Verify that clicking Discard calls the callback."""
    callback = MagicMock()

    # Mock Gtk.AlertDialog
    with patch('gi.repository.Gtk.AlertDialog') as MockDialog:
        mock_dialog_instance = MockDialog.return_value
        # Mock choose_finish to return 1 (Discard)
        mock_dialog_instance.choose_finish.return_value = 1

        # Trigger _check_unsaved_changes
        mock_file_controller._check_unsaved_changes(callback)

        # Capture the callback passed to choose
        args, kwargs = mock_dialog_instance.choose.call_args
        on_response = args[2]

        # Simulate the response from GTK
        on_response(mock_dialog_instance, MagicMock(spec=Gio.AsyncResult))

        # Verify callback was called
        callback.assert_called_once()

def test_check_unsaved_changes_save(mock_file_controller):
    """Verify that clicking Save calls save() with the callback."""
    callback = MagicMock()
    mock_file_controller.save = MagicMock()

    # Mock Gtk.AlertDialog
    with patch('gi.repository.Gtk.AlertDialog') as MockDialog:
        mock_dialog_instance = MockDialog.return_value
        # Mock choose_finish to return 0 (Save)
        mock_dialog_instance.choose_finish.return_value = 0

        # Trigger _check_unsaved_changes
        mock_file_controller._check_unsaved_changes(callback)

        # Capture the callback passed to choose
        args, kwargs = mock_dialog_instance.choose.call_args
        on_response = args[2]

        # Simulate the response from GTK
        on_response(mock_dialog_instance, MagicMock(spec=Gio.AsyncResult))

        # Verify save was called with the callback
        mock_file_controller.save.assert_called_once_with(on_finish=callback)

def test_check_unsaved_changes_cancel(mock_file_controller):
    """Verify that clicking Cancel does nothing."""
    callback = MagicMock()
    mock_file_controller.save = MagicMock()

    # Mock Gtk.AlertDialog
    with patch('gi.repository.Gtk.AlertDialog') as MockDialog:
        mock_dialog_instance = MockDialog.return_value
        # Mock choose_finish to return 2 (Cancel)
        mock_dialog_instance.choose_finish.return_value = 2

        # Trigger _check_unsaved_changes
        mock_file_controller._check_unsaved_changes(callback)

        # Capture the callback passed to choose
        args, kwargs = mock_dialog_instance.choose.call_args
        on_response = args[2]

        # Simulate the response from GTK
        on_response(mock_dialog_instance, MagicMock(spec=Gio.AsyncResult))

        # Verify nothing was called
        callback.assert_not_called()
        mock_file_controller.save.assert_not_called()
