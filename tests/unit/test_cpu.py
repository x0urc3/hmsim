"""Unit tests for HM CPU Engine."""

import pytest
from hmsim.engine.cpu import HMv1Engine, HMEngine


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


class TestHMv2Engine:
    @pytest.fixture
    def engine(self):
        return HMEngine("HMv2")

    def test_sub_instruction(self, engine):
        engine.ac = 0x0005
        engine._memory[0x0100] = 0x0002
        cycles = engine.execute(0x6, 0x0100)
        assert engine.ac == 0x0003
        assert cycles == 10

    def test_jmp_instruction(self, engine):
        cycles = engine.execute(0x8, 0x0200)
        assert engine.pc == 0x0200
        assert cycles == 5

    def test_jmpz_when_zero(self, engine):
        engine.sr = 0x4000
        old_pc = 0x0001
        engine.pc = old_pc
        cycles = engine.execute(0x9, 0x0300)
        assert engine.pc == 0x0300
        assert cycles == 5

    def test_jmpz_when_nonzero(self, engine):
        engine.sr = 0x0000
        old_pc = 0x0001
        engine.pc = old_pc
        cycles = engine.execute(0x9, 0x0300)
        assert engine.pc == old_pc
        assert cycles == 5

    def test_version_rejects_v1_instructions(self, engine):
        with pytest.raises(ValueError) as exc_info:
            engine.execute(0xA, 0x0100)
        assert "Unknown opcode" in str(exc_info.value)

    def test_status_register_zero_flag(self, engine):
        engine.ac = 0x0001
        engine._memory[0x0100] = 0x0001
        engine.execute(0x6, 0x0100)
        assert engine.sr & 0x4000

    def test_status_register_sign_flag(self, engine):
        engine.ac = 0x0001
        engine._memory[0x0100] = 0x8000
        engine.execute(0x6, 0x0100)
        assert engine.sr & 0x8000


class TestVersionSupport:
    def test_hmv1_only_supports_base_instructions(self):
        engine = HMv1Engine()
        engine.execute(0x1, 0x0100)
        engine.execute(0x2, 0x0100)
        engine.execute(0x5, 0x0100)
        with pytest.raises(ValueError):
            engine.execute(0x6, 0x0100)

    def test_invalid_version(self):
        with pytest.raises(ValueError) as exc_info:
            HMEngine("HMv3")
        assert "Invalid version" in str(exc_info.value)
