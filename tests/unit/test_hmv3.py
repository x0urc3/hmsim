#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Unit tests for HMv3 (subroutine support)."""

import pytest
from hmsim.engine.cpu import HMEngine


class TestHMv3Engine:
    @pytest.fixture
    def engine(self):
        return HMEngine("HMv3")

    def test_call_instruction(self, engine):
        engine.pc = 0x0000
        engine._memory[0x0000] = 0xA005
        engine.step()
        assert engine.ac == 0x0001
        assert engine.pc == 0x0005

    def test_call_cycles(self, engine):
        engine.pc = 0x0000
        engine._memory[0x0000] = 0xA005
        cycles = engine.step()
        assert cycles == 5

    def test_return_instruction(self, engine):
        engine.ac = 0x0010
        engine.pc = 0x0005
        engine._memory[0x0005] = 0xB000
        engine.step()
        assert engine.pc == 0x0010

    def test_return_cycles(self, engine):
        engine.ac = 0x0010
        engine.pc = 0x0005
        engine._memory[0x0005] = 0xB000
        cycles = engine.step()
        assert cycles == 1

    def test_call_return_subroutine(self, engine):
        engine._memory[0x0000] = 0xA005
        engine._memory[0x0001] = 0x0000
        engine._memory[0x0005] = 0xB000
        engine.step()
        assert engine.pc == 0x0005
        assert engine.ac == 0x0001
        engine.step()
        assert engine.pc == 0x0001

    def test_manual_save_and_restore(self, engine):
        engine._memory[0x0000] = 0xA005
        engine._memory[0x0001] = 0x0000
        engine._memory[0x0005] = 0x2100
        engine._memory[0x0006] = 0x1100
        engine._memory[0x0007] = 0xB000
        engine._memory[0x0100] = 0x0000

        engine.step()
        assert engine.pc == 0x0005
        assert engine.ac == 0x0001

        engine.step()
        assert engine._memory[0x0100] == 0x0001

        engine.step()
        assert engine.ac == 0x0001

        engine.step()
        assert engine.pc == 0x0001
