#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - File Controller."""

import json
from pathlib import Path
from typing import Optional, Callable
try:
    from gi.repository import Gtk, GLib
except ImportError:
    pass


class FileController:
    """Manages file I/O and persistence logic."""

    def __init__(self, window: Gtk.Window,
                 engine,
                 editor_view,
                 memory_view,
                 state_manager,
                 simulation_controller,
                 status_callback: Callable[[str, bool], None],
                 update_ui_callback: Callable[[], None],
                 title_callback: Callable[[Optional[Path]], None],
                 capture_snapshot_callback: Callable[[], any],
                 arch_change_callback: Callable[[str], None]):
        self.window = window
        self.engine = engine
        self.editor_view = editor_view
        self.memory_view = memory_view
        self.state_manager = state_manager
        self.simulation_controller = simulation_controller
        self._status_callback = status_callback
        self._update_ui_callback = update_ui_callback
        self._title_callback = title_callback
        self._capture_snapshot_callback = capture_snapshot_callback
        self._arch_change_callback = arch_change_callback

        self.current_file: Optional[Path] = None

    def set_engine(self, engine):
        self.engine = engine

    def new(self):
        """Create a new simulation state."""
        if self.state_manager.is_modified:
            self._check_unsaved_changes(self._perform_new)
        else:
            self._perform_new()

    def open(self):
        """Open an existing simulation state."""
        if self.state_manager.is_modified:
            self._check_unsaved_changes(self._show_open_dialog)
        else:
            self._show_open_dialog()

    def save(self):
        """Save the current state."""
        if self.current_file:
            self._save_state(self.current_file)
        else:
            self.save_as()

    def save_as(self):
        """Save the current state to a new file."""
        dialog = Gtk.FileDialog(title="Save State As")
        if self.current_file:
            dialog.set_initial_name(self.current_file.name)
        else:
            dialog.set_initial_name("program.hm")

        filter_hm = Gtk.FileFilter()
        filter_hm.set_name("HM State Files (*.hm)")
        filter_hm.add_pattern("*.hm")
        dialog.set_default_filter(filter_hm)

        def on_response(dialog, result):
            try:
                file = dialog.save_finish(result)
                if file:
                    file_path = Path(file.get_path())
                    self._save_state(file_path)
            except Exception as e:
                print(f"Save As error: {e}")

        dialog.save(self.window, None, on_response)

    def _perform_new(self):
        self.simulation_controller.reset()
        self.engine._memory = [0] * 65536

        from hmsim.engine.state import _get_current_timestamp, _get_debug_default
        from hmsim import __version__
        self.engine.metadata = {
            "debug": _get_debug_default(),
            "software_version": __version__,
            "created_at": _get_current_timestamp(),
            "updated_at": _get_current_timestamp(),
            "log": []
        }

        self.editor_view.set_text("")
        self.current_file = None
        self.state_manager.reset(self._capture_snapshot_callback())
        self._title_callback(self.current_file)
        self._update_ui_callback()

    def _show_open_dialog(self):
        dialog = Gtk.FileDialog(title="Open State")
        dialog.set_initial_name("program.hm")

        filter_hm = Gtk.FileFilter()
        filter_hm.set_name("HM State Files (*.hm)")
        filter_hm.add_pattern("*.hm")
        dialog.set_default_filter(filter_hm)

        def on_response(dialog, result):
            try:
                file = dialog.open_finish(result)
                if file:
                    file_path = Path(file.get_path())
                    self._load_state(file_path)
            except Exception as e:
                print(f"Open error: {e}")

        dialog.open(self.window, None, on_response)

    def _save_state(self, file_path: Path):
        try:
            self._status_callback(f"Saving {file_path.name}...", False)
            self.engine.save_state(file_path)
            self.current_file = file_path
            self.state_manager.sync_base_snapshot()
            self._title_callback(self.current_file)
            self._status_callback(f"Saved to {file_path.name}", False)
        except Exception as e:
            self._status_callback(f"Error saving state: {e}", True)

    def _load_state(self, file_path: Path):
        try:
            self._status_callback(f"Loading {file_path.name}...", False)
            GLib.idle_add(self._perform_load, file_path)
        except Exception as e:
            self._status_callback(f"Error loading state: {e}", True)

    def _perform_load(self, file_path: Path):
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)

            self.memory_view.reset_modified_rows()
            arch = self.engine.load_state(file_path)

            if arch not in self.engine.VALID_ARCHITECTURES:
                self._status_callback(f"Warning: Unknown architecture, loaded as HMv2", False)
                arch = "HMv2"
            else:
                self._status_callback(f"Loaded {arch} state", False)

            self.current_file = file_path

            text_region = self.engine.text_region
            data_region = self.engine.data_region
            self.editor_view.set_text_region(text_region)
            self.memory_view.set_regions(text_region, data_region)

            state_data = {}
            for addr_str in state.get("text", {}):
                addr = int(addr_str, 16)
                state_data[addr] = self.engine._memory[addr]
            for addr_str in state.get("data", {}):
                addr = int(addr_str, 16)
                state_data[addr] = self.engine._memory[addr]

            self.memory_view.set_memory(self.engine._memory, state_data)

            if self.engine.architecture != arch:
                self._arch_change_callback(arch)

            setup = state.get("setup", None)
            if setup:
                text_section = state.get("text", {})
                if text_section:
                    lines = []
                    text_start = setup.get("text", [0, 256])[0]
                    max_addr = text_start - 1
                    if text_section:
                        max_addr = max(int(addr, 16) for addr in text_section.keys())
                        for addr in range(text_start, max_addr + 1):
                            addr_str = f"0x{addr:04X}"
                            if addr_str in text_section:
                                lines.append(text_section[addr_str])
                            else:
                                lines.append("")
                    self.editor_view.set_text("\n".join(lines))

            self._update_ui_callback()

            # Use same timing logic for sync
            from hmsim.gui.widgets.editor_view import EditorView
            GLib.timeout_add(EditorView.DEBOUNCE_DELAY + 50, self._sync_and_title)
            return False
        except Exception as e:
            self._status_callback(f"Error loading state: {e}", True)
            return False

    def _sync_and_title(self):
        self.state_manager.sync_base_snapshot()
        self._title_callback(self.current_file)
        return False

    def confirm_close(self, on_close_confirmed: Callable[[], None]):
        """Confirm if unsaved changes should be saved before closing."""
        if self.state_manager.is_modified:
            self._check_unsaved_changes(on_close_confirmed)
            return True
        return False

    def _check_unsaved_changes(self, callback):
        dialog = Gtk.AlertDialog(
            message="Unsaved Changes",
            detail="You have unsaved changes. Do you want to save them before proceeding?",
            buttons=["Save", "Discard", "Cancel"]
        )

        def on_response(dialog, result):
            if result == 0:  # Save
                self.save()
                callback()
            elif result == 1:  # Discard
                callback()
            # result == 2 is Cancel, do nothing

        dialog.choose(self.window, None, on_response)
