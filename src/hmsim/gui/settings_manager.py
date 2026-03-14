#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Settings manager for persistent application settings."""

import json
import os
from pathlib import Path
from typing import Optional


class SettingsManager:
    _instance: Optional['SettingsManager'] = None

    def __init__(self):
        self._config_dir = self._get_config_dir()
        self._settings_file = self._config_dir / "settings.json"
        self._settings: dict = {}
        self._load_settings()

    @classmethod
    def get_instance(cls) -> 'SettingsManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_config_dir(self) -> Path:
        if os.name == 'nt':
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif os.name == 'posix':
            if 'XDG_CONFIG_HOME' in os.environ:
                base = Path(os.environ['XDG_CONFIG_HOME'])
            else:
                base = Path.home() / '.config'
        else:
            base = Path.home()

        config_dir = base / "hmsim"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _load_settings(self):
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r') as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._settings = {}
        else:
            self._settings = {}

        self._settings.setdefault('theme', 'system')

    def _save_settings(self):
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except IOError:
            pass

    def get_theme(self) -> str:
        return self._settings.get('theme', 'system')

    def set_theme(self, theme: str):
        if theme not in ('light', 'dark', 'system'):
            theme = 'system'
        self._settings['theme'] = theme
        self._save_settings()

    def get(self, key: str, default=None):
        return self._settings.get(key, default)

    def set(self, key: str, value):
        self._settings[key] = value
        self._save_settings()
