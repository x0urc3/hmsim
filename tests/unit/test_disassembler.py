"""Unit tests for HM Disassembler."""

import pytest
from hmsim.tools.hmdas import disassemble
from hmsim.tools.hmasm import assemble


class TestDisassemblerHMv1:
    def test_load_instruction(self):
        result = disassemble(0x112C, "HMv1")
        assert result == "LOAD 0x12C"

    def test_store_instruction(self):
        result = disassemble(0x2200, "HMv1")
        assert result == "STORE 0x200"

    def test_add_instruction(self):
        result = disassemble(0x5134, "HMv1")
        assert result == "ADD 0x134"


class TestDisassemblerHMv2:
    def test_sub_instruction(self):
        result = disassemble(0x6100, "HMv2")
        assert result == "SUB 0x100"

    def test_jmp_instruction(self):
        result = disassemble(0x8640, "HMv2")
        assert result == "JMP 0x640"

    def test_jmpz_instruction(self):
        result = disassemble(0x9300, "HMv2")
        assert result == "JMPZ 0x300"

    def test_hmv2_load_instruction(self):
        result = disassemble(0x1100, "HMv2")
        assert result == "LOAD 0x100"


class TestDisassemblerRoundTrip:
    def test_round_trip_add(self):
        machine_code = assemble("ADD 300", "HMv1")
        result = disassemble(machine_code, "HMv1")
        assert result == "ADD 0x12C"

    def test_round_trip_load(self):
        machine_code = assemble("LOAD 256", "HMv1")
        result = disassemble(machine_code, "HMv1")
        assert result == "LOAD 0x100"

    def test_round_trip_store(self):
        machine_code = assemble("STORE 0x200", "HMv1")
        result = disassemble(machine_code, "HMv1")
        assert result == "STORE 0x200"

    def test_round_trip_jmp_hmv2(self):
        machine_code = assemble("JMP 256", "HMv2")
        result = disassemble(machine_code, "HMv2")
        assert result == "JMP 0x100"

    def test_round_trip_sub_hmv2(self):
        machine_code = assemble("SUB 100", "HMv2")
        result = disassemble(machine_code, "HMv2")
        assert result == "SUB 0x064"


class TestDisassemblerInvalid:
    def test_invalid_opcode(self):
        result = disassemble(0xF123, "HMv1")
        assert result == "??? 0x123"

    def test_invalid_opcode_hmv2(self):
        result = disassemble(0xC000, "HMv2")
        assert result == "??? 0x000"
