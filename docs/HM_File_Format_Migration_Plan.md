# Implementation Plan: HM State File Format Migration (.hm)

This document outlines the strategy for migrating the HM Simulator from the legacy JSON-based `memory` format to the enhanced `.hm` format with structured `text` and `data` sections and support for inline comments.

---

## Phase 1: Engine Logic Refactoring

### 1.1 Update `src/hmsim/tools/hmasm.py`
Modify the `assemble()` function to handle inline comments.
- **Action**: Use `instruction.split(';', 1)[0].strip()` to isolate the code before parsing.
- **Goal**: Allow instructions like `"LOAD 0x100 ; load data"` to be correctly assembled.

### 1.2 Update `src/hmsim/engine/cpu.py`
Modify the `HMEngine` to store comment metadata.
- **Action**: Add a `comments` dictionary (mapping address integers to strings).
- **Goal**: Persist comments across simulation cycles.

### 1.3 Update `src/hmsim/engine/state.py`
Implement the "Linear Disassembly" heuristic and comment extraction.
- **Save Logic**:
    1.  Start at address `0x0000` and use `hmdas` to disassemble words sequentially.
    2.  If an address exists in `engine.comments`, append it to the assembly string (e.g., `"MNEMONIC ADDR ; Comment"`).
    3.  Stop disassembly when an invalid opcode is hit.
    4.  Store all other non-zero memory in `data` section as hexadecimal strings.
- **Load Logic**:
    1.  Parse the `text` section. If a `;` is found, extract and store the comment in `engine.comments`.
    2.  Pass the pre-`;` portion to `hmasm.assemble()`.
    3.  Parse the `data` section from hexadecimal.

---

## Phase 2: GUI and CLI Adaptation

### 2.1 Update File Dialogs (`src/hmsim/gui/widgets/file_dialog.py`)
- Change `set_initial_name("program.json")` to `set_initial_name("program.hm")`.
- Update filters to point to `*.hm`.

### 2.2 Update CLI Tool (`src/hmsim/tools/hmsim_cli.py`)
- Update `argparse` descriptions to reference the `.hm` format.

---

## Phase 3: Data Migration (Final State)

Rename files and update content as follows:

### 3.1 `examples/add_two_numbers.hm`
```json
{
  "version": "HMv1",
  "pc": 0,
  "ac": 0,
  "ir": 0,
  "sr": 0,
  "text": {
    "0x0000": "LOAD 0x00A ; load value from address 10 into AC",
    "0x0001": "ADD 0x00B  ; add value from address 11 to AC",
    "0x0002": "STORE 0x00C ; store AC value into address 12"
  },
  "data": {
    "0x000A": "0x0005",
    "0x000B": "0x0007"
  }
}
```

### 3.2 `examples/multiply_two_numbers.hm`
```json
{
  "version": "HMv2",
  "pc": 0,
  "ac": 0,
  "ir": 0,
  "sr": 0,
  "text": {
    "0x0000": "LOAD 0x011",
    "0x0001": "STORE 0x013",
    "0x0002": "LOAD 0x010",
    "0x0003": "STORE 0x014",
    "0x0004": "LOAD 0x013",
    "0x0005": "JMPZ 0x00D",
    "0x0006": "LOAD 0x00E",
    "0x0007": "ADD 0x014",
    "0x0008": "STORE 0x00E",
    "0x0009": "LOAD 0x013",
    "0x000A": "SUB 0x012",
    "0x000B": "STORE 0x013",
    "0x000C": "JMP 0x004"
  },
  "data": {
    "0x000D": "0x0000",
    "0x000E": "0x0000",
    "0x0010": "0x0003",
    "0x0011": "0x0004",
    "0x0012": "0x0001"
  }
}
```

### 3.3 `tests/fixtures/sample_state.hm`
```json
{
  "version": "HMv1",
  "pc": 0,
  "ac": 0,
  "ir": 0,
  "sr": 0,
  "text": {
    "0x0000": "LOAD 0x100 ; test load"
  },
  "data": {
    "0x0100": "0x0005"
  }
}
```
