#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Tests for window setup and UI widget existence."""

from hmsim.engine.cpu import HMEngine


class TestWidgetExistence:
    """Test that all UI widgets are properly created."""

    def test_window_exists(self, main_window):
        assert main_window is not None

    def test_reset_button_exists(self, main_window):
        assert hasattr(main_window, 'btn_reset')
        assert main_window.btn_reset is not None

    def test_step_button_exists(self, main_window):
        assert hasattr(main_window, 'btn_step')
        assert main_window.btn_step is not None

    def test_run_button_exists(self, main_window):
        assert hasattr(main_window, 'btn_run')
        assert main_window.btn_run is not None

    def test_register_view_exists(self, main_window):
        assert hasattr(main_window, 'register_view')
        assert main_window.register_view is not None
        assert hasattr(main_window.register_view, 'arch_label')
        assert main_window.register_view.arch_label is not None

    def test_memory_view_exists(self, main_window):
        assert hasattr(main_window, 'memory_view')
        assert main_window.memory_view is not None

    def test_status_bar_exists(self, main_window):
        assert hasattr(main_window, 'status_bar')
        assert main_window.status_bar is not None


class TestInitialState:
    """Test initial state of UI components."""

    def test_window_title(self, main_window):
        assert main_window.get_title() == "HM Simulator"

    def test_reset_button_icon(self, main_window):
        assert main_window.btn_reset.get_icon_name() == "view-refresh-symbolic"
        assert main_window.btn_reset.get_tooltip_text() == "Reset Simulator"

    def test_step_button_icon(self, main_window):
        assert main_window.btn_step.get_icon_name() == "media-skip-forward-symbolic"
        assert main_window.btn_step.get_tooltip_text() == "Step Instruction"

    def test_run_button_icon(self, main_window):
        assert main_window.btn_run.get_icon_name() == "media-playback-start-symbolic"
        assert main_window.btn_run.get_tooltip_text() == "Run Simulation"

    def test_buttons_sensitive_on_start(self, main_window):
        assert main_window.btn_reset.get_sensitive() is True
        assert main_window.btn_step.get_sensitive() is True
        assert main_window.btn_run.get_sensitive() is True

    def test_architecture_default_hmv1(self, main_window):
        assert main_window.register_view.arch_label.get_label() == "Arch: HMv1"
        assert main_window.current_arch == "HMv1"

    def test_status_bar_initial(self, main_window):
        assert main_window.status_bar.get_label() == "Ready"

    def test_engine_initialized(self, main_window):
        assert main_window.engine is not None
        assert isinstance(main_window.engine, HMEngine)
