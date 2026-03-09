# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Shared reporting utilities for HM Simulator."""

import json
from typing import Dict, Any, List, Tuple

from hmsim.engine.cpu import HMEngine


def format_report(engine: HMEngine) -> str:
    """Format the final register, statistics, and non-zero memory content as a string.

    Args:
        engine: The HMEngine instance.

    Returns:
        Formatted report string.
    """
    lines = []
    lines.append("\n" + "=" * 40)
    lines.append("      HM SIMULATOR EXECUTION REPORT")
    lines.append("=" * 40)

    lines.append("\n[Registers]")
    lines.append(f"PC (Program Counter): 0x{engine.pc:04X}")
    lines.append(f"AC (Accumulator):     0x{engine.ac:04X}")
    lines.append(f"IR (Instr Register):  0x{engine.ir:04X}")
    lines.append(f"SR (Status Register): 0x{engine.sr:04X}")

    lines.append("\n[Statistics]")
    lines.append(f"Total Cycles: {engine.total_cycles}")

    lines.append("\n[Memory (Non-zero)]")
    has_memory = False
    for addr, val in enumerate(engine._memory):
        if val != 0:
            lines.append(f"0x{addr:04X}: 0x{val:04X}")
            has_memory = True

    if not has_memory:
        lines.append("(All memory is zero)")

    lines.append("=" * 40 + "\n")
    return "\n".join(lines)


def format_report_json(engine: HMEngine) -> str:
    """Format the final state as JSON for programmatic use.

    Args:
        engine: The HMEngine instance.

    Returns:
        JSON string.
    """
    memory_content: List[Dict[str, str]] = []
    for addr, val in enumerate(engine._memory):
        if val != 0:
            memory_content.append({
                "address": f"0x{addr:04X}",
                "value": f"0x{val:04X}"
            })

    report: Dict[str, Any] = {
        "registers": {
            "pc": f"0x{engine.pc:04X}",
            "ac": f"0x{engine.ac:04X}",
            "ir": f"0x{engine.ir:04X}",
            "sr": f"0x{engine.sr:04X}"
        },
        "statistics": {
            "total_cycles": engine.total_cycles
        },
        "memory": memory_content
    }
    return json.dumps(report, indent=2)


def print_report(engine: HMEngine, json_output: bool = False) -> None:
    """Print the final register, statistics, and non-zero memory content.

    Args:
        engine: The HMEngine instance.
        json_output: If True, output JSON format instead of human-readable.
    """
    if json_output:
        print(format_report_json(engine))
    else:
        print(format_report(engine))
