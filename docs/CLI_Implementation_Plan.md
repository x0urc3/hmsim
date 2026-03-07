# CLI HMSim Implementation Plan

This document outlines the strategy for implementing a command-line interface (CLI) for the HM Simulator, ensuring maximum code reuse with the existing GUI version.

## Phase A: Refactor State Persistence (Code Sharing)
**Goal:** Extract JSON state handling from the GUI into a shared module.

### Tasks
1. Create `src/hmsim/engine/state.py` to house `load_state(engine, path)` and `save_state(engine, path)`.
2. Update `HMEngine` to use these functions or integrate them as methods.
3. Refactor `src/hmsim/gui/main_window.py` to remove its local JSON logic.

### Test Cases
*   **Unit Test - Sparse Memory:** Verify that `save_state` only writes non-zero memory addresses to the JSON file.
*   **Unit Test - Version Recovery:** Verify that loading a file with `version: "HMv3"` correctly initializes an `HMv2` engine and issues a warning, as per specification.
*   **Unit Test - Round-trip:** Load a state, modify one register, save it, and reload it to ensure all data (PC, AC, IR, SR, and memory) is preserved exactly.

## Phase B: CLI Core Development (`hmsim_cli.py`)
**Goal:** Implement the execution engine for headless simulation.

### Tasks
1. Create `src/hmsim/tools/hmsim_cli.py` using `argparse`.
2. Implement a simulation loop that handles `engine.step()` until a halt or error.
3. Add support for `--max-cycles` to prevent infinite execution.

### Test Cases
*   **Functional Test - Successful Run:** Execute `examples/add_two_numbers.json` and verify the process exits with code 0.
*   **Functional Test - Cycle Limit:** Run a program with an infinite loop (e.g., `JMP 0`) and verify it terminates when `--max-cycles` (default 1,000,000) is reached.
*   **Functional Test - Interrupt Handling:** Simulate a `KeyboardInterrupt` during execution and verify the simulator stops safely and prints the partial state.
*   **Functional Test - Unknown Opcode:** Verify that an invalid opcode (like `0x0000` on HMv1) triggers a "Program Halted" message rather than a crash.

## Phase C: Output Formatting & Statistics
**Goal:** Provide clear, human-readable feedback on program termination.

### Tasks
1. Implement a `print_report(engine)` function in the CLI tool.
2. Format registers and memory addresses in hexadecimal (e.g., `0x000A`).
3. Only display non-zero memory locations in the final summary.

### Test Cases
*   **Verification - Register Formatting:** Confirm that all registers (PC, AC, IR, SR) are padded to 4 hex digits (e.g., `AC: 0x0005` instead of `AC: 5`).
*   **Verification - Memory Summary:** Verify that if memory contains `{0: 1, 1: 0, 2: 5}`, the output only shows addresses `0x0000` and `0x0002`.
*   **Verification - Cycle Counts:** Ensure `Total Cycles` matches the sum of instruction weights defined in `isa.py`.

## Integration & Final Validation
**Goal:** Ensure the CLI is properly installed and compatible with the ecosystem.

### Tasks
1. Register `hmsim` as a script in `pyproject.toml`.
2. Perform a "GUI-to-CLI" integration test.

### Test Cases
*   **End-to-End - Cross-Compatibility:**
    1. Open `add_two_numbers.json` in the GUI.
    2. Step twice and "Save State" to `temp.json`.
    3. Run `hmsim temp.json` in the CLI.
    4. Verify the CLI picks up exactly where the GUI left off and finishes the calculation correctly.
*   **Installation Test:** Run `pip install -e .` and verify the `hmsim` command is available in the shell path.
