"""Unit tests for sparse JSON state format."""

import json
import os
import tempfile
import pytest
from hmsim.engine.cpu import HMv1Engine, HMEngine


class TestSparseJsonFormat:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_save_only_nonzero_memory(self, engine):
        engine._memory[0] = 0x1100
        engine._memory[1] = 0x0005
        engine._memory[100] = 0x1234
        engine.pc = 10
        engine.ac = 0xABCD

        memory = {str(addr): val for addr, val in enumerate(engine._memory) if val != 0}

        assert "0" in memory
        assert memory["0"] == 0x1100
        assert "1" in memory
        assert memory["1"] == 0x0005
        assert "100" in memory
        assert memory["100"] == 0x1234
        assert "2" not in memory
        assert "99" not in memory
        assert "101" not in memory

    def test_save_empty_memory(self, engine):
        memory = {str(addr): val for addr, val in enumerate(engine._memory) if val != 0}
        assert memory == {}

    def test_load_sparse_json(self, engine, tmp_path):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {
                "0": 0x1100,
                "256": 0x0005,
                "1024": 0xABCD
            }
        }
        f = tmp_path / "state.json"
        f.write_text(json.dumps(state))

        engine.load_state(str(f))

        assert engine._memory[0] == 0x1100
        assert engine._memory[256] == 0x0005
        assert engine._memory[1024] == 0xABCD

    def test_load_fills_zeros_for_missing(self, engine, tmp_path):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {"10": 0x1234}
        }
        f = tmp_path / "state.json"
        f.write_text(json.dumps(state))

        engine.load_state(str(f))

        assert engine._memory[0] == 0
        assert engine._memory[9] == 0
        assert engine._memory[10] == 0x1234
        assert engine._memory[11] == 0

    def test_load_invalid_address_ignored(self, engine, tmp_path):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {"65536": 0x1234, "-1": 0x5678, "100": 0xABCD}
        }
        f = tmp_path / "state.json"
        f.write_text(json.dumps(state))

        engine.load_state(str(f))

        assert engine._memory[100] == 0xABCD
        assert engine._memory[0] == 0

    def test_save_and_load_roundtrip(self, engine, tmp_path):
        engine._memory[0] = 0x1100
        engine._memory[256] = 0x0005
        engine.pc = 10
        engine.ac = 0xABCD
        engine.ir = 0x1100
        engine.sr = 0x4000

        f = tmp_path / "state.json"
        engine.save_state(str(f))

        new_engine = HMv1Engine()
        new_engine.load_state(str(f))

        assert new_engine.pc == 10
        assert new_engine.ac == 0xABCD
        assert new_engine._memory[0] == 0x1100
        assert new_engine._memory[256] == 0x0005
        assert new_engine._memory[1] == 0
