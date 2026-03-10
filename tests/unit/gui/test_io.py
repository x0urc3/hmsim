#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Tests for file I/O operations."""

import json
import os
import tempfile
from gi.repository import GLib


class TestFileOperations:
    """Test file open/save operations and UI updates."""

    def test_load_state_updates_engine_and_ui(self, main_window):
        state = {
            "architecture": "HMv1",
            "pc": 0x0100,
            "ac": 0xABCD,
            "ir": 0x0000,
            "sr": 0x0000,
            "text": {},
            "data": {
                "0x0050": "0x1234"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.hm', delete=False) as f:
            json.dump(state, f)
            temp_path = f.name

        try:
            main_window._load_state(temp_path)

            # Wait for GLib.idle_add in _load_state to finish
            while GLib.MainContext.default().iteration(False):
                pass

            assert main_window.engine.pc == 0x0100
            assert main_window.engine.ac == 0xABCD
            assert main_window.engine._memory[0x50] == 0x1234
        finally:
            os.unlink(temp_path)
