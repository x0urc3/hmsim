#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator GUI - Main application entry point."""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Gio, GLib, Gdk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

if not GTK_AVAILABLE:
    print("Error: PyGObject (GTK 4) is not installed.", file=sys.stderr)
    print("Install with: pip install PyGObject", file=sys.stderr)
    sys.exit(1)

from hmsim import __version__
from hmsim.engine.cpu import HMEngine
from hmsim.engine.report import print_report
from hmsim.gui.main_window import MainWindow
from hmsim.gui.widgets.about_dialog import AboutDialog


class HMApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='org.hmsim.simulator',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.connect('startup', self.on_startup)
        self.connect('activate', self.on_activate)

    def on_startup(self, app):
        self._setup_actions()
        self._setup_menus()
        self._apply_initial_theme()
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup custom fonts if provided for consistent UI/Mono rendering."""
        font_ui = os.environ.get("HMSIM_FONT_UI")
        font_mono = os.environ.get("HMSIM_FONT_MONO")

        # Apply standard rendering settings for font quality
        try:
            gtk_settings = Gtk.Settings.get_default()
            gtk_settings.set_property("gtk-xft-antialias", 1)
            gtk_settings.set_property("gtk-xft-hinting", 1)
            gtk_settings.set_property("gtk-xft-hintstyle", "hintslight")
            gtk_settings.set_property("gtk-xft-rgba", "rgb")
        except Exception:
            pass

        if font_ui or font_mono:
            try:
                # Load font families into GTK via CSS
                provider = Gtk.CssProvider()

                # Default to system if not set
                ui_family = font_ui or "sans-serif"
                mono_family = font_mono or "monospace"

                css = f"""
                /* Global UI Font and Size */
                * {{
                    font-family: '{ui_family}', 'Segoe UI', 'Arial', sans-serif;
                    font-size: 10pt;
                }}

                /* Monospace widgets - use explicit classes and tags */
                .monospace, textview, .fixed, .editor-view, .memory-view, .register-value, .hex-view {{
                    font-family: '{mono_family}', 'Consolas', 'Courier New', monospace;
                }}

                /* Specific overrides for clarity */
                label, button, headerbar {{
                    font-family: '{ui_family}', 'Segoe UI', 'Arial', sans-serif;
                }}

                /* Editor specific */
                textview {{
                    font-size: 11pt;
                }}
                """


                provider.load_from_data(css.encode())
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(),
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                print(f"Error setting up fonts: {e}")


    def _apply_initial_theme(self):
        from hmsim.gui.settings_manager import SettingsManager
        settings = SettingsManager.get_instance()
        theme = settings.get_theme()
        self._apply_gtk_theme(theme)

    def _apply_gtk_theme(self, theme: str):
        try:
            settings = Gtk.Settings.get_default()
            if theme == "dark":
                settings.set_property("gtk-application-prefer-dark-theme", True)
            elif theme == "light":
                settings.set_property("gtk-application-prefer-dark-theme", False)
            else:
                settings.set_property("gtk-application-prefer-dark-theme", False)
        except Exception:
            pass

    def _setup_actions(self):
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        theme_light = Gio.SimpleAction.new("set_theme_light", None)
        theme_light.connect("activate", self._on_theme_change("light"))
        self.add_action(theme_light)

        theme_dark = Gio.SimpleAction.new("set_theme_dark", None)
        theme_dark.connect("activate", self._on_theme_change("dark"))
        self.add_action(theme_dark)

        theme_system = Gio.SimpleAction.new("set_theme_system", None)
        theme_system.connect("activate", self._on_theme_change("system"))
        self.add_action(theme_system)

    def _on_quit(self, action, param):
        print("Action: quit triggered")
        self.quit()

    def _on_about(self, action, param):
        print("Action: about triggered")
        if hasattr(self, 'win'):
            dialog = AboutDialog(
                parent=self.win,
                program_name="HM Simulator",
                version=__version__,
                comments="A multi-version simulator for the HM 16-bit processor family (v1-v4)",
                copyright="Copyright 2026 Khairulmizam Samsudin",
                authors=["Khairulmizam Samsudin <xource@gmail.com>"],
                website="https://github.com/x0urc3/hmsim",
                license_type="Apache 2.0",
            )
            dialog.present()

    def _on_theme_change(self, theme):
        def handler(action, param):
            from hmsim.gui.settings_manager import SettingsManager
            settings = SettingsManager.get_instance()
            settings.set_theme(theme)
            if hasattr(self, 'win'):
                self.win.apply_theme(theme)
        return handler

    def _setup_menus(self):
        self.menubar_model = Gio.Menu()

        file_menu = Gio.Menu()
        file_menu.append("New", "win.new")
        file_menu.append("Open...", "win.open")
        file_menu.append("Save", "win.save")
        file_menu.append("Save As...", "win.save_as")
        file_menu.append("Quit", "app.quit")
        self.menubar_model.append_submenu("File", file_menu)

        edit_menu = Gio.Menu()
        edit_menu.append("Undo", "win.undo")
        edit_menu.append("Redo", "win.redo")
        self.menubar_model.append_submenu("Edit", edit_menu)

        run_menu = Gio.Menu()
        run_menu.append("Run", "win.run")
        run_menu.append("Step", "win.step")
        run_menu.append("Reset", "win.reset")
        self.menubar_model.append_submenu("Run", run_menu)

        view_menu = Gio.Menu()
        theme_section = Gio.Menu()
        theme_section.append("Light", "app.set_theme_light")
        theme_section.append("Dark", "app.set_theme_dark")
        theme_section.append("System", "app.set_theme_system")
        view_menu.append_section(None, theme_section)
        self.menubar_model.append_submenu("View", view_menu)

        help_menu = Gio.Menu()
        help_menu.append("Tutorial", "win.show_tutorial")
        help_menu.append("User Guide", "win.show_user_guide")
        help_menu.append("About", "app.about")
        self.menubar_model.append_submenu("Help", help_menu)

        # Menus are set up in MainWindow instead for custom layout

        # Standard GTK shortcut strings
        self.set_accels_for_action("win.new", ["<Control>n"])
        self.set_accels_for_action("win.open", ["<Control>o"])
        self.set_accels_for_action("win.save", ["<Control>s"])
        self.set_accels_for_action("win.save_as", ["<Control><Shift>s"])
        self.set_accels_for_action("win.undo", ["<Control>z"])
        self.set_accels_for_action("win.redo", ["<Control><Shift>z", "<Control>y"])
        self.set_accels_for_action("win.run", ["F5"])
        self.set_accels_for_action("win.step", ["F10"])
        self.set_accels_for_action("win.reset", ["F12"])
        self.set_accels_for_action("app.quit", ["<Control>q"])
        self.set_accels_for_action("app.about", ["F1"])

    def on_activate(self, app):
        if not hasattr(self, 'win'):
            self.win = MainWindow(application=app)
        self.win.present()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HM Simulator GUI")
    parser.add_argument(
        "--run-headless",
        metavar="STATE_FILE",
        help="Run in headless mode with the specified state file"
    )
    parser.add_argument(
        "-m", "--max-cycles",
        type=int,
        default=1000000,
        help="Maximum cycles before forced termination (default: 1,000,000)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report in JSON format"
    )
    args, remaining = parser.parse_known_args(argv)

    if args.run_headless:
        return run_headless(args.run_headless, args.max_cycles, args.json)

    app = HMApplication()
    return app.run(remaining)


def run_headless(state_file: str | Path, max_cycles: int, json_output: bool = False) -> int:
    """Run the simulator in headless mode without GUI."""
    state_file_path = Path(state_file)
    try:
        temp_engine = HMEngine("HMv1")
        loaded_arch = temp_engine.load_state(state_file_path)

        architecture = loaded_arch
        if architecture not in HMEngine.VALID_ARCHITECTURES:
            architecture = "HMv2"

        engine = HMEngine(architecture)
        engine.load_state(state_file_path)

        print(f"Loaded {architecture} program. Starting execution...")

        try:
            while engine.total_cycles < max_cycles:
                engine.step()
        except ValueError as e:
            if "Unknown opcode" in str(e) or "not supported" in str(e):
                print(f"\nProgram Halted: {e}")
            else:
                print(f"\nExecution Error: {e}", file=sys.stderr)
                print_report(engine, json_output)
                return 1
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")
            print_report(engine, json_output)
            return 1

        if engine.total_cycles >= max_cycles:
            print(f"\nWarning: Maximum cycles ({max_cycles}) reached.")

        print_report(engine, json_output)
        return 0

    except FileNotFoundError:
        print(f"Error: State file not found: {state_file_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
