#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Unit tests for HMv4 (indirect addressing)."""

import pytest
from hmsim.engine.cpu import HMEngine


class TestHMv4Engine:
    @pytest.fixture
    def engine(self):
        return HMEngine("HMv4")

    def test_indirect_load(self, engine):
        engine._memory[0x0100] = 0x0200
        engine._memory[0x0200] = 0x1234
        cycles = engine.execute(0x3, 0x0100)
        assert engine.ac == 0x1234
        assert cycles == 10

    def test_indirect_store(self, engine):
        engine.ac = 0xABCD
        engine._memory[0x0100] = 0x0200
        cycles = engine.execute(0x4, 0x0100)
        assert engine._memory[0x0200] == 0xABCD
        assert cycles == 25

    def test_indirect_load_single_level(self, engine):
        engine._memory[0x0100] = 0x0200
        engine._memory[0x0200] = 0x0300
        cycles = engine.execute(0x3, 0x0100)
        assert engine.ac == 0x0300

    def test_indirect_store_and_load(self, engine):
        engine.ac = 0x1234
        engine._memory[0x0100] = 0x0200
        engine.execute(0x4, 0x0100)
        engine._memory[0x0100] = 0x0300
        engine._memory[0x0300] = 0x5678
        result = engine.execute(0x3, 0x0100)
        assert engine.ac == 0x5678

    def test_indirect_load_with_zero_pointer(self, engine):
        engine._memory[0x0100] = 0x0000
        engine._memory[0x0000] = 0xBEEF
        cycles = engine.execute(0x3, 0x0100)
        assert engine.ac == 0xBEEF

    def test_indirect_store_with_zero_pointer(self, engine):
        engine.ac = 0xCAFE
        engine._memory[0x0100] = 0x0000
        engine.execute(0x4, 0x0100)
        assert engine._memory[0x0000] == 0xCAFE

    def test_step_indirect_load(self, engine):
        engine._memory[0x0000] = 0x3100
        engine._memory[0x0100] = 0x0200
        engine._memory[0x0200] = 0xABCD
        engine.step()
        assert engine.ac == 0xABCD
        assert engine.pc == 0x0001

    def test_step_indirect_store(self, engine):
        engine.ac = 0x1234
        engine._memory[0x0000] = 0x4100
        engine._memory[0x0100] = 0x0200
        engine.step()
        assert engine._memory[0x0200] == 0x1234
        assert engine.pc == 0x0001
