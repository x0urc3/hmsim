"""Tests for status bar and user feedback."""


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
