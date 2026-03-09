#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Instruction Set Architecture definitions.

This module serves as the single source of truth for the HM processor
instruction set. It defines opcodes, mnemonics, and cycle counts for
each processor version.
"""

from typing import Dict, Tuple

OP_LOAD = 0x1
OP_STORE = 0x2
OP_LOAD_INDIRECT = 0x3
OP_STORE_INDIRECT = 0x4
OP_ADD = 0x5
OP_SUB = 0x6
OP_JMP = 0x8
OP_JMPZ = 0x9
OP_CALL = 0xA
OP_RETURN = 0xB

HMV1_ISA: Dict[str, Tuple[int, int]] = {
    "LOAD": (OP_LOAD, 5),
    "STORE": (OP_STORE, 15),
    "ADD": (OP_ADD, 10),
}

HMV2_ISA: Dict[str, Tuple[int, int]] = {
    **HMV1_ISA,
    "SUB": (OP_SUB, 10),
    "JMP": (OP_JMP, 5),
    "JMPZ": (OP_JMPZ, 5),
}

HMV3_ISA: Dict[str, Tuple[int, int]] = {
    **HMV2_ISA,
    "CALL": (OP_CALL, 5),
    "RETURN": (OP_RETURN, 1),
}

HMV4_ISA: Dict[str, Tuple[int, int]] = {
    **HMV3_ISA,
    "LOAD": (OP_LOAD, 5),
    "STORE": (OP_STORE, 15),
}

VERSION_ISA = {
    "HMv1": HMV1_ISA,
    "HMv2": HMV2_ISA,
    "HMv3": HMV3_ISA,
    "HMv4": HMV4_ISA,
}

HMV1_OPCODE_TO_MNEMONIC = {v[0]: k for k, v in HMV1_ISA.items()}

HMV2_OPCODE_TO_MNEMONIC = {v[0]: k for k, v in HMV2_ISA.items()}

HMV3_OPCODE_TO_MNEMONIC = {v[0]: k for k, v in HMV3_ISA.items()}

HMV4_OPCODE_TO_MNEMONIC = {v[0]: k for k, v in HMV4_ISA.items()}

VERSION_OPCODE_MAP = {
    "HMv1": HMV1_OPCODE_TO_MNEMONIC,
    "HMv2": HMV2_OPCODE_TO_MNEMONIC,
    "HMv3": HMV3_OPCODE_TO_MNEMONIC,
    "HMv4": {
        **HMV4_OPCODE_TO_MNEMONIC,
        OP_LOAD_INDIRECT: "LOAD",
        OP_STORE_INDIRECT: "STORE",
    },
}


def get_opcode(mnemonic: str, version: str = "HMv1") -> int:
    """Get opcode number for a mnemonic."""
    return VERSION_ISA[version][mnemonic.upper()][0]


def get_cycles(mnemonic: str, version: str = "HMv1") -> int:
    """Get cycle count for a mnemonic."""
    return VERSION_ISA[version][mnemonic.upper()][1]


def get_mnemonic(opcode: int, version: str = "HMv1") -> str:
    """Get mnemonic for an opcode.

    Args:
        opcode: 4-bit opcode value (0-15)
        version: HM version (HMv1 or HMv2)

    Returns:
        Mnemonic string, or "???" if unknown opcode.
    """
    opcode_map = VERSION_OPCODE_MAP.get(version, HMV1_OPCODE_TO_MNEMONIC)
    return opcode_map.get(opcode, "???")
