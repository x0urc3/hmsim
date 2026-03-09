# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Integration tests for CLI vs GUI consistency."""

import glob
import os
import subprocess
import sys


EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "examples")


def get_example_files():
    """Get all .hm files from the examples directory."""
    return sorted(glob.glob(os.path.join(EXAMPLES_DIR, "*.hm")))





def run_command(cmd: list[str]) -> tuple[str, str, int]:
    """Run a command and return stdout, stderr, and return code."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr, result.returncode


class TestConsistency:
    def test_cli_vs_gui_consistency(self):
        """Test that CLI and GUI produce identical results for all example files."""
        example_files = get_example_files()

        assert len(example_files) > 0, "No example files found"

        for example_file in example_files:
            filename = os.path.basename(example_file)

            stdout_cli, stderr_cli, return_cli = run_command([
                sys.executable, "-m", "hmsim.tools.hmsim_cli", "--json", example_file
            ])

            stdout_gui, stderr_gui, return_gui = run_command([
                sys.executable, "-m", "hmsim.gui.hm_gui",
                "--run-headless", example_file, "--json"
            ])

            combined_cli = stdout_cli
            combined_gui = stdout_gui

            report_cli = stdout_cli.strip()
            report_gui = stdout_gui.strip()

            assert return_cli == 0, f"CLI failed for {filename}: {stderr_cli}"
            assert return_gui == 0, f"GUI failed for {filename}: {stderr_gui}"
            assert report_cli == report_gui, (
                f"Output mismatch for {filename}:\n"
                f"CLI report:\n{report_cli}\n"
                f"GUI report:\n{report_gui}"
            )
