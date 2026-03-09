# Implementation Plan: Processor Architecture Renaming & Software Version Alignment

## 1. Overview
The current codebase uses the term "Version" ambiguously to refer to both the software version (e.g., 0.1.0) and the processor ISA level (e.g., HMv1). This plan provides a step-by-step directive to refactor the internal logic, persistence layer, CLI, and GUI to use "Architecture" for the processor and "Version" for the software.

## 2. Technical Requirements
- **Scope:** `src/hmsim/engine/`, `src/hmsim/tools/`, `src/hmsim/gui/`, `docs/`, `tests/`, and `examples/`.
- **Backward Compatibility:** **None required.** Legacy `.hm` files using the `"version"` key will be considered invalid.
- **Data Migration:** All existing example programs (`examples/*.hm`) and test fixtures must be updated to use the new `"architecture"` key.
- **CLI Standard:** Reassign `-v/--version` to software version; introduce `-a/--arch` for processor selection.

## 3. Step-by-Step Execution Strategy

### Step 1: Internal Logic Refactoring (The Engine)
1.  **ISA Definitions (`isa.py`):**
    - Rename `VERSION_ISA` to `ARCH_ISA`.
    - Rename `VERSION_OPCODE_MAP` to `ARCH_OPCODE_MAP`.
    - Update function signatures: `get_opcode(mnemonic, arch="HMv1")`, `get_cycles(mnemonic, arch="HMv1")`, `get_mnemonic(opcode, arch="HMv1")`.
2.  **CPU Core (`cpu.py`):**
    - Rename `VALID_VERSIONS` to `VALID_ARCHITECTURES`.
    - Rename `HMEngine.version` attribute to `HMEngine.architecture`.
    - Update constructor to accept `architecture` instead of `version`.
3.  **Strategies (`strategies/__init__.py`):**
    - Rename `get_strategy(version)` to `get_strategy(arch)`.
    - Update internal mapping dictionary keys.

### Step 2: Persistence & Schema Migration (The State)
1.  **JSON Schema (`schema.json`):**
    - Replace the `version` property with `architecture`.
    - Update descriptions to reflect "Processor Architecture".
2.  **State Logic (`state.py`):**
    - **Loading:** Update `load_state_from_dict` to strictly require the `architecture` key. Remove any logic that falls back to or maps from `version`.
    - **Saving:** Update `save_state_to_dict` to use the new `architecture` key exclusively.
    - **Return Value:** Ensure `load_state` returns the architecture string.

### Step 3: CLI Entry Point & Flag Remapping
1.  **Global Versioning (`src/hmsim/__init__.py`):**
    - Ensure `__version__ = "0.1.0"` is defined.
2.  **CLI Tools (`hmsim_cli.py`, `hmasm.py`, `hmdas.py`):**
    - **Processor Flag:** Change `-v/--version` to `-a/--arch` (or `--architecture`). Update the `choices` to reference `VALID_ARCHITECTURES`.
    - **Software Flag:** Implement a standard `argparse` version action: `parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")`.
    - **Help Text:** Update all descriptions to use "Architecture" when referring to HMv1-4.

### Step 4: Graphical User Interface Updates
1.  **Main Window (`main_window.py`):**
    - Rename `self.current_version` to `self.current_arch`.
    - Rename `_on_version_changed` to `_on_arch_changed`.
    - Update all logic referencing `engine.version` to `engine.architecture`.
2.  **Widgets:**
    - **RegisterView (`register_view.py`):** Rename `set_version` to `set_architecture`. Update UI label from "Engine: HMvX" to "Arch: HMvX".
    - **SetupDialog (`setup_dialog.py`):** Rename "Processor Version" labels/dropdowns to "Processor Architecture".
3.  **Application (`hm_gui.py`):**
    - Ensure the `AboutDialog` correctly pulls `__version__` and labels it as the application version.

### Step 5: Batch Update: Examples & Documentation
1.  **Examples:** Update all `.hm` files in the `examples/` directory. Replace `"version": "HMvX"` with `"architecture": "HMvX"`.
2.  **Markdown Documentation:** Perform a case-sensitive search-and-replace for "Processor Version" -> "Processor Architecture" in all `.md` files in `docs/` and `README.md`.

### Step 6: Verification & Test Suite Alignment
1.  **Test Fixtures:** Search all files in `tests/` for any hardcoded state dictionaries and update the `version` key to `architecture`.
2.  **Test Logic:** Update any test assertions or function calls that use the old `version` terminology (e.g., `engine.version == "HMv1"` should become `engine.architecture == "HMv1"`).
3.  **Run Suite:** Execute `pytest` and ensure 100% pass rate.
4.  **CLI Check:** Verify `hmsim_cli --version` returns the software version and `hmsim_cli --arch HMv3` functions correctly.

## 4. Success Metrics
- Codebase internal variables use `arch` or `architecture` for processor levels.
- JSON state files use the `architecture` key; files with the `version` key are correctly rejected by the schema/loader.
- CLI `-v` returns the software version.
- UI labels clearly distinguish between software version and processor architecture.
- All example programs and tests pass with the new nomenclature.

## 5. Contingencies
- **Ambiguity:** If "HMv1" appears in a string, ensure it is preserved as the name of the architecture, only changing the label *describing* it.
- **Build Failure:** If `pyproject.toml` version mismatch occurs, prioritize the version defined in `src/hmsim/__init__.py`.
