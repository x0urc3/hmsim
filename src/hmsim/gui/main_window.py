#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - Main Window."""

import sys
import array
from pathlib import Path
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

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
from hmsim.gui.state_manager import StateManager, Snapshot
from hmsim.gui.controllers.simulation_controller import SimulationController
from hmsim.gui.controllers.file_controller import FileController

from hmsim.tools.hmdas import disassemble


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application=None):
        super().__init__(
            application=application,
            title="HM Simulator",
            default_width=1400,
            default_height=800
        )
        self.set_resizable(True)
        self.current_arch = "HMv1"
        self.engine = HMEngine(self.current_arch)
        self._is_updating_editor = False
        self._help_windows = {}

        self.state_manager = StateManager(self._apply_snapshot)
        self.simulation_controller = SimulationController(
            self.engine,
            update_ui_callback=self._update_ui,
            show_error_callback=self._show_error,
            status_callback=self._set_status,
            controls_callback=self._set_controls_sensitivity
        )

        self._setup_ui(application)

        self.file_controller = FileController(
            self,
            self.engine,
            self.editor_view,
            self.memory_view,
            self.state_manager,
            self.simulation_controller,
            status_callback=self._set_status,
            update_ui_callback=self._update_ui,
            title_callback=self._update_window_title,
            capture_snapshot_callback=self._capture_snapshot,
            arch_change_callback=self._on_arch_changed
        )

        self._setup_actions()
        self._connect_engine()

        self._apply_saved_theme()

        # Capture initial base snapshot (empty state)
        initial_snapshot = self._capture_snapshot()
        self.state_manager.reset(initial_snapshot)
        self._update_window_title()
        self.connect("close-request", self._on_close_request)

    def _setup_ui(self, application=None):
        self.set_titlebar(self._create_header_bar())

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        main_box.add_css_class("main-container")
        self.set_child(main_box)

        if application:
            main_box.append(self._create_menubar())
            main_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        main_box.append(self._create_toolbar())
        self._setup_styles()
        main_box.append(self._create_main_content())

        # Status Bar Footer
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        status_box.add_css_class("status-bar")

        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.set_halign(Gtk.Align.START)
        self.status_bar.set_margin_top(4)
        self.status_bar.set_margin_bottom(4)
        self.status_bar.set_margin_start(10)
        self.status_bar.set_margin_end(10)

        status_box.append(self.status_bar)
        main_box.append(status_box)

    def _create_menubar(self) -> Gtk.Box:
        menu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        menu_box.add_css_class("menubar")

        file_menu = Gio.Menu()
        file_menu.append("New", "win.new")
        file_menu.append("Open...", "win.open")
        file_menu.append("Save", "win.save")
        file_menu.append("Save As...", "win.save_as")
        file_menu.append("Quit", "app.quit")
        file_menu_model = Gio.Menu()
        file_menu_model.append_submenu("File", file_menu)

        edit_menu = Gio.Menu()
        edit_menu.append("Undo", "win.undo")
        edit_menu.append("Redo", "win.redo")
        edit_menu_model = Gio.Menu()
        edit_menu_model.append_submenu("Edit", edit_menu)

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

        view_menu = Gio.Menu()
        theme_menu = Gio.Menu()
        theme_menu.append("Light", "app.set_theme_light")
        theme_menu.append("Dark", "app.set_theme_dark")
        theme_menu.append("System", "app.set_theme_system")
        view_menu.append_submenu("Theme", theme_menu)
        view_menu_model = Gio.Menu()
        view_menu_model.append_submenu("View", view_menu)

        main_file_run = Gio.Menu()
        main_file_run.append_section(None, file_menu_model)
        main_file_run.append_section(None, edit_menu_model)
        main_file_run.append_section(None, run_menu_model)
        main_file_run.append_section(None, setup_menu_model)
        main_file_run.append_section(None, view_menu_model)
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

        return menu_box

    def _setup_styles(self):
        self._css_provider = Gtk.CssProvider()
        self._update_css_theme("system")
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            self._css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _update_css_theme(self, theme: str):
        if theme == "dark":
            bg = "#2d2d2d"
            fg = "#e0e0e0"
            hover_bg = "#404040"
            hover_fg = "#ffffff"
            text_region = "#27ae60"
            data_region = "#2980b9"
            error_fg = "#e74c3c"
            popover_border = "#444444"
            strong_border = "#ffffff"
        else:
            bg = "#fafafa"
            fg = "#2c3e50"
            hover_bg = "#e0e0e0"
            hover_fg = "#000000"
            text_region = "#2ECC71"
            data_region = "#3498DB"
            error_fg = "#c0392b"
            popover_border = "#dddddd"
            strong_border = "#000000"

        css_data = f"""
            window, .main-container, .register-box, .editor-box, scrolledwindow {{
                background-color: {bg};
                color: {fg};
            }}
            .custom-header {{
                background-color: {bg};
                color: {fg};
                border-bottom: 1px solid @borders;
            }}
            label {{
                color: {fg};
            }}
            box, paned {{
                background-color: {bg};
            }}
            textview, textview text {{
                background-color: {bg};
                color: {fg};
            }}
            treeview {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {popover_border};
            }}
            treeview.view {{
                background-color: {bg};
                color: {fg};
            }}
            treeview.view:hover {{
                background-color: {hover_bg};
            }}
            treeview header button {{
                background-color: {bg};
                color: {fg};
                border-right: 1px solid {popover_border};
                border-bottom: 1px solid {popover_border};
                border-left: none;
            }}
            /* Address and PC Arrow header highlights */
            treeview header button:nth-child(1),
            treeview header button:nth-child(3) {{
                border-left: 1px solid {strong_border};
                border-right: 1px solid {strong_border};
            }}
            treeview.view cell {{
                border-right: 1px solid {popover_border};
                border-bottom: 1px solid {popover_border};
            }}
            entry {{
                background-color: {bg};
                color: {fg};
                border: 1px solid @borders;
            }}
            button {{
                color: {fg};
            }}
            popover content, popover list, popover.menu, popover.menu box {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {popover_border};
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                padding: 4px;
                border-radius: 8px;
            }}
            popover arrow {{
                background-color: {bg};
                border: 1px solid {popover_border};
            }}
            popover label {{
                background-color: transparent;
                padding: 4px 8px;
            }}
            popover contents {{
                background-color: {bg};
                color: {fg};
                padding: 0;
                margin: 0;
            }}
            modelbutton {{
                border-radius: 4px;
                margin: 1px 2px;
                min-height: 28px;
            }}
            modelbutton:hover, modelbutton:active,
            popover list row:hover, popover list row:active,
            .menubar popover button:hover {{
                background-color: {hover_bg};
                color: {hover_fg};
                border: none;
            }}
            modelbutton:hover label,
            popover list row:hover label,
            .menubar popover button:hover label {{
                color: {hover_fg};
            }}
            .toolbar {{
                padding: 4px;
                border-bottom: 1px solid @borders;
                background-color: {bg};
            }}
            .toolbar button {{
                color: {fg};
            }}
            .menubar {{
                background-color: {bg};
                border-bottom: 1px solid @borders;
            }}
            .status-bar {{
                background-color: {bg};
                border-top: 1px solid @borders;
                font-size: 0.9em;
            }}
            popovermenubar {{
                background-color: {bg};
                border-bottom: 1px solid @borders;
                min-height: 30px;
            }}
            popovermenubar > contents {{
                background-color: {bg};
                color: {fg};
            }}
            .region-text {{
                background-color: {text_region};
            }}
            .region-data {{
                background-color: {data_region};
            }}
            .error {{
                color: {error_fg};
            }}
        """.encode()
        self._css_provider.load_from_data(css_data)

    def _apply_saved_theme(self):
        from hmsim.gui.settings_manager import SettingsManager
        settings = SettingsManager.get_instance()
        theme = settings.get_theme()
        self.apply_theme(theme)

    def apply_theme(self, theme: str):
        if theme not in ("light", "dark", "system"):
            theme = "system"

        try:
            settings = Gtk.Settings.get_default()
            if theme == "dark":
                settings.set_property("gtk-application-prefer-dark-theme", True)
                self._dark_mode = True
            elif theme == "light":
                settings.set_property("gtk-application-prefer-dark-theme", False)
                self._dark_mode = False
            else:
                settings.set_property("gtk-application-prefer-dark-theme", False)
                self._dark_mode = False

            self._update_css_theme(theme)
            self._notify_theme_change(theme)
        except Exception:
            pass

    def _notify_theme_change(self, theme: str):
        is_dark = theme == "dark"
        if hasattr(self, 'memory_view'):
            self.memory_view.set_theme(is_dark)
        if hasattr(self, 'editor_view') and hasattr(self.editor_view, 'set_theme'):
            self.editor_view.set_theme(is_dark)
        if hasattr(self, 'register_view') and hasattr(self.register_view, 'set_theme'):
            self.register_view.set_theme(is_dark)
        for window in self._help_windows.values():
            if hasattr(window, 'set_theme'):
                window.set_theme(is_dark)

    def _create_main_content(self) -> Gtk.Paned:
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_hexpand(True)
        paned.set_vexpand(True)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.left_pane.add_css_class("editor-box")
        paned.set_start_child(self.left_pane)
        paned.set_resize_start_child(True)
        paned.set_shrink_start_child(False)

        self.editor_view = EditorView(arch=self.current_arch)
        self.editor_view.set_change_callback(self._on_editor_changed)
        self.editor_view.set_text_region(self.engine.text_region)
        self.left_pane.append(self.editor_view)

        self.right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True)
        self.right_pane.add_css_class("register-box")
        self.right_pane.set_size_request(300, -1)
        paned.set_end_child(self.right_pane)
        paned.set_resize_end_child(False)
        paned.set_shrink_end_child(False)

        self.register_view = RegisterView()
        self.register_view.set_architecture(self.current_arch)
        self.register_view.set_register_changed_callback(self._on_register_edited)
        self.right_pane.append(self.register_view)

        self.memory_view = MemoryView()
        self.memory_view.set_vexpand(True)
        self.memory_view.set_memory(self.engine._memory)
        self.memory_view.set_memory_changed_callback(self._on_memory_edited)
        self.memory_view.set_regions(self.engine.text_region, self.engine.data_region)
        self.memory_view.ensure_populated()
        self.right_pane.append(self.memory_view)

        return paned

    def _create_header_bar(self) -> Gtk.HeaderBar:
        header = Gtk.HeaderBar()
        header.add_css_class("custom-header")
        header.set_show_title_buttons(True)

        self.title_label = Gtk.Label(label="HM Simulator")
        header.set_title_widget(self.title_label)

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
        self._add_action("save_as", self._on_save_as_action)
        self._add_action("undo", self._on_undo_action)
        self._add_action("redo", self._on_redo_action)
        self._add_action("step", self._on_step_action)
        self._add_action("run", self._on_run_action)
        self._add_action("reset", self._on_reset_action)
        self._add_action("setup", self._on_setup_action)
        self._add_action("show_tutorial", self._on_show_tutorial)
        self._add_action("show_user_guide", self._on_show_user_guide)

    def _add_action(self, name, callback):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

    # Action Handlers
    def _on_new_action(self, action, param):
        self.file_controller.new()

    def _on_open_action(self, action, param):
        self.file_controller.open()

    def _on_save_action(self, action, param):
        self.file_controller.save()

    def _on_save_as_action(self, action, param):
        self.file_controller.save_as()

    def _on_undo_action(self, action, param):
        self.state_manager.undo()
        self._update_window_title(self.file_controller.current_file)

    def _on_redo_action(self, action, param):
        self.state_manager.redo()
        self._update_window_title(self.file_controller.current_file)

    def _on_step_action(self, action, param):
        self.simulation_controller.step()

    def _on_run_action(self, action, param):
        self.simulation_controller.run()

    def _on_reset_action(self, action, param):
        self.simulation_controller.reset()

    def _on_setup_action(self, action, param):
        self._on_setup(None)

    # Support methods for Help and Docs
    def _get_docs_path(self) -> Path:
        import hmsim
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
            return base_path / 'docs'
        else:
            base_path = Path(hmsim.__file__).resolve().parent
            return base_path / '..' / '..' / 'docs'

    def _resolve_help_file(self, filename: str) -> Path:
        docs_path = self._get_docs_path()
        return docs_path / 'user' / filename

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

    # Core State Management and UI Updates
    @property
    def is_modified(self) -> bool:
        return self.state_manager.is_modified

    def _capture_snapshot(self) -> Snapshot:
        start, end = self.engine.data_region
        data_to_hash = array.array('H', self.engine._memory[start:end+1]).tobytes()

        return self.state_manager.capture_snapshot(
            editor_text=self.editor_view.get_text(),
            memory_data=data_to_hash,
            architecture=self.current_arch,
            text_region=self.engine.text_region,
            data_region=self.engine.data_region
        )

    def _apply_snapshot(self, snapshot: Snapshot):
        self._is_updating_editor = True
        try:
            self.editor_view.set_text(snapshot.editor_text)

            if snapshot.architecture != self.current_arch:
                self.current_arch = snapshot.architecture
                self.engine = HMEngine(self.current_arch)
                self.simulation_controller.set_engine(self.engine)
                self.file_controller.set_engine(self.engine)
                self.editor_view.set_architecture(self.current_arch)
                self._connect_engine()

            if (snapshot.text_region != self.engine.text_region or
                snapshot.data_region != self.engine.data_region):
                self.engine.set_regions(snapshot.text_region, snapshot.data_region)
                self.memory_view.set_regions(snapshot.text_region, snapshot.data_region)
                self.editor_view.set_text_region(snapshot.text_region)

            self.editor_view.assemble_to_engine(self.engine)
            self._update_ui()
        finally:
            self._is_updating_editor = False

    def _update_window_title(self, current_file: Optional[Path] = None):
        title = "HM Simulator"
        if current_file:
            title += f" - {current_file.name}"
        if self.is_modified:
            title += "*"
        self.set_title(title)
        if hasattr(self, 'title_label'):
            self.title_label.set_label(title)

    def _on_close_request(self, window):
        return self.file_controller.confirm_close(self.destroy)

    def _on_setup(self, button):
        dialog = SetupDialog(
            self,
            self.engine.text_region,
            self.engine.data_region,
            self.current_arch
        )

        def on_response(dialog, response):
            if response == Gtk.ResponseType.APPLY:
                try:
                    text_region, data_region = dialog.get_regions()
                    new_arch = dialog.get_architecture()

                    if new_arch != self.current_arch:
                        self._on_arch_changed(new_arch)

                    self.engine.set_regions(text_region, data_region)
                    self.memory_view.set_regions(text_region, data_region)
                    self.editor_view.set_text_region(text_region)
                    self._refresh_editor_from_memory()
                    self._set_status("Simulation setup updated", False)
                except ValueError as e:
                    self._set_status(f"Error: {e}", True)
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.present()

    def _on_arch_changed(self, new_arch):
        if new_arch != self.current_arch:
            old_memory = self.engine._memory.copy()
            old_pc = self.engine.pc
            old_ac = self.engine.ac
            old_ir = self.engine.ir
            old_sr = self.engine.sr
            old_comments = self.engine.comments.copy()
            old_text_region = self.engine.text_region
            old_data_region = self.engine.data_region

            self.current_arch = new_arch
            self.engine = HMEngine(self.current_arch)
            self.simulation_controller.set_engine(self.engine)
            self.file_controller.set_engine(self.engine)

            self.engine._memory = old_memory
            self.engine.pc = old_pc
            self.engine.ac = old_ac
            self.engine.ir = old_ir
            self.engine.sr = old_sr
            self.engine.comments = old_comments
            self.engine.set_regions(old_text_region, old_data_region)

            self.editor_view.set_architecture(new_arch)
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
        self.state_manager.push_history(self._capture_snapshot())
        self._update_window_title(self.file_controller.current_file)
        errors = self.editor_view.assemble_to_engine(self.engine)
        if errors:
            for addr, error in errors:
                self._show_error(f"Line {addr}: {error}", addr)
        self._update_ui()

    def _on_memory_edited(self, address, value):
        self.engine._memory[address] = value
        self.engine.comments.pop(address, None)
        self.state_manager.push_history(self._capture_snapshot())
        self._update_window_title(self.file_controller.current_file)
        self._refresh_editor_from_memory()

    def _on_register_edited(self, name, value):
        if name == "PC":
            self.engine.pc = value
        elif name == "AC":
            self.engine.ac = value
        elif name == "IR":
            self.engine.ir = value
        elif name == "SR":
            self.engine.sr = value
        self.engine._notify_observers()

    def _refresh_editor_from_memory(self):
        self._is_updating_editor = True
        try:
            text_start, text_end = self.engine.text_region
            max_addr = text_start - 1

            for addr in range(text_end, text_start - 1, -1):
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
                    line = disassemble(machine_code, self.current_arch)
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
        self.register_view.set_architecture(self.current_arch)
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

    def _set_status(self, message: str, is_error: bool):
        self.status_bar.set_label(message)
        if is_error:
            self.status_bar.add_css_class("error")
        else:
            self.status_bar.remove_css_class("error")

    def _set_controls_sensitivity(self, sensitive: bool):
        """Enable or disable UI controls based on simulation state."""
        self.btn_run.set_label("Run" if sensitive else "Stop")
        self.btn_step.set_sensitive(sensitive)
        self.btn_reset.set_sensitive(sensitive)

    def _show_error(self, message, address):
        self._set_status(f"Error at 0x{address:04X}: {message}", True)
        self.memory_view.highlight_address(address)

    def _clear_error(self):
        self._set_status("Ready", False)
        self.memory_view.clear_highlight()
