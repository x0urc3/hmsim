# Implementation Plan: HM State File Format Migration (.hm)

This document outlines the strategy for migrating the HM Simulator from the legacy JSON-based `memory` format to the enhanced `.hm` format with structured `text` (assembly) and `data` (hex) sections.

---

## Objective
- Replace the `memory` field in state files with `text` and `data` sections.
- Rename the file extension from `.json` to `.hm`.
- Update all existing examples and test fixtures to the new format.
- **Note:** Backward compatibility with the old `.json` format is NOT required.

---

## Phase 1: Engine Logic Refactoring

### 1.1 Update `src/hmsim/engine/state.py`
Modify the state persistence logic to implement the "Linear Disassembly" heuristic.

**Actions:**
- **`save_state_to_dict(engine)`**:
    1.  Initialize `text = {}` and `data = {}`.
    2.  Starting at `addr = 0`, attempt to disassemble each word using `hmsim.tools.hmdas.disassemble(val, engine.version)`.
    3.  If successful, add to `text` using `0xXXXX` hex string keys.
    4.  If disassembly fails (e.g., `ValueError` from an unknown opcode), stop the `text` collection process.
    5.  Iterate through all remaining non-zero memory locations. Add them to `data` as hex string pairs: `{"0xADDR": "0xVAL"}`.
    6.  Return a dictionary with `version`, `pc`, `ac`, `ir`, `sr`, `text`, and `data`.
- **`load_state_from_dict(engine, state)`**:
    1.  Restore registers (`pc`, `ac`, `ir`, `sr`) from the dictionary.
    2.  Clear engine memory (`[0] * 65536`).
    3.  **Process `text`**: For each entry, use `hmsim.tools.hmasm.assemble(mnemonic, version)` to convert the assembly string back to 16-bit machine code and write it to the specified address.
    4.  **Process `data`**: Parse the hex string values and write them to the specified addresses.
    5.  Remove any logic that handles the legacy `memory` field.

### 1.2 Update `src/hmsim/engine/cpu.py`
Ensure the `HMEngine` properly delegates to the updated `state.py` methods.

---

## Phase 2: GUI and CLI Adaptation

### 2.1 Update File Dialogs (`src/hmsim/gui/widgets/file_dialog.py`)
- Change `set_initial_name("program.json")` to `set_initial_name("program.hm")`.
- Update `Gtk.FileFilter`:
    - Name: "HM State Files (*.hm)"
    - Pattern: `*.hm`
- Remove `.json` filters.

### 2.2 Update CLI Tool (`src/hmsim/tools/hmsim_cli.py`)
- Update `argparse` descriptions and help text to reference `.hm` files.
- Update examples in the `--help` output.

### 2.3 Update Documentation
- **`README.md`**: Update examples to use `hmsim program.hm`.
- **`DEVELOPMENT.md`**: Update tool usage sections.
- **`docs/HM_Software_Spec.md`**: Ensure it mentions `.hm` as the primary state format.

---

## Phase 3: Data Migration (Examples & Fixtures)

### 3.1 Rename Files
Rename all existing state files:
- `examples/add_two_numbers.json` → `examples/add_two_numbers.hm`
- `examples/multiply_two_numbers.json` → `examples/multiply_two_numbers.hm`
- `tests/fixtures/sample_state.json` → `tests/fixtures/sample_state.hm`

### 3.2 Update File Content
Manually or programmatically convert the content of these files to the new format:

**Example: `add_two_numbers.hm`**
```json
{
  "version": "HMv1",
  "pc": 0,
  "ac": 0,
  "ir": 0,
  "sr": 0,
  "text": {
    "0x0000": "LOAD 0x00A",
    "0x0001": "ADD 0x00B",
    "0x0002": "STORE 0x00C"
  },
  "data": {
    "0x000A": "0x0005",
    "0x000B": "0x0007"
  }
}
```

---

## Phase 4: Validation and Testing

### 4.1 Update Test Suite
- Update `tests/unit/test_json_state.py` (or similar) to use the new `.hm` extension and verify the `text`/`data` split.
- Update any integration tests that load these files.

### 4.2 Manual Verification
1.  **CLI Test**: Run `hmsim examples/add_two_numbers.hm` and verify the output.
2.  **GUI Test**:
    - Launch `hmsim_gui`.
    - Open `examples/add_two_numbers.hm`.
    - Verify instructions appear in the editor/memory view.
    - Save to `test.hm` and verify the internal JSON structure matches the specification.

---

## Verification Commands
```bash
# Run unit tests
pytest

# Test CLI
hmsim examples/multiply_two_numbers.hm

# Test Assembler/Disassembler integration
hmasm "LOAD 0x10"
hmdas 0x1010
```
