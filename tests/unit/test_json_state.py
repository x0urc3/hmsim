#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Unit tests for HM state file format with text and data sections."""

import json
import tempfile
import pytest
from hmsim.engine.cpu import HMEngine
from hmsim.engine.state import save_state_to_dict, load_state_from_dict


class TestHMStateFormat:
    @pytest.fixture
    def engine(self):
        return HMEngine("HMv1")

    def test_save_produces_text_and_data_sections(self, engine):
        engine._memory[0] = 0x1100
        engine._memory[1] = 0x5100
        engine._memory[2] = 0x2100
        engine._memory[0x100] = 0x0005
        engine._memory[0x101] = 0x0007
        engine.pc = 10
        engine.ac = 0xABCD

        state = save_state_to_dict(engine)

        assert "text" in state
        assert "data" in state
        assert state["text"]["0x0000"] == "LOAD 0x100"
        assert state["text"]["0x0001"] == "ADD 0x100"
        assert state["text"]["0x0002"] == "STORE 0x100"
        assert state["data"]["0x0101"] == "0x0007"

    def test_save_empty_memory(self, engine):
        state = save_state_to_dict(engine)
        assert state["text"] == {}
        assert state["data"] == {}

    def test_load_text_section_assembles_instructions(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {
                "0x0000": "LOAD 0x100",
                "0x0001": "ADD 0x101"
            },
            "data": {}
        }
        load_state_from_dict(engine, state)

        assert engine._memory[0] == 0x1100
        assert engine._memory[1] == 0x5101

    def test_load_data_section_populates_memory(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {},
            "data": {
                "0x0010": "0x0005",
                "0x0011": "0x0007"
            }
        }
        load_state_from_dict(engine, state)

        assert engine._memory[0x10] == 0x0005
        assert engine._memory[0x11] == 0x0007

    def test_load_with_both_text_and_data(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {
                "0x0000": "LOAD 0x100",
                "0x0001": "ADD 0x101",
                "0x0002": "STORE 0x102"
            },
            "data": {
                "0x0100": "0x0005",
                "0x0101": "0x0007"
            }
        }
        load_state_from_dict(engine, state)

        assert engine._memory[0] == 0x1100
        assert engine._memory[1] == 0x5101
        assert engine._memory[2] == 0x2102
        assert engine._memory[0x100] == 0x0005
        assert engine._memory[0x101] == 0x0007

    def test_save_and_load_roundtrip(self, tmp_path):
        engine = HMEngine("HMv1")
        engine._memory[0] = 0x1100
        engine._memory[1] = 0x5100
        engine._memory[2] = 0x2100
        engine._memory[0x101] = 0x0007
        engine._memory[0x102] = 0x0005
        engine.pc = 10
        engine.ac = 0xABCD
        engine.ir = 0x1100
        engine.sr = 0x4000

        f = tmp_path / "state.hm"
        engine.save_state(str(f))

        new_engine = HMEngine("HMv1")
        new_engine.load_state(str(f))

        assert new_engine.pc == 10
        assert new_engine.ac == 0xABCD
        assert new_engine._memory[0] == 0x1100
        assert new_engine._memory[1] == 0x5100
        assert new_engine._memory[2] == 0x2100
        assert new_engine._memory[0x101] == 0x0007
        assert new_engine._memory[0x102] == 0x0005
        assert new_engine._memory[3] == 0

        assert "setup" in save_state_to_dict(new_engine)
        assert save_state_to_dict(new_engine)["setup"]["text"] == [0, 256]
        assert save_state_to_dict(new_engine)["setup"]["data"] == [257, 65535]

    def test_linear_disassembly_stops_at_data(self, engine):
        engine._memory[0] = 0x1100
        engine._memory[1] = 0x1101
        engine._memory[2] = 0x1102
        engine._memory[0x100] = 0x0005
        engine._memory[0x101] = 0x0006

        state = save_state_to_dict(engine)

        assert "0x0000" in state["text"]
        assert "0x0001" in state["text"]
        assert "0x0002" in state["text"]
        assert "0x0101" in state["data"]

    def test_load_invalid_assembly_ignored(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {
                "0x0000": "INVALID 0x010"
            },
            "data": {}
        }
        load_state_from_dict(engine, state)
        assert engine._memory[0] == 0

    def test_load_invalid_data_ignored(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {},
            "data": {
                "0x0100": "0x1234",
                "0x10000": "0x5678",
                "not_a_number": "0xABCD"
            }
        }
        load_state_from_dict(engine, state)
        assert engine._memory[0x0100] == 0x1234

    def test_load_registers_from_state(self, engine):
        state = {
            "version": "HMv1",
            "pc": 100,
            "ac": 0x1234,
            "ir": 0x5678,
            "sr": 0x4000,
            "text": {},
            "data": {}
        }
        load_state_from_dict(engine, state)

        assert engine.pc == 100
        assert engine.ac == 0x1234
        assert engine.ir == 0x5678
        assert engine.sr == 0x4000

    def test_load_default_values(self, engine):
        state = {
            "version": "HMv1",
            "text": {},
            "data": {}
        }
        load_state_from_dict(engine, state)

        assert engine.pc == 0
        assert engine.ac == 0
        assert engine.ir == 0
        assert engine.sr == 0

    def test_load_setup_with_hex_notation(self, engine):
        state = {
            "version": "HMv1",
            "setup": {
                "text": ["0x0", "0x3"],
                "data": ["0x4", "0xffff"]
            },
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {},
            "data": {}
        }
        load_state_from_dict(engine, state)

        assert engine.text_region == (0, 3)
        assert engine.data_region == (4, 0xFFFF)

    def test_load_setup_with_mixed_notation(self, engine):
        state = {
            "version": "HMv1",
            "setup": {
                "text": ["0x0", 256],
                "data": [257, "0xffff"]
            },
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "text": {},
            "data": {}
        }
        load_state_from_dict(engine, state)

        assert engine.text_region == (0, 256)
        assert engine.data_region == (257, 0xFFFF)


