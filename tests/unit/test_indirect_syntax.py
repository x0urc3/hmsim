#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Unit tests for bracketed indirect addressing syntax."""

import pytest
from hmsim.tools.hmasm import assemble
from hmsim.tools.hmdas import disassemble
from hmsim.engine.isa import OP_LOAD, OP_STORE, OP_LOAD_INDIRECT, OP_STORE_INDIRECT

class TestIndirectSyntax:
    def test_standard_indirect_load(self):
        # LOAD (0x0100) -> 0x3100
        code = assemble("LOAD (0x0100)", "HMv4")
        assert code == (OP_LOAD_INDIRECT << 12) | 0x100
        assert disassemble(code, "HMv4") == "LOAD (0x100)"

    def test_standard_indirect_store(self):
        # STORE (0x0200) -> 0x4200
        code = assemble("STORE (0x0200)", "HMv4")
        assert code == (OP_STORE_INDIRECT << 12) | 0x200
        assert disassemble(code, "HMv4") == "STORE (0x200)"

    def test_standard_direct_load(self):
        # LOAD 0x0100 -> 0x1100
        code = assemble("LOAD 0x0100", "HMv4")
        assert code == (OP_LOAD << 12) | 0x100
        assert disassemble(code, "HMv4") == "LOAD 0x100"

    def test_whitespace_robustness(self):
        code = assemble("LOAD  ( 0x0100 ) ", "HMv4")
        assert code == (OP_LOAD_INDIRECT << 12) | 0x100

    def test_malformed_bracket_missing_close(self):
        with pytest.raises(ValueError, match="Malformed indirect address"):
            assemble("LOAD (0x0100", "HMv4")

    def test_malformed_bracket_missing_open(self):
        with pytest.raises(ValueError, match="Malformed indirect address"):
            assemble("LOAD 0x0100)", "HMv4")

    def test_empty_brackets(self):
        with pytest.raises(ValueError, match="Missing address in indirect operand"):
            assemble("LOAD ()", "HMv4")

    def test_unsupported_indirect(self):
        with pytest.raises(ValueError, match="'ADD' does not support indirect addressing"):
            assemble("ADD (0x0100)", "HMv4")

    def test_removed_mnemonics(self):
        with pytest.raises(ValueError, match="Unknown mnemonic 'LOAD_INDIRECT'"):
            assemble("LOAD_INDIRECT 0x0100", "HMv4")
        with pytest.raises(ValueError, match="Unknown mnemonic 'STORE_INDIRECT'"):
            assemble("STORE_INDIRECT 0x0100", "HMv4")
