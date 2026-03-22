#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""About Dialog Widget - Custom about dialog for HM Simulator."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Gdk, Gio
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False


class AboutDialog(Gtk.Dialog):
    def __init__(
        self,
        parent,
        program_name: str = "HM Simulator",
        version: str = "",
        comments: str = "",
        copyright: str = "",
        authors: list = None,
        website: str = "",
        license_type: str = "APACHE_2_0"
    ):
        super().__init__(
            title="About",
            transient_for=parent,
            modal=True
        )
        self.set_default_size(450, 400)

        self._program_name = program_name
        self._version = version
        self._comments = comments
        self._copyright = copyright
        self._authors = authors or []
        self._website = website
        self._license_type = license_type

        self._is_dark_mode = self._detect_dark_mode()
        self._setup_css()
        self._setup_ui()

    def _setup_ui(self):
        main_box = self.get_content_area()
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)

        name_label = Gtk.Label()
        name_label.set_markup(f"<span size='x-large' weight='bold'>{self._program_name}</span>")
        name_label.set_halign(Gtk.Align.CENTER)
        main_box.append(name_label)

        if self._version:
            version_label = Gtk.Label(label=f"Version {self._version}")
            version_label.set_halign(Gtk.Align.CENTER)
            version_label.set_margin_top(5)
            main_box.append(version_label)

        if self._comments:
            comments_label = Gtk.Label(label=self._comments)
            comments_label.set_halign(Gtk.Align.CENTER)
            comments_label.set_margin_top(10)
            comments_label.set_wrap(True)
            main_box.append(comments_label)

        if self._copyright:
            copyright_label = Gtk.Label(label=self._copyright)
            copyright_label.set_halign(Gtk.Align.CENTER)
            copyright_label.set_margin_top(15)
            main_box.append(copyright_label)

        if self._authors:
            authors_label = Gtk.Label(label="\n".join(self._authors))
            authors_label.set_halign(Gtk.Align.CENTER)
            authors_label.set_margin_top(10)
            main_box.append(authors_label)

        if self._website:
            website_label = Gtk.Label()
            website_label.set_markup(f'<a href="{self._website}">{self._website}</a>')
            website_label.set_halign(Gtk.Align.CENTER)
            website_label.set_margin_top(10)
            website_label.connect("activate-link", self._on_activate_link)
            main_box.append(website_label)

        if self._license_type:
            license_label = Gtk.Label(label=f"License: {self._license_type.replace('_', ' ')}")
            license_label.set_halign(Gtk.Align.CENTER)
            license_label.set_margin_top(10)
            main_box.append(license_label)

    def _detect_dark_mode(self) -> bool:
        try:
            settings = Gtk.Settings.get_default()
            return settings.get_property("gtk-application-prefer-dark-theme")
        except Exception:
            return False

    def _on_activate_link(self, label, uri):
        try:
            app_info = Gio.AppInfo.create_from_commandline(
                f"xdg-open {uri}",
                None,
                Gio.AppInfoCreateFlags.NONE
            )
            app_info.launch_uris([uri], None)
        except Exception:
            pass
        return True

    def _setup_css(self):
        self._css_provider = Gtk.CssProvider()
        fg = "#e0e0e0" if self._is_dark_mode else "#2c3e50"
        bg = "#2d2d2d" if self._is_dark_mode else "#fafafa"

        css_data = f"""
            .toolbar-button {{
                color: {fg};
                background-color: {bg};
                border: 1px solid @borders;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            .toolbar-button:hover {{
                background-color: @theme_selected_bg_color;
            }}
        """.encode()
        self._css_provider.load_from_data(css_data)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                self._css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
