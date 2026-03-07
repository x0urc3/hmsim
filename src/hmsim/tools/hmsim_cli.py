#!/usr/bin/env python3
"""HM Simulator CLI - Headless execution for HM processor family."""

import argparse
import sys
from typing import Optional

from hmsim.engine.cpu import HMEngine


def print_report(engine: HMEngine) -> None:
    """Print the final register, statistics, and non-zero memory content.

    Args:
        engine: The HMEngine instance.
    """
    print("\n" + "=" * 40)
    print("      HM SIMULATOR EXECUTION REPORT")
    print("=" * 40)

    print("\n[Registers]")
    print(f"PC (Program Counter): 0x{engine.pc:04X}")
    print(f"AC (Accumulator):     0x{engine.ac:04X}")
    print(f"IR (Instr Register):  0x{engine.ir:04X}")
    print(f"SR (Status Register): 0x{engine.sr:04X}")

    print("\n[Statistics]")
    print(f"Total Cycles: {engine.total_cycles}")

    print("\n[Memory (Non-zero)]")
    has_memory = False
    for addr, val in enumerate(engine._memory):
        if val != 0:
            print(f"0x{addr:04X}: 0x{val:04X}")
            has_memory = True

    if not has_memory:
        print("(All memory is zero)")

    print("=" * 40 + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HM Simulator CLI - Run HM state files headlessly"
    )
    parser.add_argument(
        "state_file",
        help="Path to the HM state file (.hm)"
    )
    parser.add_argument(
        "-v", "--version",
        choices=["HMv1", "HMv2"],
        help="Override processor version (default: from state file)"
    )
    parser.add_argument(
        "-m", "--max-cycles",
        type=int,
        default=1000000,
        help="Maximum cycles before forced termination (default: 1,000,000)"
    )
    args = parser.parse_args(argv)

    try:
        # Initial dummy engine to load state and find version
        temp_engine = HMEngine("HMv1")
        loaded_version = temp_engine.load_state(args.state_file)

        # Determine actual version to use
        version = args.version or loaded_version
        if version not in HMEngine.VALID_VERSIONS:
            print(f"Warning: HMv{version[-1]} state loaded as HMv2", file=sys.stderr)
            version = "HMv2"

        # Create final engine with correct version and reload state
        engine = HMEngine(version)
        engine.load_state(args.state_file)

        print(f"Loaded {version} program. Starting execution...")

        try:
            while engine.total_cycles < args.max_cycles:
                engine.step()
        except ValueError as e:
            # Check if it's an unknown opcode, which we treat as HALT
            if "Unknown opcode" in str(e) or "not supported" in str(e):
                print(f"\nProgram Halted: {e}")
            else:
                print(f"\nExecution Error: {e}", file=sys.stderr)
                print_report(engine)
                return 1
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")

        if engine.total_cycles >= args.max_cycles:
            print(f"\nWarning: Maximum cycles ({args.max_cycles}) reached.")

        print_report(engine)
        return 0

    except FileNotFoundError:
        print(f"Error: State file not found: {args.state_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
