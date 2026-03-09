# Implementation Plan: Bracketed Indirect Addressing Syntax

**Role:** Senior Compiler Engineer / ISA Architect

## 1. Objective
The goal is to modernize the HM assembly syntax by introducing bracket notation for indirect memory access. Specifically, the mnemonics `LOAD_INDIRECT <address>` and `STORE_INDIRECT <address>` will be **completely removed** and replaced by `LOAD (<address>)` and `STORE (<address>)`. This change improves architectural consistency and aligns the HM ISA with established assembly language conventions where brackets signify dereferencing.

## 2. Preparation / Requirements
- **Codebase Access:** Access to `src/hmsim/engine/isa.py`, `src/hmsim/tools/hmasm.py`, and `src/hmsim/tools/hmdas.py`.
- **Documentation:** Access to `docs/reference/HM_ISA_Specification.md`.
- **Testing Framework:** `pytest` environment for unit and integration testing.
- **Backups/Git:** Ensure a clean git state to allow for surgical reverts if regression is detected.

## 3. Step-by-Step Execution

### Phase 1: Assembler Logic Enhancement (`hmasm.py`)
1.  **Pattern Recognition:** Modify the `assemble` function to detect if the operand (address string) is enclosed in parentheses.
2.  **Opcode Selection Logic:**
    - If mnemonic is `LOAD` and operand is `(address)`, select `OP_LOAD_INDIRECT`.
    - If mnemonic is `LOAD` and operand is `address`, select `OP_LOAD`.
    - Repeat similar logic for `STORE`.
3.  **Mnemonic Removal:** Remove `LOAD_INDIRECT` and `STORE_INDIRECT` from the `HMV4_ISA` dictionary and the `assemble` function. Ensure the assembler throws an "Unknown mnemonic" error if these are encountered.
4.  **Error Handling:** Implement strict validation for bracket parity. Throw `ValueError` for `LOAD (100`, `LOAD 100)`, or `LOAD ()`.

### Phase 2: Disassembler Logic Update (`hmdas.py`)
1.  **Formatting Logic:** Update the `disassemble` function.
2.  **Conditional Output:**
    - If opcode is `OP_LOAD_INDIRECT` (0x3), format output as `LOAD (0xXXX)`.
    - If opcode is `OP_STORE_INDIRECT` (0x4), format output as `STORE (0xXXX)`.
    - Ensure other instructions remain unaffected.

### Phase 3: ISA Specification & Internal Constants (`isa.py`)
1.  **Internal Mappings:** Remove `LOAD_INDIRECT` and `STORE_INDIRECT` from `HMV4_ISA`. Add any necessary logic to handle the new unified mnemonics if required for internal lookups.
2.  **Mnemonic Map:** Update `HMV4_OPCODE_TO_MNEMONIC` so that 0x3 maps back to `LOAD` and 0x4 maps to `STORE` (the disassembler will append brackets based on the opcode).

### Phase 4: Documentation & Examples
1.  **Reference Update:** Modify `docs/reference/HM_ISA_Specification.md` to reflect the removal of `LOAD_INDIRECT`/`STORE_INDIRECT` and show the new bracketed syntax in the Instruction Set Summary table.
2.  **Example Migration:** Update `examples/indirect_addressing.hm` and any other `.hm` files in `examples/` to use the new syntax.
3.  **User Guide:** (Optional) Update `docs/user/hmsim_User_Guide.md` if it contains assembly examples.

### Phase 5: Verification & Testing
1.  **Unit Tests:** Add new test cases to `tests/unit/test_disassembler.py` and `tests/unit/test_json_state.py`.
2.  **Integration Tests:** Run `tests/integration/test_consistency.py` to ensure that saving and loading `.hm` files still works perfectly with the new syntax.

## 4. Test Cases for Edge Situations

| Case | Input | Expected Output / Behavior |
|------|-------|----------------------------|
| **Standard Indirect** | `LOAD (0x0100)` | Assembles to 0x3100 |
| **Standard Direct** | `LOAD 0x0100` | Assembles to 0x1100 |
| **Whitespace** | `LOAD  ( 0x0100 ) ` | Assembles to 0x3100 (robust stripping) |
| **Missing Close** | `LOAD (0x0100` | `ValueError: Malformed indirect address` |
| **Missing Open** | `LOAD 0x0100)` | `ValueError: Malformed indirect address` |
| **Empty Brackets** | `LOAD ()` | `ValueError: Missing address in indirect operand` |
| **Nested Brackets** | `LOAD ((100))` | `ValueError` (unless multi-level indirection is added) |
| **Direct with Parentheses** | `ADD (100)` | `ValueError` (if ADD doesn't support indirect) |
| **Removed Mnemonic** | `LOAD_INDIRECT 100` | `ValueError: Unknown mnemonic` (enforcing removal) |

## 5. Success Metrics
- **Round-trip Integrity:** `assemble("LOAD (100)")` followed by `disassemble()` returns `"LOAD (0x064)"`.
- **Zero Regression:** All existing HMv1, HMv2, and HMv3 tests pass without modification.
- **Documentation Consistency:** The ISA specification matches the simulator's behavior exactly and no longer lists the old mnemonics.

## 6. Contingencies / Advice
- **Clean Break:** Since the mnemonics are being removed, ensure that any "auto-complete" or "syntax highlighting" in the GUI (if implemented) is also updated to avoid user confusion.
- **Parsing Complexity:** Avoid regex for simple bracket parsing; string `startswith` and `endswith` are more performant and less error-prone for this specific ISA.
- **Error Messages:** Provide helpful error messages when encountering removed mnemonics, potentially suggesting the new syntax.
