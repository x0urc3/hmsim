"""Unit tests for HM CLI Report formatting."""

import io
from contextlib import redirect_stdout
from hmsim.engine.cpu import HMEngine
from hmsim.tools.hmsim_cli import print_report


def test_print_report_formatting():
    """Verify that print_report correctly formats registers and memory in hex."""
    engine = HMEngine("HMv1")
    engine.pc = 0x123
    engine.ac = 0xABC
    engine.ir = 0x5005
    engine.sr = 0x4000
    engine.total_cycles = 42
    engine._memory[0x10] = 0x1
    engine._memory[0xFF] = 0xFFFF

    f = io.StringIO()
    with redirect_stdout(f):
        print_report(engine)

    output = f.getvalue()

    # Check registers
    assert "PC (Program Counter): 0x0123" in output
    assert "AC (Accumulator):     0x0ABC" in output
    assert "IR (Instr Register):  0x5005" in output
    assert "SR (Status Register): 0x4000" in output

    # Check statistics
    assert "Total Cycles: 42" in output

    # Check memory
    assert "0x0010: 0x0001" in output
    assert "0x00FF: 0xFFFF" in output

    # Check that zero-memory is NOT printed (address 0x0 is zero by default)
    assert "0x0000: 0x0000" not in output


def test_print_report_empty_memory():
    """Verify report handles all-zero memory correctly."""
    engine = HMEngine("HMv1")
    f = io.StringIO()
    with redirect_stdout(f):
        print_report(engine)

    output = f.getvalue()
    assert "(All memory is zero)" in output
