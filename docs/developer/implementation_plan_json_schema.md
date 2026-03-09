# Implementation Plan: HM State JSON Schema & Cleanup

**Role:** Senior Systems Architect
**Objective:** Directive for Implementation Agent to formalize state persistence and optimize test artifacts.

## 1. Overview
The goal is to transition from an implicit state format to an explicit, validated contract using JSON Schema. This ensures that as the HM engine versions evolve, the data remains consistent, maintainable, and backward compatible.

## 2. Technical Requirements
- **Library:** Use the `jsonschema` Python library for validation.
- **Scope:**
    - Create a versioned JSON Schema.
    - Integrate validation into the `HMEngine` load/save lifecycle.
    - Remove the redundant `tests/fixtures/sample_state.hm`.

## 3. Step-by-Step Execution Strategy

### Step 1: Requirements Extraction
- **Code Analysis:** Inspect `src/hmsim/engine/cpu.py` and `src/hmsim/engine/state.py` to identify all required and optional fields (PC, AC, IR, SR, total_cycles, total_instructions, text, data, setup).
- **Type Mapping:** Determine exact types (e.g., integers for registers, hex-string patterns for memory keys, objects for sections).

### Step 2: Schema Definition
- **Drafting:** Create a JSON Schema file (e.g., `src/hmsim/engine/schema.json`) that defines the structure for an HM state file.
- **Constraints:** Implement regex patterns for memory addresses (e.g., `^0x[0-9A-F]{4}$`) and value ranges (0-65535).
- **Polymorphism:** Use conditional logic (`if/then/else` or `allOf`) in the schema to handle version-specific requirements (e.g., SR is more critical in HMv2+).

### Step 3: Integration & Validation Logic
- **Validation Hook:** Modify the state loading process in `src/hmsim/engine/state.py` to perform a schema check immediately after JSON parsing.
- **Error Handling:** Implement descriptive error reporting that tells the user *exactly* which field failed validation.
- **Backward Compatibility:** Ensure the validation logic allows for missing optional fields from older versions (HMv1) while enforcing them for newer ones.

### Step 4: Verification & Regression Testing
- **Schema Tests:** Add new unit tests to `tests/unit/test_json_state.py` that attempt to load "Negative Cases" (e.g., state files with out-of-range AC values or malformed hex strings) to confirm rejection.
- **Consistency Check:** Run the existing integration tests (`tests/integration/test_consistency.py`) to ensure schema enforcement doesn't break current workflows.

### Step 5: Artifact Decommissioning
- **Fixture Audit:** Confirm that `tests/fixtures/sample_state.hm` is no longer referenced in any test or documentation.
- **Removal:** Delete the file and any associated swap files from the repository.

## 4. Success Metrics
- **Validation Pass:** All current valid state files pass the schema check.
- **Validation Fail:** Files with logical errors (overlapping regions, invalid opcodes) are rejected with clear messages.
- **Lean Repository:** The `tests/fixtures/` directory is pruned of unused artifacts.

## 5. Contingencies
- **Performance:** If schema validation significantly slows down GUI loading, plan for a "Lazy Validation" approach or optimized schema caching.
- **Dependency Missing:** If `jsonschema` is not in `pyproject.toml`, add it to the project dependencies first.