class TestSchemaValidation:
    @pytest.fixture
    def engine(self):
        return HMEngine("HMv1")

    def test_valid_state_passes_validation(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0x1234,
            "ir": 0,
            "text": {},
            "data": {}
        }
        load_state_from_dict(engine, state)
        assert engine.ac == 0x1234

    def test_invalid_ac_out_of_range(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 70000,
            "ir": 0,
            "text": {},
            "data": {}
        }
        with pytest.raises(ValueError, match="Schema validation failed"):
            load_state_from_dict(engine, state)

    def test_invalid_malformed_hex_address_ignored_during_load(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "text": {
                "0xGGGG": "LOAD 0x100",
                "0x0000": "LOAD 0x100"
            },
            "data": {}
        }
        load_state_from_dict(engine, state)
        assert engine._memory[0] == 0x1100
        assert engine._memory[0xFFFF] == 0

    def test_invalid_malformed_data_value_ignored_during_load(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "text": {},
            "data": {
                "0x0100": "GGGG",
                "0x0101": "0x1234"
            }
        }
        load_state_from_dict(engine, state)
        assert engine._memory[0x0101] == 0x1234
        assert engine._memory[0x0100] == 0

    def test_missing_required_field_version(self, engine):
        state = {
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "text": {},
            "data": {}
        }
        with pytest.raises(ValueError, match="Schema validation failed"):
            load_state_from_dict(engine, state)

    def test_invalid_version(self, engine):
        state = {
            "version": "HMv5",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "text": {},
            "data": {}
        }
        with pytest.raises(ValueError, match="Schema validation failed"):
            load_state_from_dict(engine, state)

    def test_hmv2_requires_sr(self, engine):
        state = {
            "version": "HMv2",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "text": {},
            "data": {}
        }
        with pytest.raises(ValueError, match="Schema validation failed"):
            load_state_from_dict(engine, state)

    def test_hmv2_with_sr_passes(self, engine):
        state = {
            "version": "HMv2",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0x4000,
            "text": {},
            "data": {}
        }
        load_state_from_dict(engine, state)
        assert engine.sr == 0x4000

    def test_invalid_address_out_of_range_ignored_during_load(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "text": {
                "0x10000": "LOAD 0x100",
                "0x0000": "LOAD 0x100"
            },
            "data": {}
        }
        load_state_from_dict(engine, state)
        assert engine._memory[0] == 0x1100
