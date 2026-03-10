#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM State Persistence - Logic for loading and saving JSON state files."""

import datetime
import json
import platform
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema

from hmsim import __version__
from hmsim.engine.strategies import get_strategy
from hmsim.tools.hmdas import disassemble
from hmsim.tools.hmasm import assemble

SCHEMA_PATH = Path(__file__).parent / "schema.json"


def _load_schema() -> Dict[str, Any]:
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


def _get_current_timestamp() -> str:
    return datetime.datetime.now().isoformat()


def _get_machine_info() -> Dict[str, str]:
    return {
        "os": platform.system(),
        "hostname": socket.gethostname(),
        "platform": platform.platform()
    }


def _get_debug_default() -> bool:
    return True


def validate_state(state: Dict[str, Any]) -> None:
    schema = _load_schema()
    try:
        jsonschema.validate(state, schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        raise ValueError(f"Schema validation failed at '{path}': {e.message}") from None
    except jsonschema.SchemaError as e:
        raise ValueError(f"Invalid schema: {e.message}") from None


def _parse_region_value(val):
    """Parse a region value that can be int or hex string."""
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        if val.lower().startswith("0x"):
            return int(val, 16)
        return int(val)
    return 0


def save_state_to_dict(engine: Any) -> Dict[str, Any]:
    """Convert engine state to a dictionary for JSON serialization.

    Implements "Linear Disassembly" heuristic:
    - Starting at text_region[0], attempt to disassemble each word as instruction.
    - If successful, add to text section.
    - If disassembly fails or 0x0 encountered, stop text collection.
    - Remaining non-zero memory within data_region goes to data section.

    Args:
        engine: The HMEngine instance.

    Returns:
        Dictionary containing the sparse engine state with text and data sections.
    """
    text: Dict[str, str] = {}
    data: Dict[str, str] = {}

    text_start, text_end = engine.text_region
    data_start, data_end = engine.data_region

    addr = text_start
    while addr <= text_end:
        val = engine._memory[addr]
        if val == 0:
            addr += 1
            continue
        disasm = disassemble(val, engine.architecture)
        if disasm.startswith("???"):
            break
        if addr in engine.comments:
            disasm = f"{disasm} ; {engine.comments[addr]}"
        text[f"0x{addr:04X}"] = disasm
        addr += 1

    for i in range(data_start, data_end + 1):
        val = engine._memory[i]
        if val != 0 and f"0x{i:04X}" not in text:
            data[f"0x{i:04X}"] = f"0x{val:04X}"

    return {
        "architecture": engine.architecture,
        "setup": {
            "text": list(engine.text_region),
            "data": list(engine.data_region)
        },
        "pc": engine.pc,
        "ac": engine.ac,
        "ir": engine.ir,
        "sr": engine.sr,
        "text": text,
        "data": data
    }

def save_state(engine: Any, file_path: str | Path, debug: Optional[bool] = None) -> None:
    """Save engine state to a JSON file with session-bound metadata tracking.

    Args:
        engine: The HMEngine instance.
        file_path: Path to the output JSON file.
        debug: If provided, overrides the session's debug setting.
    """
    state = save_state_to_dict(engine)

    # Use session-bound metadata from the engine
    session_metadata = engine.metadata

    if debug is not None:
        session_metadata["debug"] = debug

    updated_at = _get_current_timestamp()
    software_version = __version__

    # Update top-level fields
    session_metadata["updated_at"] = updated_at
    session_metadata["software_version"] = software_version

    if session_metadata.get("debug", _get_debug_default()):
        current_machine_info = _get_machine_info()
        log = session_metadata.get("log", [])

        if log:
            last_entry = log[-1]
            last_machine = last_entry.get("machine_info", {})
            if last_machine == current_machine_info:
                # Same machine/user: Update existing entry
                last_entry["timestamp"] = updated_at
                last_entry["software_version"] = software_version
            else:
                # Different machine/user: Append new entry
                log.append({
                    "timestamp": updated_at,
                    "software_version": software_version,
                    "machine_info": current_machine_info,
                    "relevant_info": ""
                })
        else:
            # First log entry
            log.append({
                "timestamp": updated_at,
                "software_version": software_version,
                "machine_info": current_machine_info,
                "relevant_info": ""
            })
        session_metadata["log"] = log

    ordered_state: Dict[str, Any] = {}
    ordered_state["architecture"] = state["architecture"]
    ordered_state["setup"] = state["setup"]
    ordered_state["pc"] = state["pc"]
    ordered_state["ac"] = state["ac"]
    ordered_state["ir"] = state["ir"]
    ordered_state["sr"] = state["sr"]
    ordered_state["text"] = state["text"]
    ordered_state["data"] = state["data"]
    ordered_state["metadata"] = session_metadata

    with open(file_path, 'w') as f:
        json.dump(ordered_state, f, indent=2)

def load_state_from_dict(engine: Any, state: Dict[str, Any]) -> str:
    """Load engine state from a dictionary.

    Args:
        engine: The HMEngine instance.
        state: Dictionary containing the engine state with text and data sections.

    Returns:
        The architecture string from the state file.

    Raises:
        ValueError: If the state fails JSON Schema validation or architecture is missing.
    """
    validate_state(state)
    architecture = state.get("architecture")
    if not architecture:
        raise ValueError("State file missing required 'architecture' key")
    engine.architecture = architecture
    engine._strategy = get_strategy(architecture)

    engine.pc = state.get("pc", 0)
    engine.ac = state.get("ac", 0)
    engine.ir = state.get("ir", 0)
    engine.sr = state.get("sr", 0)

    # Ingest metadata into engine session
    metadata = state.get("metadata")
    if metadata:
        engine.metadata = metadata
    else:
        # For legacy files missing metadata, initialize a fresh session
        engine.metadata = {
            "debug": _get_debug_default(),
            "software_version": __version__,
            "created_at": _get_current_timestamp(),
            "updated_at": _get_current_timestamp(),
            "log": []
        }

    setup = state.get("setup", None)
    if setup:
        text_region = [_parse_region_value(v) for v in setup.get("text", [0, 0x0100])]
        data_region = [_parse_region_value(v) for v in setup.get("data", [0x0101, 0xFFFF])]
        if len(text_region) == 2 and len(data_region) == 2:
            try:
                engine.set_regions(
                    (text_region[0], text_region[1]),
                    (data_region[0], data_region[1])
                )
            except ValueError:
                engine._text_region = (0x0000, 0x0100)
                engine._data_region = (0x0101, 0xFFFF)

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
                    machine_code = assemble(code_part, architecture)
                else:
                    machine_code = assemble(mnemonic, architecture)
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

    return architecture

def load_state(engine: Any, file_path: str | Path) -> str:
    """Load engine state from a JSON file.

    Args:
        engine: The HMEngine instance.
        file_path: Path to the input JSON file.

    Returns:
        The architecture string from the state file.
    """
    with open(file_path, 'r') as f:
        state = json.load(f)
    return load_state_from_dict(engine, state)
