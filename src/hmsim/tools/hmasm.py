#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Assembler - CLI tool to assemble HM instructions."""

import argparse
import sys
from typing import Optional

from hmsim.engine.isa import VERSION_ISA


def assemble(instruction: str, version: str = "HMv1") -> int:
    """Assemble an instruction string into machine code.

    Args:
        instruction: String like "LOAD 100", "STORE 0x200", "ADD 0b1010"
        version: HM version (HMv1 or HMv2)

    Returns:
        16-bit machine code word.

    Raises:
        ValueError: If instruction format is invalid.
    """
    code = instruction.split(';', 1)[0].strip()
    parts = code.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid instruction format: {instruction}")

    mnemonic = parts[0].upper()
    address_str = parts[1]

    isa = VERSION_ISA[version]
    if mnemonic not in isa:
        raise ValueError(f"Unknown mnemonic '{mnemonic}' for {version}")

    opcode = isa[mnemonic][0]
    address = int(address_str, 0)

    if not 0 <= address <= 0xFFF:
        raise ValueError(f"Address out of range (0-4095): {address}")

    return (opcode << 12) | (address & 0x0FFF)


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HM Assembler - Convert mnemonics to machine code"
    )
    parser.add_argument(
        "-v", "--version",
        default="HMv1",
        choices=["HMv1", "HMv2"],
        help="HM processor version (default: HMv1)"
    )
    parser.add_argument(
        "instruction",
        nargs="?",
        help="Instruction to assemble (e.g., 'LOAD 100')"
    )
    args = parser.parse_args(argv)

    if not args.instruction:
        print("Usage: hmasm [-v HMv1|HMv2] <instruction>", file=sys.stderr)
        print("Example: hmasm -v HMv2 'SUB 100'", file=sys.stderr)
        return 1

    try:
        result = assemble(args.instruction, args.version)
        print(f"0x{result:04X}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
