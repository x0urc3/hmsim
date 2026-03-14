#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Tests for user controls and interactions."""


class TestButtonHandlers:
    """Test button click handlers."""

    def test_on_step_executes_instruction(self, main_window):
        main_window.engine._memory[0] = 0x1100  # LOAD instruction
        initial_pc = main_window.engine.pc
        main_window.simulation_controller.step()
        assert main_window.engine.pc != initial_pc

    def test_on_reset_clears_state(self, main_window):
        main_window.engine.pc = 0x0100
        main_window.engine.ac = 0x1234
        main_window.engine.total_cycles = 100
        main_window.engine._memory[0] = 0x5678
        main_window.simulation_controller.reset()
        assert main_window.engine.pc == 0x0000
        assert main_window.engine.ac == 0x0000
        assert main_window.engine.total_cycles == 0
        assert main_window.engine._memory[0] == 0x5678

    def test_on_reset_preserves_memory(self, main_window):
        main_window.engine._memory[0x0100] = 0xABCD
        main_window.engine._memory[0x0200] = 0x1234
        main_window.simulation_controller.reset()
        assert main_window.engine._memory[0x0100] == 0xABCD
        assert main_window.engine._memory[0x0200] == 0x1234

    def test_on_reset_preserves_editor(self, main_window):
        main_window.editor_view.set_text("LOAD 100\nADD 200")
        main_window.simulation_controller.reset()
        assert main_window.editor_view.get_text() == "LOAD 100\nADD 200"

    def test_on_new_clears_everything(self, main_window):
        main_window.engine.pc = 0x0100
        main_window.engine.ac = 0x1234
        main_window.engine._memory[0] = 0x5678
        main_window.editor_view.set_text("LOAD 100")
        # Ensure not modified to avoid async dialog in test
        main_window.state_manager.sync_base_snapshot()
        main_window.file_controller.new()
        assert main_window.engine.pc == 0x0000
        assert main_window.engine.ac == 0x0000
        assert main_window.engine._memory[0] == 0x0000
        assert main_window.editor_view.get_text() == ""

    def test_on_new_resets_engine(self, main_window):
        main_window.engine.pc = 0x0100
        # Ensure not modified to avoid async dialog in test
        main_window.state_manager.sync_base_snapshot()
        main_window.file_controller.new()
        assert main_window.engine.pc == 0x0000


class TestRunStopToggle:
    """Test Run/Stop toggle behavior."""

    def test_run_starts_execution(self, main_window):
        main_window.engine._memory[0] = 0x1100
        main_window.simulation_controller.start()
        assert main_window.simulation_controller.is_running is True
        assert main_window.btn_run.get_icon_name() == "media-playback-stop-symbolic"
        assert main_window.btn_run.get_tooltip_text() == "Stop Simulation"

    def test_step_disabled_while_running(self, main_window):
        main_window.simulation_controller.start()
        assert main_window.btn_step.get_sensitive() is False

    def test_reset_disabled_while_running(self, main_window):
        main_window.simulation_controller.start()
        assert main_window.btn_reset.get_sensitive() is False

    def test_stop_halts_execution(self, main_window):
        main_window.simulation_controller.start()
        main_window.simulation_controller.stop()
        assert main_window.simulation_controller.is_running is False
        assert main_window.btn_run.get_icon_name() == "media-playback-start-symbolic"
        assert main_window.btn_run.get_tooltip_text() == "Run Simulation"

    def test_buttons_enabled_after_stop(self, main_window):
        main_window.simulation_controller.start()
        main_window.simulation_controller.stop()
        assert main_window.btn_step.get_sensitive() is True
        assert main_window.btn_reset.get_sensitive() is True

    def test_run_button_toggles_on_click(self, main_window):
        main_window.simulation_controller.run()
        assert main_window.simulation_controller.is_running is True
        main_window.simulation_controller.run()
        assert main_window.simulation_controller.is_running is False


class TestResetDuringRun:
    """Test reset behavior while running."""

    def test_reset_stops_run_then_resets(self, main_window):
        main_window.engine._memory[0] = 0x1100
        main_window.simulation_controller.start()
        main_window.simulation_controller.reset()
        assert main_window.simulation_controller.is_running is False
        assert main_window.engine.pc == 0x0000
