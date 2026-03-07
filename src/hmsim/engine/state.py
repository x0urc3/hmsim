"""HM State Persistence - Logic for loading and saving JSON state files."""

import json
from typing import Any, Dict, Optional

def save_state_to_dict(engine: Any) -> Dict[str, Any]:
    """Convert engine state to a dictionary for JSON serialization.

    Args:
        engine: The HMEngine instance.

    Returns:
        Dictionary containing the sparse engine state.
    """
    memory = {str(addr): val for addr, val in enumerate(engine._memory) if val != 0}
    return {
        "version": engine.version,
        "pc": engine.pc,
        "ac": engine.ac,
        "ir": engine.ir,
        "sr": engine.sr,
        "memory": memory
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
        state: Dictionary containing the engine state.

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
    memory = state.get("memory", {})
    for addr_str, val in memory.items():
        try:
            addr = int(addr_str)
            if 0 <= addr < 65536:
                if isinstance(val, str) and val.startswith("0x"):
                    val = int(val, 16)
                engine._memory[addr] = val & 0xFFFF
        except ValueError:
            continue # Skip invalid addresses

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
