# Implementation Plan: Phase 1 (HMv1 Core & Assembler)

This document provides a step-by-step guide for an AI agent to implement the foundational components of the **hmsim** project.

## 1. Environment & Scaffolding
- **Initialize Structure:** Create the following directory layout:
  ```text
  src/hmsim/
  ├── __init__.py
  ├── engine/
  │   ├── __init__.py
  │   └── cpu.py
  └── tools/
      ├── __init__.py
      └── hmasm.py
  tests/
  ├── __init__.py
  └── unit/
      ├── __init__.py
      └── test_cpu.py
  ```
- **Build Config:** Create `pyproject.toml` with pytest as optional dev dependency.

## 2. Core Engine Implementation
**File:** `src/hmsim/engine/cpu.py`
Implement the `HMv1Engine` class with the following specifications:
- **Registers:** `pc`, `ir`, `ac` initialized to `0x0000` (16-bit integers).
- **Memory:** A list/array of 65,536 integers (16-bit words).
- **Method `decode(instruction)`:**
  - Extract bits 15-12 as `opcode`.
  - Extract bits 11-0 as `address`.
- **Method `execute(opcode, address)`:**
  - `0x1 (LOAD)`: `ac = memory[address]`, `cycles += 5`.
  - `0x2 (STORE)`: `memory[address] = ac`, `cycles += 15`.
  - `0x5 (ADD)`: `ac += memory[address]`, `cycles += 10`.
  - Raise `ValueError` for unknown opcodes.
- **Method `step()`:** Fetch `memory[pc]`, decode, execute, and increment `pc`.

## 3. Unit Test Development
**File:** `tests/unit/test_cpu.py`
Develop `pytest` functions to verify the engine:
- `test_load_instruction`: Verify `AC` update and cycle count (5).
- `test_store_instruction`: Verify memory update and cycle count (15).
- `test_add_instruction`: Verify arithmetic result in `AC` and cycle count (10).
- `test_invalid_opcode`: Verify `ValueError` handling.

## 4. CLI Assembler Implementation
**File:** `src/hmsim/tools/hmasm.py`
Implement a simple CLI tool:
- **Parsing:** Accept a string like `"LOAD 100"`, `"STORE 0x200"`, or `"ADD 0b1010"`.
- **Address Handling:** Support decimal (default), hexadecimal (`0x`), and binary (`0b`) literals for addresses. Use `int(address_str, 0)` for flexible base detection.
- **Translation:** Map mnemonics to HMv1 opcodes (`0x1`, `0x2`, `0x5`).
- **Bitwise Construction:** Result = `(opcode << 12) | (address & 0x0FFF)`.
- **CLI Output:** Print the resulting 16-bit hex value prefixed with `0x`.

## 5. Final Verification
Execute the following commands to confirm implementation:
1. `pip install -e ".[dev]"` (install with test dependencies)
2. `pytest tests/unit/test_cpu.py`
3. `python3 src/hmsim/tools/hmasm.py "LOAD 100"` (Expect: `0x1064`)
3. `python3 src/hmsim/tools/hmasm.py "STORE 0x200"` (Expect: `0x2200`)
4. `python3 src/hmsim/tools/hmasm.py "ADD 0b1010"` (Expect: `0x500a`)
