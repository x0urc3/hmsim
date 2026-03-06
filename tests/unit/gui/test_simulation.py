"""Tests for simulation loop and execution."""

from gi.repository import GLib


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
