#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Test for issue #46: memory editing updates editor content correctly."""

import pytest
from gi.repository import Gtk

@pytest.mark.usefixtures("app")
def test_memory_edit_updates_editor(main_window):
    """Verify that editing memory updates the editor with the full program."""
    # 1. Setup engine with some program
    # LOAD 0x0004
    main_window.engine._memory[0] = 0x1004
    # ADD 0x0005
    main_window.engine._memory[1] = 0x5005
    # STORE 0x0006
    main_window.engine._memory[2] = 0x2006

    main_window.engine.set_regions((0, 3), (4, 10))
    main_window.memory_view.set_regions((0, 3), (4, 10))

    # 2. Trigger memory edit at address 1
    # Change ADD 0x0005 to ADD 0x0015
    main_window._on_memory_edited(1, 0x5015)

    # 3. Check editor content
    editor_text = main_window.editor_view.get_text()
    lines = editor_text.strip().split('\n')

    assert len(lines) == 3, f"Expected 3 lines in editor, got {len(lines)}:\n{editor_text}"
    assert "LOAD 0x004" in lines[0]
    assert "ADD 0x015" in lines[1]
    assert "STORE 0x006" in lines[2]
