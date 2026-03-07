# HM Simulator Development Guide

This document provides technical information for developers and advanced users of the HM Simulator suite. It covers command-line tools, internal architecture, and the development workflow.

## Command-Line Toolset

The HM Simulator includes a suite of CLI tools for headless execution, assembly, and disassembly. These are registered as system-wide commands when installed via `pip install -e .`.

### 1. Headless Simulator (`hmsim`)

The `hmsim` tool executes HM JSON state files without a graphical interface. This is ideal for automated testing, batch processing, or server-side execution.

**Usage:**
```bash
hmsim <state_file.json> [options]
```

**Options:**
- `-v, --version {HMv1,HMv2}`: Override the processor version (default: read from state file).
- `-m, --max-cycles N`: Set a hard limit on execution cycles to prevent infinite loops (default: 1,000,000).

**Example:**
```bash
hmsim examples/add_two_numbers.json
```

**Output:**
The tool prints a detailed execution report including:
- Final register states (PC, AC, IR, SR).
- Total clock cycles consumed (based on ISA timing).
- Non-zero memory contents.

---

### 2. HM Assembler (`hmasm`)

A utility for converting HM assembly mnemonics into 16-bit machine code. Currently, this tool supports single-instruction assembly for quick verification.

**Usage:**
```bash
hmasm [-v {HMv1,HMv2}] "<instruction>"
```

**Example:**
```bash
hmasm -v HMv1 "LOAD 100"
# Output: 0x1064
```

---

### 3. HM Disassembler (`hmdas`)

A utility for converting 16-bit machine code back into human-readable mnemonics.

**Usage:**
```bash
hmdas [-v {HMv1,HMv2}] <hex_value>
```

**Example:**
```bash
hmdas -v HMv1 0x1064
# Output: LOAD 0x064
```

---

## Development Workflow

### Environment Setup

The project uses Python 3.10+ and GTK 4. To set up a development environment:

```bash
# Clone the repository
git clone <repository_url>
cd hmsim

# Install in editable mode with development dependencies
pip install -e ".[all]"
```

### Testing

The test suite is powered by `pytest` and covers unit logic, integration, and GUI components.

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/unit/test_cpu.py
pytest tests/unit/test_cli_report.py
```

---

## Internal Architecture

The HM Simulator is built on a modular architecture that separates the execution engine from the user interfaces.

### Core Engine (`src/hmsim/engine/`)
- `cpu.py`: The `HMEngine` class maintains the 16-bit state machine.
- `isa.py`: Single source of truth for opcodes, mnemonics, and cycle counts.
- `strategies/`: Version-specific instruction decoding and execution logic.
- `state.py`: Handles serialization/deserialization of JSON state files.

### GUI (`src/hmsim/gui/`)
A GTK 4 implementation using the Observer pattern. The GUI listens for `state-changed` signals from the `HMEngine` to update its visual components.

### Tools (`src/hmsim/tools/`)
Standalone CLI utilities that wrap the core engine logic for specialized tasks.
