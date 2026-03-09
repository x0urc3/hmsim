# Consistency Test Plan: hmsim CLI vs GUI

This document outlines the plan for ensuring that the HM Simulator's command-line interface (`hmsim_cli`) and graphical user interface (`hmsim gui`) produce identical simulation results for the HM processor family (v1-v4).

## Objectives

1.  **Refactor**: Consolidate simulation reporting logic into a shared module.
2.  **Enhance GUI**: Add a headless mode to the HMSim GUI to allow execution without a display.
3.  **Validate**: Create an automated test suite to verify consistency between both interfaces using all provided example state files.

## Proposed Changes

### 1. Refactor Reporting Logic

Move the `print_report` function from `src/hmsim/tools/hmsim_cli.py` to a new shared location: `src/hmsim/engine/report.py`.

-   **File**: `src/hmsim/engine/report.py`
-   **Function**: `print_report(engine: HMEngine) -> None`
-   **Description**: Prints the final register state, statistics (total cycles), and non-zero memory content in a standardized format.

Update `src/hmsim/tools/hmsim_cli.py` to import and use this shared function.

### 2. Add Headless Mode to GUI

Enhance the HMSim GUI entry point to support headless execution via command-line arguments.

-   **File**: `src/hmsim/gui/hm_gui.py`
-   **Implementation**:
    -   Use `argparse` within the `main` function (before `HMApplication().run(argv)`).
    -   Add `--run-headless <state_file>` flag.
    -   Add `-m`, `--max-cycles <num>` flag (default to 1,000,000, matching `hmsim_cli`).
-   **Behavior**:
    -   If `--run-headless` is provided:
        1.  Initialize `HMEngine`.
        2.  Load the specified `.hm` state file.
        3.  Run the simulation loop until a halt condition is reached (e.g., unknown opcode) or `max-cycles` is exceeded.
        4.  Call `print_report(engine)` to output the final state.
        5.  Exit with a success (0) or failure (1) code.
    -   If `--run-headless` is NOT provided, proceed with the normal GTK application loop.

### 3. Automated Consistency Test

Create an integration test script to automate the comparison.

-   **File**: `tests/integration/test_consistency.py`
-   **Test Case Logic**:
    1.  Discover all `.hm` files in the `examples/` directory.
    2.  For each file:
        -   Execute `python3 -m hmsim.tools.hmsim_cli examples/<file>.hm` and capture `stdout`.
        -   Execute `python3 -m hmsim.gui.hm_gui --run-headless examples/<file>.hm` and capture `stdout`.
        -   Compare the "REPORT" sections of both outputs (everything from `[Registers]` to the end).
        -   Assert that the outputs are identical.
-   **Goal**: Ensure that both tools behave exactly the same when processing the same state files, especially for different HM versions (v1-v4).

## Implementation Steps (for the next AI agent)

1.  **Extract `print_report`**: Move the function and update `hmsim_cli.py`.
2.  **Update `hm_gui.py`**: Add `argparse` and the headless execution logic.
3.  **Create Integration Test**: Implement `tests/integration/test_consistency.py`.
4.  **Verify**: Run `pytest tests/integration/test_consistency.py` and fix any discrepancies found.
5.  **Documentation**: Update `docs/developer/DEVELOPMENT.md` to mention the consistency test as part of the CI/CD requirements.

## Expected Outcome

-   `hmsim gui --run-headless <file>` produces the exact same report as `hmsim_cli <file>`.
-   The integration test passes for all example files.
-   Discrepancies between the CLI and GUI are eliminated, providing users with consistent results regardless of the interface used.
