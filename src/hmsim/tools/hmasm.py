#!/usr/bin/env python3
"""HM Assembler - CLI tool to assemble HM instructions."""

import sys
from typing import Optional

from hmsim.engine.isa import HMV1_ISA


def assemble(instruction: str) -> int:
    """Assemble an instruction string into machine code.

    Args:
        instruction: String like "LOAD 100", "STORE 0x200", "ADD 0b1010"

    Returns:
        16-bit machine code word.

    Raises:
        ValueError: If instruction format is invalid.
    """
    parts = instruction.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid instruction format: {instruction}")

    mnemonic = parts[0].upper()
    address_str = parts[1]

    if mnemonic not in HMV1_ISA:
        raise ValueError(f"Unknown mnemonic: {mnemonic}")

    opcode = HMV1_ISA[mnemonic][0]
    address = int(address_str, 0)

    if not 0 <= address <= 0xFFF:
        raise ValueError(f"Address out of range (0-4095): {address}")

    return (opcode << 12) | (address & 0x0FFF)


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    argv = argv or sys.argv[1:]

    if not argv:
        print("Usage: hmasm <instruction>", file=sys.stderr)
        print("Example: hmasm 'LOAD 100'", file=sys.stderr)
        return 1

    instruction = " ".join(argv)
    try:
        result = assemble(instruction)
        print(f"0x{result:04X}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
