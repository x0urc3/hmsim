"""Unit tests for MainWindow GUI components."""

import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gio, GLib

from hmsim.gui.main_window import MainWindow
from hmsim.engine.cpu import HMEngine


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

    def test_version_dropdown_exists(self, main_window):
        assert hasattr(main_window, 'version_dropdown')
        assert main_window.version_dropdown is not None

    def test_register_view_exists(self, main_window):
        assert hasattr(main_window, 'register_view')
        assert main_window.register_view is not None

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

    def test_reset_button_label(self, main_window):
        assert main_window.btn_reset.get_label() == "Reset"

    def test_step_button_label(self, main_window):
        assert main_window.btn_step.get_label() == "Step"

    def test_run_button_label(self, main_window):
        assert main_window.btn_run.get_label() == "Run"

    def test_buttons_sensitive_on_start(self, main_window):
        assert main_window.btn_reset.get_sensitive() is True
        assert main_window.btn_step.get_sensitive() is True
        assert main_window.btn_run.get_sensitive() is True

    def test_version_default_hmv1(self, main_window):
        assert main_window.version_dropdown.get_selected() == 0
        assert main_window.current_version == "HMv1"

    def test_status_bar_initial(self, main_window):
        assert main_window.status_bar.get_label() == "Ready"

    def test_engine_initialized(self, main_window):
        assert main_window.engine is not None
        assert isinstance(main_window.engine, HMEngine)


class TestButtonHandlers:
    """Test button click handlers."""

    def test_on_step_executes_instruction(self, main_window):
        main_window.engine._memory[0] = 0x1100  # LOAD instruction
        initial_pc = main_window.engine.pc
        main_window._on_step(main_window.btn_step)
        assert main_window.engine.pc != initial_pc

    def test_on_reset_clears_state(self, main_window):
        main_window.engine.pc = 0x0100
        main_window.engine.ac = 0x1234
        main_window.engine._memory[0] = 0x5678
        main_window._on_reset(main_window.btn_reset)
        assert main_window.engine.pc == 0x0000
        assert main_window.engine.ac == 0x0000

    def test_on_new_resets_engine(self, main_window):
        main_window.engine.pc = 0x0100
        main_window._on_new(None)
        assert main_window.engine.pc == 0x0000


class TestRunStopToggle:
    """Test Run/Stop toggle behavior."""

    def test_run_starts_execution(self, main_window):
        main_window.engine._memory[0] = 0x1100
        main_window._start_run()
        assert main_window._is_running is True
        assert main_window.btn_run.get_label() == "Stop"

    def test_step_disabled_while_running(self, main_window):
        main_window._start_run()
        assert main_window.btn_step.get_sensitive() is False

    def test_reset_disabled_while_running(self, main_window):
        main_window._start_run()
        assert main_window.btn_reset.get_sensitive() is False

    def test_stop_halts_execution(self, main_window):
        main_window._start_run()
        main_window._stop_run()
        assert main_window._is_running is False
        assert main_window.btn_run.get_label() == "Run"

    def test_buttons_enabled_after_stop(self, main_window):
        main_window._start_run()
        main_window._stop_run()
        assert main_window.btn_step.get_sensitive() is True
        assert main_window.btn_reset.get_sensitive() is True

    def test_run_button_toggles_on_click(self, main_window):
        main_window._on_run(main_window.btn_run)
        assert main_window._is_running is True
        main_window._on_run(main_window.btn_run)
        assert main_window._is_running is False


class TestStatusBar:
    """Test status bar updates."""

    def test_status_bar_running(self, main_window):
        main_window._start_run()
        assert main_window.status_bar.get_label() == "Running..."

    def test_status_bar_ready_after_stop(self, main_window):
        main_window._start_run()
        main_window._stop_run()
        assert main_window.status_bar.get_label() == "Ready"

    def test_status_bar_shows_error(self, main_window):
        main_window.engine._memory[0] = 0xFFFF
        main_window._on_step(main_window.btn_step)
        assert "Error" in main_window.status_bar.get_label()
        assert "0x0000" in main_window.status_bar.get_label()

    def test_status_bar_clears_on_new(self, main_window):
        main_window.engine._memory[0] = 0xFFFF
        main_window._on_step(main_window.btn_step)
        assert "Error" in main_window.status_bar.get_label()
        main_window._on_new(None)
        assert main_window.status_bar.get_label() == "Ready"


class TestRunLoop:
    """Test the run loop functionality."""

    def test_run_loop_returns_continue_when_running(self, main_window):
        main_window.RUN_BATCH_SIZE = 1
        main_window.engine._memory[0] = 0x1100
        main_window._start_run()
        result = main_window._run_loop()
        main_window._stop_run()
        assert result == GLib.SOURCE_CONTINUE

    def test_run_loop_returns_remove_when_stopped(self, main_window):
        main_window.RUN_BATCH_SIZE = 1
        main_window.engine._memory[0] = 0x1100
        main_window._start_run()
        main_window._stop_run()
        result = main_window._run_loop()
        assert result == GLib.SOURCE_REMOVE

    def test_run_loop_stops_on_invalid_instruction(self, main_window):
        main_window.engine._memory[0] = 0xFFFF
        main_window._start_run()
        main_window._run_loop()
        assert main_window._is_running is False
        assert "Error" in main_window.status_bar.get_label()


class TestResetDuringRun:
    """Test reset behavior while running."""

    def test_reset_stops_run_then_resets(self, main_window):
        main_window.engine._memory[0] = 0x1100
        main_window._start_run()
        main_window._on_reset(main_window.btn_reset)
        assert main_window._is_running is False
        assert main_window.engine.pc == 0x0000


class TestVersionDropdown:
    """Test version dropdown functionality."""

    def test_version_change_to_hmv2(self, main_window):
        main_window.version_dropdown.set_selected(1)
        main_window._on_version_changed(main_window.version_dropdown, None)
        assert main_window.current_version == "HMv2"

    def test_version_preserves_memory(self, main_window):
        main_window.engine._memory[0x0100] = 0x1234
        main_window.version_dropdown.set_selected(1)
        main_window._on_version_changed(main_window.version_dropdown, None)
        assert main_window.engine._memory[0x0100] == 0x1234

    def test_version_change_creates_new_engine(self, main_window):
        old_engine_id = id(main_window.engine)
        main_window.version_dropdown.set_selected(1)
        main_window._on_version_changed(main_window.version_dropdown, None)
        assert id(main_window.engine) != old_engine_id


class TestFileOperations:
    """Test file open/save operations and UI updates."""

    def test_load_state_updates_engine_and_ui(self, main_window):
        state = {
            "version": "HMv1",
            "pc": 0x0100,
            "ac": 0xABCD,
            "ir": 0x0000,
            "sr": 0x0000,
            "memory": {
                "80": 0x1234
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(state, f)
            temp_path = f.name

        try:
            main_window._load_state(temp_path)

            assert main_window.engine.pc == 0x0100
            assert main_window.engine.ac == 0xABCD
            assert main_window.engine._memory[80] == 0x1234
        finally:
            os.unlink(temp_path)
