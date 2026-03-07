"""Regression tests for EditorView implementation (Step 4.6).

These tests ensure existing widget visibility and functionality is not affected
by the new EditorView implementation.
"""

import pytest
from gi.repository import Gtk

from hmsim.engine.cpu import HMEngine


class TestWidgetExistence:
    """Test that all existing UI widgets still exist after EditorView implementation."""

    def test_register_view_exists(self, main_window):
        assert hasattr(main_window, 'register_view')
        assert main_window.register_view is not None

    def test_memory_view_exists(self, main_window):
        assert hasattr(main_window, 'memory_view')
        assert main_window.memory_view is not None

    def test_status_bar_exists(self, main_window):
        assert hasattr(main_window, 'status_bar')
        assert main_window.status_bar is not None

    def test_toolbar_buttons_exist(self, main_window):
        assert hasattr(main_window, 'btn_reset')
        assert main_window.btn_reset is not None
        assert hasattr(main_window, 'btn_run')
        assert main_window.btn_run is not None
        assert hasattr(main_window, 'btn_step')
        assert main_window.btn_step is not None

    def test_version_dropdown_exists(self, main_window):
        assert hasattr(main_window, 'version_dropdown')
        assert main_window.version_dropdown is not None


class TestWidgetVisibility:
    """Test that all existing widgets remain visible after EditorView implementation."""

    def test_register_view_visible(self, main_window):
        assert main_window.register_view.get_visible() is True

    def test_memory_view_visible(self, main_window):
        assert main_window.memory_view.get_visible() is True

    def test_status_bar_visible(self, main_window):
        assert main_window.status_bar.get_visible() is True

    def test_buttons_visible(self, main_window):
        assert main_window.btn_reset.get_visible() is True
        assert main_window.btn_run.get_visible() is True
        assert main_window.btn_step.get_visible() is True


class TestLayoutIntegrity:
    """Test that the layout structure is maintained correctly.

    NOTE: These tests require left_pane and right_pane to be stored as
    instance attributes (self.left_pane, self.right_pane) in main_window.py.
    """

    def test_left_pane_exists_as_attribute(self, main_window):
        """Verify left_pane is stored as instance attribute."""
        assert hasattr(main_window, 'left_pane'), (
            "main_window must store left_pane as self.left_pane for layout tests"
        )
        assert main_window.left_pane is not None

    def test_right_pane_exists_as_attribute(self, main_window):
        """Verify right_pane is stored as instance attribute."""
        assert hasattr(main_window, 'right_pane'), (
            "main_window must store right_pane as self.right_pane for layout tests"
        )
        assert main_window.right_pane is not None

    def test_left_pane_child_count(self, main_window):
        """Verify left_pane has exactly 1 child (EditorView replaces placeholder)."""
        assert hasattr(main_window, 'left_pane'), (
            "main_window must store left_pane as self.left_pane"
        )
        children = list(main_window.left_pane)
        assert len(children) == 1, (
            f"left_pane should have exactly 1 child (EditorView), got {len(children)}"
        )

    def test_right_pane_child_count(self, main_window):
        """Verify right_pane still has 3 children (RegisterView, MemoryView, status_bar)."""
        assert hasattr(main_window, 'right_pane'), (
            "main_window must store right_pane as self.right_pane"
        )
        children = list(main_window.right_pane)
        assert len(children) == 3, (
            f"right_pane should have exactly 3 children, got {len(children)}"
        )

    def test_editor_replaces_placeholder(self, main_window):
        """Verify the placeholder label is removed from left_pane."""
        assert hasattr(main_window, 'left_pane'), (
            "main_window must store left_pane as self.left_pane"
        )
        children = list(main_window.left_pane)
        for child in children:
            assert not isinstance(child, Gtk.Label) or child.get_label() != "Editor (Coming Soon)", (
                "Placeholder label should be removed from left_pane"
            )


class TestFunctionalRegression:
    """Test that existing functionality still works after EditorView implementation."""

    def test_registers_update_after_step(self, main_window):
        main_window.engine._memory[0] = 0x1100
        initial_pc = main_window.engine.pc
        main_window._on_step(main_window.btn_step)
        assert main_window.engine.pc != initial_pc, "PC should change after step"

    def test_memory_view_displays_memory(self, main_window):
        main_window.engine._memory[0] = 0x1234
        main_window.memory_view.set_memory(main_window.engine._memory)
        tree_model = main_window.memory_view.tree_view.get_model()
        assert tree_model is not None, "Memory view tree model should exist"

    def test_status_bar_shows_message(self, main_window):
        main_window._show_error("Test error message", 0)
        assert "Test error message" in main_window.status_bar.get_label()
        main_window._clear_error()

    def test_version_dropdown_functional(self, main_window):
        main_window.version_dropdown.set_selected(1)
        assert main_window.current_version == "HMv2"

    def test_status_bar_shows_ready_after_reset(self, main_window):
        main_window._show_error("Some error", 0)
        main_window._on_reset(main_window.btn_reset)
        assert main_window.status_bar.get_label() == "Ready"


class TestEditorViewPresence:
    """Test that EditorView is properly integrated after implementation.

    These tests will pass once EditorView is implemented and integrated.
    """

    def test_editor_view_exists_as_attribute(self, main_window):
        """Verify EditorView is stored as instance attribute."""
        assert hasattr(main_window, 'editor_view'), (
            "main_window should have editor_view attribute after Step 4.6"
        )
        assert main_window.editor_view is not None

    def test_editor_view_is_scrolled_window(self, main_window):
        """Verify editor_view is a Gtk.ScrolledWindow."""
        assert hasattr(main_window, 'editor_view')
        assert isinstance(main_window.editor_view, Gtk.ScrolledWindow)
