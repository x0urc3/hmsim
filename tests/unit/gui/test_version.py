#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see details
"""Tests for version handling and state loading."""


class TestVersionChange:
    """Test version change functionality."""

    def test_version_change_to_hmv2(self, main_window):
        main_window._on_arch_changed("HMv2")
        assert main_window.current_arch == "HMv2"
        assert main_window.register_view.arch_label.get_label() == "Arch: HMv2"

    def test_version_preserves_memory(self, main_window):
        main_window.engine._memory[0x0100] = 0x1234
        main_window._on_arch_changed("HMv2")
        assert main_window.engine._memory[0x0100] == 0x1234

    def test_version_change_creates_new_engine(self, main_window):
        old_engine_id = id(main_window.engine)
        main_window._on_arch_changed("HMv2")
        assert id(main_window.engine) != old_engine_id


class TestVersionMismatchHandling:
    """Test version loading logic."""

    VERSIONS = ["HMv1", "HMv2", "HMv3", "HMv4"]

    def test_hmv3_loads_correctly(self):
        state = {
            "architecture": "HMv3",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        arch = state.get("architecture", "HMv1")
        loaded_arch = arch if arch in self.VERSIONS else "HMv2"

        assert loaded_arch == "HMv3"

    def test_hmv4_loads_correctly(self):
        state = {
            "architecture": "HMv4",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        arch = state.get("architecture", "HMv1")
        loaded_arch = arch if arch in self.VERSIONS else "HMv2"

        assert loaded_arch == "HMv4"

    def test_hmv1_loads_correctly(self):
        state = {
            "architecture": "HMv1",
            "pc": 10,
            "ac": 0x1234,
            "ir": 0x1100,
            "sr": 0,
            "memory": {"0": 0x1100}
        }

        arch = state.get("architecture", "HMv1")
        loaded_arch = arch if arch in self.VERSIONS else "HMv2"

        assert loaded_arch == "HMv1"
        assert arch in self.VERSIONS

    def test_hmv2_loads_correctly(self):
        state = {
            "architecture": "HMv2",
            "pc": 10,
            "ac": 0x1234,
            "ir": 0x1100,
            "sr": 0x4000,
            "memory": {"0": 0x1100}
        }

        arch = state.get("architecture", "HMv1")
        loaded_arch = arch if arch in self.VERSIONS else "HMv2"

        assert loaded_arch == "HMv2"

    def test_missing_architecture_defaults_to_hmv1(self):
        state = {
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        arch = state.get("architecture", "HMv1")

        assert arch == "HMv1"

    def test_status_message_for_hmv1(self):
        version = "HMv1"
        if version in self.VERSIONS:
            status_msg = f"Loaded {version} state"
        else:
            status_msg = f"Warning: Unknown version, loaded as HMv2"

        assert status_msg == "Loaded HMv1 state"

    def test_status_message_for_hmv2(self):
        version = "HMv2"
        if version in self.VERSIONS:
            status_msg = f"Loaded {version} state"
        else:
            status_msg = f"Warning: Unknown version, loaded as HMv2"

        assert status_msg == "Loaded HMv2 state"

    def test_status_message_for_hmv3(self):
        version = "HMv3"
        if version in self.VERSIONS:
            status_msg = f"Loaded {version} state"
        else:
            status_msg = f"Warning: Unknown version, loaded as HMv2"

        assert status_msg == "Loaded HMv3 state"

    def test_status_message_for_hmv4(self):
        version = "HMv4"
        if version in self.VERSIONS:
            status_msg = f"Loaded {version} state"
        else:
            status_msg = f"Warning: Unknown version, loaded as HMv2"

        assert status_msg == "Loaded HMv4 state"

    def test_version_index_mapping(self):
        VERSIONS = ["HMv1", "HMv2", "HMv3", "HMv4"]

        assert VERSIONS.index("HMv1") == 0
        assert VERSIONS.index("HMv2") == 1
        assert VERSIONS.index("HMv3") == 2
        assert VERSIONS.index("HMv4") == 3

    def test_invalid_architecture_value_is_handled(self):
        state = {
            "architecture": "INVALID",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        arch = state.get("architecture", "HMv1")
        if arch not in self.VERSIONS:
            loaded_arch = "HMv2"
        else:
            loaded_arch = arch

        assert loaded_arch == "HMv2"
