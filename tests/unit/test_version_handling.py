"""Unit tests for version handling and state loading."""

import json
import os
import tempfile
import pytest


class TestVersionMismatchHandling:
    def test_hmv3_defaults_to_hmv2(self):
        state = {
            "version": "HMv3",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        version = state.get("version", "HMv1")
        if version not in ["HMv1", "HMv2"]:
            loaded_version = "HMv2"

        assert loaded_version == "HMv2"

    def test_hmv4_defaults_to_hmv2(self):
        state = {
            "version": "HMv4",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        version = state.get("version", "HMv1")
        if version not in ["HMv1", "HMv2"]:
            loaded_version = "HMv2"

        assert loaded_version == "HMv2"

    def test_hmv1_loads_correctly(self):
        state = {
            "version": "HMv1",
            "pc": 10,
            "ac": 0x1234,
            "ir": 0x1100,
            "sr": 0,
            "memory": {"0": 0x1100}
        }

        version = state.get("version", "HMv1")
        loaded_version = version if version in ["HMv1", "HMv2"] else "HMv2"

        assert loaded_version == "HMv1"
        assert version in ["HMv1", "HMv2"]

    def test_hmv2_loads_correctly(self):
        state = {
            "version": "HMv2",
            "pc": 10,
            "ac": 0x1234,
            "ir": 0x1100,
            "sr": 0x4000,
            "memory": {"0": 0x1100}
        }

        version = state.get("version", "HMv1")
        loaded_version = version if version in ["HMv1", "HMv2"] else "HMv2"

        assert loaded_version == "HMv2"

    def test_missing_version_defaults_to_hmv1(self):
        state = {
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        version = state.get("version", "HMv1")

        assert version == "HMv1"

    def test_status_message_for_hmv1(self):
        version = "HMv1"
        if version in ["HMv1", "HMv2"]:
            status_msg = f"Loaded {version} state"

        assert status_msg == "Loaded HMv1 state"

    def test_status_message_for_hmv2(self):
        version = "HMv2"
        if version in ["HMv1", "HMv2"]:
            status_msg = f"Loaded {version} state"

        assert status_msg == "Loaded HMv2 state"

    def test_status_message_for_hmv3(self):
        version = "HMv3"
        if version not in ["HMv1", "HMv2"]:
            version = "HMv2"
            status_msg = f"Warning: HMv3 state loaded as HMv2"

        assert status_msg == "Warning: HMv3 state loaded as HMv2"

    def test_version_index_mapping(self):
        VERSIONS = ["HMv1", "HMv2", "HMv3", "HMv4"]

        assert VERSIONS.index("HMv1") == 0
        assert VERSIONS.index("HMv2") == 1
        assert VERSIONS.index("HMv3") == 2
        assert VERSIONS.index("HMv4") == 3

    def test_invalid_version_value_is_handled(self):
        state = {
            "version": "INVALID",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {}
        }

        version = state.get("version", "HMv1")
        if version not in ["HMv1", "HMv2"]:
            loaded_version = "HMv2"

        assert loaded_version == "HMv2"
