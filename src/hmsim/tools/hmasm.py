#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Assembler - CLI tool to assemble HM instructions."""

import argparse
import sys
from typing import Optional

from hmsim.engine.isa import VERSION_ISA, OP_LOAD_INDIRECT, OP_STORE_INDIRECT

ZERO_OPERAND_MNEMONICS = {
    "HMv1": set(),
    "HMv2": set(),
    "HMv3": {"RETURN"},
    "HMv4": {"RETURN"},
}

INDIRECT_MNEMONICS = {"LOAD", "STORE"}

REMOVED_MNEMONICS = {"LOAD_INDIRECT", "STORE_INDIRECT"}


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
    parts = code.split(maxsplit=1)
    if len(parts) == 0:
        raise ValueError(f"Invalid instruction format: {instruction}")
    if len(parts) == 1:
        mnemonic = parts[0].upper()
        isa = VERSION_ISA[version]
        if mnemonic not in isa:
            raise ValueError(f"Unknown mnemonic '{mnemonic}' for {version}")
        if mnemonic not in ZERO_OPERAND_MNEMONICS[version]:
            raise ValueError(f"Invalid instruction format: {instruction}")
        opcode = isa[mnemonic][0]
        return opcode << 12

    mnemonic = parts[0].upper()
    address_str = parts[1].strip()

    if mnemonic in REMOVED_MNEMONICS:
        raise ValueError(
            f"Unknown mnemonic '{mnemonic}' for {version}. "
            f"Use 'LOAD (address)' or 'STORE (address)' for indirect addressing."
        )

    isa = VERSION_ISA[version]
    if mnemonic not in isa:
        raise ValueError(f"Unknown mnemonic '{mnemonic}' for {version}")

    if mnemonic in ZERO_OPERAND_MNEMONICS[version]:
        opcode = isa[mnemonic][0]
        return opcode << 12

    is_indirect = False
    if address_str.startswith("(") and address_str.endswith(")"):
        is_indirect = True
        inner = address_str[1:-1].strip()
        if not inner:
            raise ValueError("Missing address in indirect operand")
        address_str = inner
    elif "(" in address_str or ")" in address_str:
        raise ValueError("Malformed indirect address")

    if is_indirect:
        if mnemonic not in INDIRECT_MNEMONICS:
            raise ValueError(f"'{mnemonic}' does not support indirect addressing")
        if mnemonic == "LOAD":
            opcode = OP_LOAD_INDIRECT
        else:
            opcode = OP_STORE_INDIRECT
    else:
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
        choices=["HMv1", "HMv2", "HMv3", "HMv4"],
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
