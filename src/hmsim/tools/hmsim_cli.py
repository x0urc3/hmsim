#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator CLI - Headless execution for HM processor family."""

import argparse
import sys
from typing import Optional

from hmsim import __version__
from hmsim.engine.cpu import HMEngine
from hmsim.engine.report import print_report


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
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-a", "--arch",
        choices=["HMv1", "HMv2", "HMv3", "HMv4"],
        help="Override processor architecture (default: from state file)"
    )
    parser.add_argument(
        "-m", "--max-cycles",
        type=int,
        default=1000000,
        help="Maximum cycles before forced termination (default: 1,000,000)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report in JSON format"
    )
    args = parser.parse_args(argv)

    try:
        # Initial dummy engine to load state and find architecture
        temp_engine = HMEngine("HMv1")
        loaded_arch = temp_engine.load_state(args.state_file)

        # Determine actual architecture to use
        architecture = args.arch or loaded_arch
        if architecture not in HMEngine.VALID_ARCHITECTURES:
            print(f"Warning: HMv{architecture[-1]} state loaded as HMv2", file=sys.stderr)
            architecture = "HMv2"

        # Create final engine with correct architecture and reload state
        engine = HMEngine(architecture)
        engine.load_state(args.state_file)

        print(f"Loaded {architecture} program. Starting execution...")

        try:
            while engine.total_cycles < args.max_cycles:
                engine.step()
        except ValueError as e:
            # Check if it's an unknown opcode, which we treat as HALT
            if "Unknown opcode" in str(e) or "not supported" in str(e):
                print(f"\nProgram Halted: {e}")
            else:
                print(f"\nExecution Error: {e}", file=sys.stderr)
                print_report(engine, args.json)
                return 1
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")

        if engine.total_cycles >= args.max_cycles:
            print(f"\nWarning: Maximum cycles ({args.max_cycles}) reached.")

        print_report(engine, args.json)
        return 0

    except FileNotFoundError:
        print(f"Error: State file not found: {args.state_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
