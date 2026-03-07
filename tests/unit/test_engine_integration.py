"""Unit tests for Step 4.4 - Engine Integration (Observer Pattern, Memory Access, Reset)."""

import pytest
from hmsim.engine.cpu import HMEngine, HMv1Engine


class TestObserverPattern:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_register_observer(self, engine):
        callback_called = []
        def callback():
            callback_called.append(True)
        engine.register_observer(callback)
        assert callback in engine._observers

    def test_notify_observers_calls_callback(self, engine):
        call_count = [0]
        def callback():
            call_count[0] += 1
        engine.register_observer(callback)
        engine._notify_observers()
        assert call_count[0] == 1

    def test_multiple_observers(self, engine):
        call_count = [0, 0]
        def callback1():
            call_count[0] += 1
        def callback2():
            call_count[1] += 1
        engine.register_observer(callback1)
        engine.register_observer(callback2)
        engine._notify_observers()
        assert call_count[0] == 1
        assert call_count[1] == 1

    def test_observer_called_on_step(self, engine):
        call_count = [0]
        def callback():
            call_count[0] += 1
        engine.register_observer(callback)
        engine._memory[0] = 0x1100
        engine.step()
        assert call_count[0] == 1

    def test_observer_called_on_reset(self, engine):
        call_count = [0]
        def callback():
            call_count[0] += 1
        engine.register_observer(callback)
        engine.reset()
        assert call_count[0] == 1


class TestMemoryAccess:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_write_memory(self, engine):
        engine.write_memory(0x0100, 0xABCD)
        assert engine._memory[0x0100] == 0xABCD

    def test_write_memory_masks_to_16bit(self, engine):
        engine.write_memory(0x0100, 0x1ABCD)
        assert engine._memory[0x0100] == 0xABCD

    def test_write_memory_ignores_invalid_address_high(self, engine):
        original_value = engine._memory[0]
        engine.write_memory(0x10000, 0xABCD)
        assert engine._memory[0] == original_value

    def test_write_memory_ignores_invalid_address_negative(self, engine):
        engine.write_memory(-1, 0xABCD)
        assert engine._memory[0] == 0

    def test_read_memory(self, engine):
        engine._memory[0x0100] = 0xABCD
        value = engine.read_memory(0x0100)
        assert value == 0xABCD

    def test_read_memory_returns_zero_for_invalid(self):
        engine = HMv1Engine()
        value = engine.read_memory(0x10000)
        assert value == 0

    def test_write_memory_notifies_observer(self, engine):
        call_count = [0]
        def callback():
            call_count[0] += 1
        engine.register_observer(callback)
        engine.write_memory(0x0100, 0xABCD)
        assert call_count[0] == 1


class TestReset:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_reset_clears_registers(self, engine):
        engine.pc = 0x1234
        engine.ac = 0xABCD
        engine.ir = 0x1111
        engine.sr = 0x8000
        engine.reset()
        assert engine.pc == 0x0000
        assert engine.ac == 0x0000
        assert engine.ir == 0x0000
        assert engine.sr == 0x0000

    def test_reset_preserves_memory(self, engine):
        engine._memory[0x0100] = 0xABCD
        engine._memory[0x0200] = 0x1234
        engine.reset()
        assert engine._memory[0x0100] == 0xABCD
        assert engine._memory[0x0200] == 0x1234

    def test_reset_clears_statistics(self, engine):
        engine.total_cycles = 9999
        engine.total_instructions = 500
        engine.reset()
        assert engine.total_cycles == 0
        assert engine.total_instructions == 0

    def test_reset_notifies_observer(self, engine):
        call_count = [0]
        def callback():
            call_count[0] += 1
        engine.register_observer(callback)
        engine.reset()
        assert call_count[0] == 1


class TestIRUpdate:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_step_sets_ir(self, engine):
        engine._memory[0] = 0x1234
        engine.step()
        assert engine.ir == 0x1234
