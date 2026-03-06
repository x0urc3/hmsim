"""HM Instruction Set Architecture definitions.

This module serves as the single source of truth for the HM processor
instruction set. It defines opcodes, mnemonics, and cycle counts for
each processor version.
"""

from typing import Dict, Tuple

OP_LOAD = 0x1
OP_STORE = 0x2
OP_ADD = 0x5
OP_SUB = 0x6
OP_JMP = 0x8
OP_JMPZ = 0x9

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

VERSION_ISA = {
    "HMv1": HMV1_ISA,
    "HMv2": HMV2_ISA,
}

HMV1_OPCODE_TO_MNEMONIC = {v[0]: k for k, v in HMV1_ISA.items()}


def get_opcode(mnemonic: str, version: str = "HMv1") -> int:
    """Get opcode number for a mnemonic."""
    return VERSION_ISA[version][mnemonic.upper()][0]


def get_cycles(mnemonic: str, version: str = "HMv1") -> int:
    """Get cycle count for a mnemonic."""
    return VERSION_ISA[version][mnemonic.upper()][1]
