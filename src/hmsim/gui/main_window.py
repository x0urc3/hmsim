#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
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
from hmsim.gui.widgets.editor_view import EditorView
from hmsim.gui.widgets.help_window import HelpWindow
from hmsim.gui.widgets.setup_dialog import SetupDialog
from hmsim.engine.cpu import HMEngine

from hmsim.tools.hmdas import disassemble


class MainWindow(Gtk.ApplicationWindow):
    RUN_BATCH_SIZE = 1000

    def __init__(self, application=None):
        super().__init__(
            application=application,
            title="HM Simulator",
            default_width=1400,
            default_height=800
        )
        self.set_resizable(True)
        self.current_version = "HMv1"
        self.engine = HMEngine(self.current_version)
        self._is_running = False
        self._run_source_id = None
        self._is_updating_editor = False
        self._help_windows = {}
        self._setup_ui(application)
        self._setup_actions()
        self._connect_engine()

    def _setup_ui(self, app=None):
        self.set_titlebar(self._create_header_bar())

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.set_child(main_box)

        if app:
            menu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
            menu_box.add_css_class("menubar")
            main_box.append(menu_box)

            file_menu = Gio.Menu()
            file_menu.append("New", "win.new")
            file_menu.append("Open...", "win.open")
            file_menu.append("Save", "win.save")
            file_menu.append("Quit", "app.quit")
            file_menu_model = Gio.Menu()
            file_menu_model.append_submenu("File", file_menu)

            run_menu = Gio.Menu()
            run_menu.append("Run", "win.run")
            run_menu.append("Step", "win.step")
            run_menu.append("Reset", "win.reset")
            run_menu_model = Gio.Menu()
            run_menu_model.append_submenu("Run", run_menu)

            setup_menu = Gio.Menu()
            setup_menu.append("Simulator Setup...", "win.setup")
            setup_menu_model = Gio.Menu()
            setup_menu_model.append_submenu("Setup", setup_menu)

            main_file_run = Gio.Menu()
            main_file_run.append_section(None, file_menu_model)
            main_file_run.append_section(None, run_menu_model)
            main_file_run.append_section(None, setup_menu_model)
            menubar_left = Gtk.PopoverMenuBar.new_from_model(main_file_run)
            menu_box.append(menubar_left)

            spacer = Gtk.Box(hexpand=True)
            menu_box.append(spacer)

            help_menu = Gio.Menu()
            help_menu.append("Tutorial", "win.show_tutorial")
            help_menu.append("User Guide", "win.show_user_guide")
            help_menu.append("About", "app.about")
            help_menu_model = Gio.Menu()
            help_menu_model.append_submenu("Help", help_menu)
            menubar_right = Gtk.PopoverMenuBar.new_from_model(help_menu_model)
            menu_box.append(menubar_right)

            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            main_box.append(separator)

        toolbar = self._create_toolbar()
        main_box.append(toolbar)

        # Add CSS provider
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .toolbar {
                padding: 4px;
                border-bottom: 1px solid @borders;
                background-color: @theme_bg_color;
            }
            .menubar {
                background-color: @theme_bg_color;
                border-bottom: 1px solid @borders;
            }
            popovermenubar {
                background-color: @theme_bg_color;
                border-bottom: 1px solid @borders;
                min-height: 30px;
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_hexpand(True)
        paned.set_vexpand(True)
        main_box.append(paned)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        paned.set_start_child(self.left_pane)
        paned.set_resize_start_child(True)
        paned.set_shrink_start_child(False)

        self.editor_view = EditorView(version=self.current_version)
        self.editor_view.set_change_callback(self._on_editor_changed)
        self.editor_view.set_text_region(self.engine.text_region)
        self.left_pane.append(self.editor_view)

        self.right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True)
        self.right_pane.set_size_request(300, -1)
        paned.set_end_child(self.right_pane)
        paned.set_resize_end_child(False)
        paned.set_shrink_end_child(False)

        self.register_view = RegisterView()
        self.register_view.set_version(self.current_version)
        self.right_pane.append(self.register_view)

        self.memory_view = MemoryView()
        self.memory_view.set_vexpand(True)
        self.memory_view.set_memory(self.engine._memory)
        self.memory_view.set_memory_changed_callback(self._on_memory_edited)
        self.memory_view.set_regions(self.engine.text_region, self.engine.data_region)
        self.memory_view.ensure_populated()
        self.right_pane.append(self.memory_view)

        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.set_margin_top(5)
        self.status_bar.set_margin_bottom(5)
        self.status_bar.set_margin_start(10)
        self.status_bar.set_margin_end(10)
        self.right_pane.append(self.status_bar)

    def _create_header_bar(self) -> Gtk.HeaderBar:
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)

        title_label = Gtk.Label(label="HM Simulator")
        header.set_title_widget(title_label)

        return header

    def _create_toolbar(self) -> Gtk.Box:
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(5)
        toolbar.set_margin_bottom(5)
        toolbar.set_margin_start(10)
        toolbar.set_margin_end(10)
        toolbar.add_css_class("toolbar")

        self.btn_reset = Gtk.Button(label="Reset")
        self.btn_reset.set_action_name("win.reset")
        toolbar.append(self.btn_reset)

        self.btn_run = Gtk.Button(label="Run")
        self.btn_run.set_size_request(60, -1)
        self.btn_run.set_action_name("win.run")
        toolbar.append(self.btn_run)

        self.btn_step = Gtk.Button(label="Step")
        self.btn_step.set_action_name("win.step")
        toolbar.append(self.btn_step)

        return toolbar

    def _setup_actions(self):
        self._add_action("new", self._on_new_action)
        self._add_action("open", self._on_open_action)
        self._add_action("save", self._on_save_action)
        self._add_action("step", self._on_step_action)
        self._add_action("run", self._on_run_action)
        self._add_action("reset", self._on_reset_action)
        self._add_action("setup", self._on_setup_action)
        self._add_action("show_tutorial", self._on_show_tutorial)
        self._add_action("show_user_guide", self._on_show_user_guide)

    def _get_docs_path(self) -> str:
        import hmsim
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            return os.path.join(base_path, 'docs')
        else:
            base_path = os.path.dirname(os.path.abspath(hmsim.__file__))
            return os.path.join(base_path, '..', '..', 'docs')

    def _resolve_help_file(self, filename: str) -> str:
        docs_path = self._get_docs_path()
        return os.path.join(docs_path, 'user', filename)

    def _on_show_tutorial(self, action, param):
        self._show_help_window('tutorial', 'Tutorial', 'Tutorial.md')

    def _on_show_user_guide(self, action, param):
        self._show_help_window('user_guide', 'User Guide', 'hmsim_User_Guide.md')

    def _show_help_window(self, key: str, title: str, filename: str):
        if key in self._help_windows:
            self._help_windows[key].present()
            return

        file_path = self._resolve_help_file(filename)
        help_window = HelpWindow(title=title)
        help_window.set_transient_for(self)

        if not help_window.load_markdown(file_path):
            self.status_bar.set_label(f"Error: Help file not found - {file_path}")
            self.status_bar.add_css_class("error")
            return

        help_window.connect('destroy', lambda w: self._help_windows.pop(key, None))
        self._help_windows[key] = help_window
        help_window.present()

    def _add_action(self, name, callback):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def _on_new_action(self, action, param):
        self._on_new(None)

    def _on_open_action(self, action, param):
        self._on_open(None)

    def _on_save_action(self, action, param):
        self._on_save(None)

    def _on_setup(self, button):
        dialog = SetupDialog(
            self,
            self.engine.text_region,
            self.engine.data_region,
            self.current_version
        )

        def on_response(dialog, response):
            if response == Gtk.ResponseType.APPLY:
                try:
                    text_region, data_region = dialog.get_regions()
                    new_version = dialog.get_version()

                    # Handle version change first as it might recreate the engine
                    if new_version != self.current_version:
                        self._on_version_changed(new_version)

                    self.engine.set_regions(text_region, data_region)
                    self.memory_view.set_regions(text_region, data_region)
                    self.editor_view.set_text_region(text_region)
                    self._refresh_editor_from_memory()
                    self.status_bar.set_label("Simulation setup updated")
                except ValueError as e:
                    self.status_bar.set_label(f"Error: {e}")
                    self.status_bar.add_css_class("error")
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def _on_step_action(self, action, param):
        self._on_step(None)

    def _on_run_action(self, action, param):
        self._on_run(None)

    def _on_reset_action(self, action, param):
        self._on_reset(None)

    def _on_setup_action(self, action, param):
        self._on_setup(None)

    def _on_version_changed(self, new_version):
        if new_version != self.current_version:
            old_memory = self.engine._memory.copy()
            old_pc = self.engine.pc
            old_ac = self.engine.ac
            old_ir = self.engine.ir
            old_sr = self.engine.sr
            old_comments = self.engine.comments.copy()
            old_text_region = self.engine.text_region
            old_data_region = self.engine.data_region

            self.current_version = new_version
            self.engine = HMEngine(self.current_version)

            self.engine._memory = old_memory
            self.engine.pc = old_pc
            self.engine.ac = old_ac
            self.engine.ir = old_ir
            self.engine.sr = old_sr
            self.engine.comments = old_comments
            self.engine.set_regions(old_text_region, old_data_region)

            self.editor_view.set_version(new_version)
            self.editor_view.set_text_region(old_text_region)
            errors = self.editor_view.assemble_to_engine(self.engine)

            if errors:
                for addr, error in errors:
                    self._show_error(f"Line {addr}: {error}", addr)

            self.memory_view.set_regions(old_text_region, old_data_region)
            self._connect_engine()
            self._update_ui()

    def _connect_engine(self):
        self.engine.register_observer(self._update_ui)

    def _on_editor_changed(self, text):
        if self._is_updating_editor:
            return
        self._clear_error()
        errors = self.editor_view.assemble_to_engine(self.engine)
        if errors:
            for addr, error in errors:
                self._show_error(f"Line {addr}: {error}", addr)
        self._update_ui()

    def _on_memory_edited(self, address, value):
        self.engine._memory[address] = value
        self.engine.comments.pop(address, None)
        self._refresh_editor_from_memory()

    def _refresh_editor_from_memory(self):
        self._is_updating_editor = True
        try:
            text_start, text_end = self.engine.text_region
            max_addr = text_start - 1

            for addr in range(text_start, text_end + 1):
                if self.engine._memory[addr] != 0 or addr in self.engine.comments:
                    max_addr = addr
                    break

            if max_addr < text_start:
                self.editor_view.set_text("")
                return

            lines = []
            for addr in range(text_start, max_addr + 1):
                machine_code = self.engine._memory[addr]
                has_comment = addr in self.engine.comments

                if machine_code == 0 and not has_comment:
                    lines.append("")
                else:
                    line = disassemble(machine_code, self.current_version)
                    if line.startswith("???"):
                        lines.append("")
                    else:
                        if has_comment:
                            line = f"{line} ; {self.engine.comments[addr]}"
                        lines.append(line)

            self.editor_view.set_text("\n".join(lines))
        finally:
            self._is_updating_editor = False

    def _update_ui(self):
        self.register_view.set_version(self.current_version)
        self.register_view.update(
            pc=self.engine.pc,
            ac=self.engine.ac,
            ir=self.engine.ir,
            sr=self.engine.sr,
            cycles=self.engine.total_cycles,
            instructions=self.engine.total_instructions
        )
        self.memory_view.set_pc(self.engine.pc)
        if self.engine.modified_addresses:
            self.memory_view.refresh_addresses(self.engine.modified_addresses)
            self.engine.clear_modified()

    def _on_step(self, button):
        self._clear_error()
        try:
            self.engine.step()
        except Exception as e:
            self._show_error(str(e), self.engine.pc)

    def _on_run(self, button):
        if self._is_running:
            self._stop_run()
        else:
            self._start_run()

    def _start_run(self):
        self._is_running = True
        self.btn_run.set_label("Stop")
        self.btn_step.set_sensitive(False)
        self.btn_reset.set_sensitive(False)
        self.status_bar.set_label("Running...")
        self._run_source_id = GLib.idle_add(self._run_loop)

    def _stop_run(self):
        self._is_running = False
        if self._run_source_id is not None:
            GLib.source_remove(self._run_source_id)
            self._run_source_id = None
        self.btn_run.set_label("Run")
        self.btn_step.set_sensitive(True)
        self.btn_reset.set_sensitive(True)
        self.status_bar.set_label("Ready")
        self.status_bar.remove_css_class("error")

    def _run_loop(self):
        if not self._is_running:
            return GLib.SOURCE_REMOVE
        try:
            self.engine.run_batch(self.RUN_BATCH_SIZE)
        except Exception as e:
            self._update_ui()
            self._stop_run()
            self._show_error(str(e), self.engine.pc)
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _on_reset(self, button):
        self._clear_error()
        if self._is_running:
            self._stop_run()
        self.engine.reset()

    def _on_new(self, button):
        self._clear_error()
        self.engine.reset()
        self.engine._memory = [0] * 65536
        self.editor_view.set_text("")
        self._update_ui()

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
        dialog.set_initial_name("program.hm")

        filter_hm = Gtk.FileFilter()
        filter_hm.set_name("HM State Files (*.hm)")
        filter_hm.add_pattern("*.hm")
        dialog.set_default_filter(filter_hm)

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
        dialog.set_initial_name("program.hm")

        filter_hm = Gtk.FileFilter()
        filter_hm.set_name("HM State Files (*.hm)")
        filter_hm.add_pattern("*.hm")
        dialog.set_default_filter(filter_hm)

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
        try:
            self.engine.save_state(file_path)
            self.status_bar.set_label(f"Saved to {os.path.basename(file_path)}")
        except Exception as e:
            self.status_bar.set_label(f"Error saving state: {e}")
            self.status_bar.add_css_class("error")

    def _load_state(self, file_path):
        try:
            import json
            with open(file_path, 'r') as f:
                state = json.load(f)

            self.memory_view.reset_modified_rows()

            version = self.engine.load_state(file_path)

            if version not in HMEngine.VALID_VERSIONS:
                version = "HMv2"
                self.status_bar.set_label(f"Warning: Unknown version, loaded as HMv2")
            else:
                self.status_bar.set_label(f"Loaded {version} state")

            self.current_version = version

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

            if self.engine.version != version:
                self._on_version_changed(version)

            setup = state.get("setup", None)
            if setup:
                text_section = state.get("text", {})
                if text_section:
                    lines = []
                    max_addr = max(int(addr, 16) for addr in text_section.keys())
                    text_start = setup.get("text", [0, 256])[0]
                    for addr in range(text_start, max_addr + 1):
                        addr_str = f"0x{addr:04X}"
                        if addr_str in text_section:
                            lines.append(text_section[addr_str])
                        else:
                            lines.append("")
                    self.editor_view.set_text("\n".join(lines))

            self._update_ui()

        except Exception as e:
            self.status_bar.set_label(f"Error loading state: {e}")
            self.status_bar.add_css_class("error")
            print(f"Error loading state: {e}")
