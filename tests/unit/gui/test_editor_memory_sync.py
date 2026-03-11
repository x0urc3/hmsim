#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Test for issue: editor changes not reflected in memory view."""

import pytest
from gi.repository import GLib

@pytest.mark.usefixtures("app")
def test_editor_change_updates_memory(main_window):
    """Verify that editing the editor updates the engine's memory and modified_addresses."""
    # 1. Set initial text
    main_window.editor_view.set_text("LOAD 0x004")

    # 2. Trigger assembly (manually to avoid debounce delay)
    main_window.editor_view.assemble_to_engine(main_window.engine)

    # Check if memory was updated at 0x0000 (LOAD 0x004 = 0x1004)
    assert main_window.engine._memory[0] == 0x1004

    # 3. Change text in editor
    main_window.editor_view.set_text("LOAD 0x006")

    # 4. Assemble again
    main_window.editor_view.assemble_to_engine(main_window.engine)

    # Check if memory was updated at 0x0000 (LOAD 0x006 = 0x1006)
    assert main_window.engine._memory[0] == 0x1006

    # 5. Check if modified_addresses is NOT empty
    # If this is empty, MemoryView will NOT refresh in _update_ui
    assert 0 in main_window.engine.modified_addresses, "Address 0 should be in modified_addresses"
