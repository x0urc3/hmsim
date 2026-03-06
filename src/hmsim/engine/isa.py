"""HM Instruction Set Architecture definitions.

This module serves as the single source of truth for the HM processor
instruction set. It defines opcodes, mnemonics, and cycle counts for
each processor version.
"""

from typing import Dict, Tuple

OP_LOAD = 0x1
OP_STORE = 0x2
OP_ADD = 0x5

HMV1_ISA: Dict[str, Tuple[int, int]] = {
    "LOAD": (OP_LOAD, 5),
    "STORE": (OP_STORE, 15),
    "ADD": (OP_ADD, 10),
}

HMV1_OPCODE_TO_MNEMONIC = {v[0]: k for k, v in HMV1_ISA.items()}


def get_opcode(mnemonic: str) -> int:
    """Get opcode number for a mnemonic."""
    return HMV1_ISA[mnemonic.upper()][0]


def get_cycles(mnemonic: str) -> int:
    """Get cycle count for a mnemonic."""
    return HMV1_ISA[mnemonic.upper()][1]
