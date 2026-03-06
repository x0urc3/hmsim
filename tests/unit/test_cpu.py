"""Unit tests for HMv1 CPU Engine."""

import pytest
from hmsim.engine.cpu import HMv1Engine


class TestHMv1Engine:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_load_instruction(self, engine):
        engine._memory[0x0100] = 0x1234
        cycles = engine.execute(0x1, 0x0100)
        assert engine.ac == 0x1234
        assert cycles == 5

    def test_store_instruction(self, engine):
        engine.ac = 0xABCD
        cycles = engine.execute(0x2, 0x0200)
        assert engine._memory[0x0200] == 0xABCD
        assert cycles == 15

    def test_add_instruction(self, engine):
        engine.ac = 0x0001
        engine._memory[0x0300] = 0x0002
        cycles = engine.execute(0x5, 0x0300)
        assert engine.ac == 0x0003
        assert cycles == 10

    def test_invalid_opcode(self, engine):
        with pytest.raises(ValueError) as exc_info:
            engine.execute(0xF, 0x0000)
        assert "Unknown opcode" in str(exc_info.value)

    def test_decode(self, engine):
        opcode, address = engine.decode(0x1234)
        assert opcode == 0x1
        assert address == 0x234

    def test_step_increments_pc(self, engine):
        engine._memory[0x0000] = 0x1100
        engine.step()
        assert engine.pc == 0x0001
