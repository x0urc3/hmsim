#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Disassembler - CLI tool to disassemble HM machine code."""

import argparse
import sys
from typing import Optional

from hmsim.engine.isa import get_mnemonic


def disassemble(machine_code: int, version: str = "HMv1") -> str:
    """Disassemble a 16-bit machine code word to mnemonic.

    Args:
        machine_code: 16-bit machine code word
        version: HM version (HMv1 or HMv2)

    Returns:
        Disassembled string in format "MNEMONIC 0xADDRESS"
    """
    opcode = (machine_code >> 12) & 0xF
    address = machine_code & 0x0FFF

    mnemonic = get_mnemonic(opcode, version)
    return f"{mnemonic} 0x{address:03X}"


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HM Disassembler - Convert machine code to mnemonics"
    )
    parser.add_argument(
        "-v", "--version",
        default="HMv1",
        choices=["HMv1", "HMv2", "HMv3", "HMv4"],
        help="HM processor version (default: HMv1)"
    )
    parser.add_argument(
        "hex_value",
        help="16-bit hex value (e.g., '0x1234' or '1234')"
    )
    args = parser.parse_args(argv)

    try:
        value_str = args.hex_value
        if value_str.startswith("0x") or value_str.startswith("0X"):
            machine_code = int(value_str, 16)
        else:
            machine_code = int(value_str, 0)

        if not 0 <= machine_code <= 0xFFFF:
            raise ValueError(f"Value out of range (0-65535): {machine_code}")

        result = disassemble(machine_code, args.version)
        print(result)
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
