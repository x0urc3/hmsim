#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Tests for simulation loop and execution."""

import os
from gi.repository import GLib


class TestRunLoop:
    """Test the run loop functionality."""

    def test_run_loop_returns_continue_when_running(self, main_window):
        main_window.simulation_controller.RUN_BATCH_SIZE = 1
        main_window.engine._memory[0] = 0x1100
        main_window.simulation_controller.start()
        result = main_window.simulation_controller._run_loop()
        main_window.simulation_controller.stop()
        assert result == GLib.SOURCE_CONTINUE

    def test_run_loop_returns_remove_when_stopped(self, main_window):
        main_window.simulation_controller.RUN_BATCH_SIZE = 1
        main_window.engine._memory[0] = 0x1100
        main_window.simulation_controller.start()
        main_window.simulation_controller.stop()
        result = main_window.simulation_controller._run_loop()
        assert result == GLib.SOURCE_REMOVE

    def test_run_loop_stops_on_invalid_instruction(self, main_window):
        main_window.engine._memory[0] = 0xFFFF
        main_window.simulation_controller.start()
        main_window.simulation_controller._run_loop()
        assert main_window.simulation_controller.is_running is False
        assert "Error" in main_window.status_bar.get_label()


class TestMemoryViewRefresh:
    """Test that memory view is refreshed after execution."""

    def test_memory_view_refresh_all_updates_display(self, main_window):
        model = main_window.memory_view._model

        main_window.engine._memory[0x7] = 0xABCD
        main_window.engine._memory[0x2000] = 0xABCD

        assert int(model[0x0007][3], 16) == 0, "Memory view should show 0 before refresh"
        assert int(model[0x2000][3], 16) == 0, "Memory view should show 0 before refresh"

        main_window.memory_view.refresh_all()

        assert int(model[0x0007][3], 16) == 0xABCD, "Memory view should show ABCD after refresh"
        assert int(model[0x2000][3], 16) == 0xABCD, "Memory view should show ABCD after refresh"

    def test_update_ui_refreshes_memory_view(self, main_window):
        model = main_window.memory_view._model

        main_window.engine.write_memory(0x7, 0xABCD, notify=False)
        main_window.engine.write_memory(0x2000, 0xABCD, notify=False)

        assert int(model[0x0007][3], 16) == 0, "Memory view should show 0 before update"

        main_window._update_ui()

        assert int(model[0x0007][3], 16) == 0xABCD, "Memory view should show ABCD after _update_ui"
        assert int(model[0x2000][3], 16) == 0xABCD, "Memory view should show ABCD after _update_ui"
