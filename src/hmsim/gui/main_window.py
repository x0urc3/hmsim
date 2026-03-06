#!/usr/bin/env python3
"""HM Simulator - Main Window."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gio', '2.0')
    from gi.repository import Gtk, Gio, GLib
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

if not GTK_AVAILABLE:
    print("Error: PyGObject (GTK 4) is not installed.", file=sys.stderr)
    print("Install with: pip install PyGObject", file=sys.stderr)
    sys.exit(1)

from hmsim.gui.widgets.register_view import RegisterView
from hmsim.gui.widgets.memory_view import MemoryView
from hmsim.engine.cpu import HMEngine


VERSIONS = ["HMv1", "HMv2", "HMv3", "HMv4"]


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application=None):
        super().__init__(
            application=application,
            title="HM Simulator",
            default_width=1200,
            default_height=800
        )
        self.set_resizable(False)
        self.current_version = "HMv1"
        self.engine = HMEngine(self.current_version)
        self._setup_ui()
        self._connect_engine()

    def _setup_ui(self):
        self.set_titlebar(self._create_header_bar())

        main_box = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        self.set_child(main_box)

        left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        main_box.set_start_child(left_pane)
        main_box.set_resize_start_child(True)
        main_box.set_shrink_start_child(False)

        label = Gtk.Label(label="Editor (Coming Soon)")
        label.set_hexpand(True)
        label.set_vexpand(True)
        left_pane.append(label)

        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True)
        right_pane.set_size_request(360, -1)
        main_box.set_end_child(right_pane)
        main_box.set_resize_end_child(False)
        main_box.set_shrink_end_child(False)

        self.register_view = RegisterView()
        right_pane.append(self.register_view)

        self.memory_view = MemoryView()
        self.memory_view.set_vexpand(True)
        right_pane.append(self.memory_view)

        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.set_margin_top(5)
        self.status_bar.set_margin_bottom(5)
        self.status_bar.set_margin_start(10)
        self.status_bar.set_margin_end(10)
        right_pane.append(self.status_bar)

    def _create_header_bar(self) -> Gtk.HeaderBar:
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)

        title_label = Gtk.Label(label="HM Simulator")
        header.set_title_widget(title_label)

        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.pack_start(file_box)

        btn_new = Gtk.Button(label="New")
        btn_new.connect("clicked", self._on_new)
        file_box.append(btn_new)

        btn_open = Gtk.Button(label="Open")
        btn_open.connect("clicked", self._on_open)
        file_box.append(btn_open)

        btn_save = Gtk.Button(label="Save")
        btn_save.connect("clicked", self._on_save)
        file_box.append(btn_save)

        version_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.pack_start(version_box)

        version_label = Gtk.Label(label="Version:")
        version_box.append(version_label)

        self.version_dropdown = Gtk.DropDown.new_from_strings(VERSIONS)
        self.version_dropdown.set_selected(0)
        self.version_dropdown.connect("notify::selected", self._on_version_changed)
        version_box.append(self.version_dropdown)

        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.pack_end(control_box)

        self.btn_reset = Gtk.Button(label="Reset")
        self.btn_reset.connect("clicked", self._on_reset)
        control_box.append(self.btn_reset)

        self.btn_step = Gtk.Button(label="Step")
        self.btn_step.connect("clicked", self._on_step)
        control_box.append(self.btn_step)

        return header

    def _on_version_changed(self, dropdown, pspec):
        index = dropdown.get_selected()
        self.current_version = VERSIONS[index]
        self.engine = HMEngine(self.current_version)
        self._connect_engine()
        self._update_ui()

    def _connect_engine(self):
        self.engine.register_observer(self._update_ui)

    def _update_ui(self):
        self.register_view.update(
            pc=self.engine.pc,
            ac=self.engine.ac,
            ir=self.engine.ir,
            sr=self.engine.sr
        )
        self.memory_view.set_memory(self.engine._memory)

    def _on_step(self, button):
        self._clear_error()
        try:
            self.engine.step()
        except Exception as e:
            self._show_error(str(e), self.engine.pc)

    def _on_reset(self, button):
        self._clear_error()
        self.engine.reset()

    def _on_new(self, button):
        self._clear_error()
        self.engine.reset()

    def _show_error(self, message, address):
        self.status_bar.set_label(f"Error at 0x{address:04X}: {message}")
        self.status_bar.add_css_class("error")
        self.memory_view.highlight_address(address)

    def _clear_error(self):
        self.status_bar.set_label("Ready")
        self.status_bar.remove_css_class("error")
        self.memory_view.clear_highlight()

    def _on_save(self, button):
        self._clear_error()
        dialog = Gtk.FileDialog(title="Save State")
        dialog.set_initial_name("program.json")

        def on_response(dialog, result):
            try:
                file = dialog.save_finish(result)
                if file:
                    file_path = file.get_path()
                    self._save_state(file_path)
            except Exception as e:
                print(f"Save error: {e}")

        dialog.save(None, None, on_response)

    def _on_open(self, button):
        self._clear_error()
        dialog = Gtk.FileDialog(title="Open State")

        def on_response(dialog, result):
            try:
                file = dialog.open_finish(result)
                if file:
                    file_path = file.get_path()
                    self._load_state(file_path)
            except Exception as e:
                print(f"Open error: {e}")

        dialog.open(None, None, on_response)

    def _save_state(self, file_path):
        state = {
            "version": self.current_version,
            "pc": self.engine.pc,
            "ac": self.engine.ac,
            "ir": self.engine.ir,
            "sr": self.engine.sr,
            "memory": list(self.engine._memory)
        }
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self, file_path):
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)

            version = state.get("version", "HMv1")
            if version not in ["HMv1", "HMv2"]:
                print(f"Warning: Version {version} not fully supported, loading as HMv2")
                version = "HMv2"

            self.current_version = version
            self.engine = HMEngine(version)

            self.engine.pc = state.get("pc", 0)
            self.engine.ac = state.get("ac", 0)
            self.engine.ir = state.get("ir", 0)
            self.engine.sr = state.get("sr", 0)

            memory = state.get("memory", [])
            for i, val in enumerate(memory[:65536]):
                self.engine._memory[i] = val & 0xFFFF

            self._connect_engine()
            self._update_ui()

        except Exception as e:
            print(f"Error loading state: {e}")
