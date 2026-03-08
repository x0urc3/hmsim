#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM State Persistence - Logic for loading and saving JSON state files."""

import json
from typing import Any, Dict, Optional

from hmsim.tools.hmdas import disassemble
from hmsim.tools.hmasm import assemble


def save_state_to_dict(engine: Any) -> Dict[str, Any]:
    """Convert engine state to a dictionary for JSON serialization.

    Implements "Linear Disassembly" heuristic:
    - Starting at addr 0, attempt to disassemble each word as instruction.
    - If successful, add to text section.
    - If disassembly fails, stop text collection.
    - Remaining non-zero memory goes to data section.

    Args:
        engine: The HMEngine instance.

    Returns:
        Dictionary containing the sparse engine state with text and data sections.
    """
    text: Dict[str, str] = {}
    data: Dict[str, str] = {}

    addr = 0
    while addr < 65536:
        val = engine._memory[addr]
        if val == 0:
            addr += 1
            continue
        disasm = disassemble(val, engine.version)
        if disasm.startswith("???"):
            break
        if addr in engine.comments:
            disasm = f"{disasm} ; {engine.comments[addr]}"
        text[f"0x{addr:04X}"] = disasm
        addr += 1

    for i, val in enumerate(engine._memory):
        if val != 0 and f"0x{i:04X}" not in text:
            data[f"0x{i:04X}"] = f"0x{val:04X}"

    return {
        "version": engine.version,
        "pc": engine.pc,
        "ac": engine.ac,
        "ir": engine.ir,
        "sr": engine.sr,
        "text": text,
        "data": data
    }

def save_state(engine: Any, file_path: str) -> None:
    """Save engine state to a JSON file.

    Args:
        engine: The HMEngine instance.
        file_path: Path to the output JSON file.
    """
    state = save_state_to_dict(engine)
    with open(file_path, 'w') as f:
        json.dump(state, f, indent=2)

def load_state_from_dict(engine: Any, state: Dict[str, Any]) -> str:
    """Load engine state from a dictionary.

    Args:
        engine: The HMEngine instance.
        state: Dictionary containing the engine state with text and data sections.

    Returns:
        The version string from the state file.
    """
    version = state.get("version", "HMv1")

    engine.pc = state.get("pc", 0)
    engine.ac = state.get("ac", 0)
    engine.ir = state.get("ir", 0)
    engine.sr = state.get("sr", 0)

    # Reset memory before loading sparse data
    engine._memory = [0] * 65536

    # Process text section: assemble mnemonics to machine code
    text = state.get("text", {})
    for addr_str, mnemonic in text.items():
        try:
            addr = int(addr_str, 16)
            if 0 <= addr < 65536:
                if ';' in mnemonic:
                    code_part, comment = mnemonic.split(';', 1)
                    engine.comments[addr] = comment.strip()
                    machine_code = assemble(code_part, version)
                else:
                    machine_code = assemble(mnemonic, version)
                engine._memory[addr] = machine_code
        except (ValueError, KeyError):
            continue

    # Process data section: parse hex string values
    data = state.get("data", {})
    for addr_str, val_str in data.items():
        try:
            addr = int(addr_str, 16)
            if 0 <= addr < 65536:
                val = int(val_str, 16)
                engine._memory[addr] = val & 0xFFFF
        except ValueError:
            continue

    return version

def load_state(engine: Any, file_path: str) -> str:
    """Load engine state from a JSON file.

    Args:
        engine: The HMEngine instance.
        file_path: Path to the input JSON file.

    Returns:
        The version string from the state file.
    """
    with open(file_path, 'r') as f:
        state = json.load(f)
    return load_state_from_dict(engine, state)
