#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Test for hash fix in _capture_snapshot."""

import pytest
from gi.repository import Gtk

@pytest.mark.usefixtures("app")
def test_hash_large_memory_values(main_window):
    """Verify that hashing memory works with values > 255 (issue reported by user)."""
    # 1. Setup engine with data region containing large values
    main_window.engine.set_regions((0, 3), (4, 10))
    main_window.memory_view.set_regions((0, 3), (4, 10))

    # 2. Add large value to memory location 4 (in data region)
    large_val = 0x5005 # > 255
    main_window.engine._memory[4] = large_val

    # 3. Capture snapshot (should NOT raise ValueError)
    try:
        snapshot = main_window._capture_snapshot()
        assert snapshot is not None
        assert snapshot.memory_hash is not None
    except ValueError as e:
        pytest.fail(f"_capture_snapshot raised ValueError: {e}")

    # 4. Trigger memory edit at address 4
    # This should also work now without errors
    main_window._on_memory_edited(4, 0x1234)

    # 5. Check status (should be Ready)
    assert main_window.status_bar.get_label() == "Ready"
