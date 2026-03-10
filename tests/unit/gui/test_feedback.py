#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Tests for status bar and user feedback."""


class TestStatusBar:
    """Test status bar updates."""

    def test_status_bar_running(self, main_window):
        main_window.simulation_controller.start()
        assert main_window.status_bar.get_label() == "Running..."

    def test_status_bar_ready_after_stop(self, main_window):
        main_window.simulation_controller.start()
        main_window.simulation_controller.stop()
        assert main_window.status_bar.get_label() == "Ready"

    def test_status_bar_shows_error(self, main_window):
        main_window.engine._memory[0] = 0xFFFF
        main_window.simulation_controller.step()
        assert "Error" in main_window.status_bar.get_label()
        assert "0x0000" in main_window.status_bar.get_label()

    def test_status_bar_clears_on_new(self, main_window):
        main_window.engine._memory[0] = 0xFFFF
        main_window.simulation_controller.step()
        assert "Error" in main_window.status_bar.get_label()
        main_window.file_controller.new()
        assert main_window.status_bar.get_label() == "Ready"
