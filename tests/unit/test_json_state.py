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

    def test_load_sparse_json(self, engine):
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

        memory = state.get("memory", {})
        for addr_str, val in memory.items():
            addr = int(addr_str)
            if 0 <= addr < 65536:
                engine._memory[addr] = val & 0xFFFF

        assert engine._memory[0] == 0x1100
        assert engine._memory[256] == 0x0005
        assert engine._memory[1024] == 0xABCD

    def test_load_fills_zeros_for_missing(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {"10": 0x1234}
        }

        memory = state.get("memory", {})
        for addr_str, val in memory.items():
            addr = int(addr_str)
            if 0 <= addr < 65536:
                engine._memory[addr] = val & 0xFFFF

        assert engine._memory[0] == 0
        assert engine._memory[9] == 0
        assert engine._memory[10] == 0x1234
        assert engine._memory[11] == 0

    def test_load_invalid_address_ignored(self, engine):
        state = {
            "version": "HMv1",
            "pc": 0,
            "ac": 0,
            "ir": 0,
            "sr": 0,
            "memory": {"65536": 0x1234, "-1": 0x5678, "100": 0xABCD}
        }

        memory = state.get("memory", {})
        for addr_str, val in memory.items():
            addr = int(addr_str)
            if 0 <= addr < 65536:
                engine._memory[addr] = val & 0xFFFF

        assert engine._memory[100] == 0xABCD
        assert engine._memory[0] == 0

    def test_save_and_load_roundtrip(self, engine):
        engine._memory[0] = 0x1100
        engine._memory[256] = 0x0005
        engine.pc = 10
        engine.ac = 0xABCD
        engine.ir = 0x1100
        engine.sr = 0x4000

        state = {
            "version": engine.version,
            "pc": engine.pc,
            "ac": engine.ac,
            "ir": engine.ir,
            "sr": engine.sr,
            "memory": {str(addr): val for addr, val in enumerate(engine._memory) if val != 0}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(state, f)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                loaded_state = json.load(f)

            new_engine = HMv1Engine()
            new_engine.pc = loaded_state.get("pc", 0)
            new_engine.ac = loaded_state.get("ac", 0)
            new_engine.ir = loaded_state.get("ir", 0)
            new_engine.sr = loaded_state.get("sr", 0)

            memory = loaded_state.get("memory", {})
            for addr_str, val in memory.items():
                addr = int(addr_str)
                if 0 <= addr < 65536:
                    new_engine._memory[addr] = val & 0xFFFF

            assert new_engine.pc == 10
            assert new_engine.ac == 0xABCD
            assert new_engine._memory[0] == 0x1100
            assert new_engine._memory[256] == 0x0005
            assert new_engine._memory[1] == 0
        finally:
            os.unlink(temp_path)
