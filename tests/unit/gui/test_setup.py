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
