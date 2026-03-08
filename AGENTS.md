# AGENTS.md - HM Simulator Development Guide

HM-Sim is a multi-version simulator for the HM (Hypothetical Microprocessor) 16-bit processor family (v1-v4). Python 3.10+, pytest for testing, PyGObject (GTK 4) for GUI.

---

## 1. Build, Lint, and Test Commands

### Running Tests

```bash
pytest                      # Run all unit tests
pytest -v                   # Verbose output
pytest tests/unit/test_cpu.py              # Single test file
pytest tests/unit/test_cpu.py::test_load_instruction  # Single test function
pytest tests/unit/gui/           # GUI tests only
pytest tests/unit/gui/test_controls.py    # Specific GUI test module
pytest -k "test_load"       # Tests matching pattern
pytest -s                   # Show print output
pytest --cov=src/hmsim      # With coverage
```

### Running the Application

```bash
hmsim                       # Run GUI
hmsim_cli <state_file.hm>   # Run headless simulator
hmasm "LOAD 100"            # Run assembler
hmdas 0x1234                # Run disassembler
pip install -e ".[dev]"     # Install with test deps
pip install -e ".[all]"     # Install with GUI deps
```

---

## 2. Code Style Guidelines

### Import Conventions

```python
# Standard library first, then third-party, then local (relative imports)
import sys
from typing import Optional, List, Dict
import pytest
from ..engine.cpu import HMv1Engine
from .cpu import CPU
```

### Formatting

- Max 100 characters per line
- 4 spaces (no tabs)
- Two blank lines between top-level definitions, one between methods

### Type Annotations

```python
def execute(self, opcode: int, address: int) -> int:
    cycles: int = 0
    return cycles

registers: Dict[str, int] = {}
memory: List[int] = [0] * 65536
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `cpu.py`, `hm_engine.py` |
| Classes | PascalCase | `HMv1Engine`, `MemoryBus` |
| Functions/methods | snake_case | `execute()`, `get_register()` |
| Constants | UPPERCASE | `MAX_MEMORY`, `OPCODES` |
| Private methods | underscore prefix | `_decode()`, `_update_state()` |
| Test functions | `test_<description>` | `test_load_instruction()` |

### Error Handling

- Use specific exceptions (`ValueError`, `TypeError`, `NotImplementedError`)
- Include descriptive messages
- Validate at public API boundaries

```python
def load(self, address: int) -> int:
    if not 0 <= address < 65536:
        raise ValueError(f"Address out of range: {address}")
    return self._memory[address]
```

### Docstrings

Use Google-style docstrings for all public functions.

---

## 3. Project Structure

```
hmsim/
├── .github/
│   └── workflows/
│       └── ci.yml      # GitHub Actions CI
├── src/hmsim/
│   ├── __init__.py
│   ├── engine/         # Core simulation (no UI deps)
│   │   ├── __init__.py
│   │   ├── cpu.py       # HMEngine, HMv1Engine
│   │   ├── isa.py       # SSOT for opcodes
│   │   └── strategies/  # ExecutionStrategy, HMv1Strategy, HMv2Strategy
│   ├── gui/             # GTK 4 GUI Module
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── widgets/     # Custom Gtk.Widgets
│   └── tools/           # CLI Tools
│       ├── __init__.py
│       ├── hmasm.py     # Assembler (supports -v flag)
│       └── hmdas.py     # Disassembler
├── tests/
│   ├── __init__.py
│   └── unit/            # Opcode and logic tests
│       ├── test_cpu.py
│       ├── test_engine_integration.py
│       ├── test_disassembler.py
│       ├── test_json_state.py
│       └── gui/         # GUI tests (refactored)
│           ├── __init__.py
│           ├── conftest.py
│           ├── test_setup.py
│           ├── test_controls.py
│           ├── test_simulation.py
│           ├── test_version.py
│           ├── test_io.py
│           └── test_feedback.py
├── docs/
├── pyproject.toml
└── AGENTS.md
```

---

## 4. Design Patterns

1. **Strategy Pattern:** Version-specific instruction decoding (HMv1-v4)
2. **Observer Pattern:** Engine notifies GUI of register/memory changes
3. **State Machine:** CPU as 16-bit state machine

---

## 5. Testing Guidelines

```python
import pytest
from hmsim.engine.cpu import HMv1Engine

class TestHMv1Engine:
    @pytest.fixture
    def engine(self):
        return HMv1Engine()

    def test_load_instruction(self, engine):
        engine._memory[0x0100] = 0x1234
        engine.execute(0x1, 0x0100)
        assert engine.ac == 0x1234
```

- Test file naming: `test_<module>.py`
- Test class naming: `Test<ClassName>`
- One assertion per test when practical

---

## 6. Version-Specific Behavior

| Version | Instructions | Notes |
|---------|--------------|-------|
| HMv1 | LOAD, STORE, ADD | Base instruction set |
| HMv2 | + SUB, JMP, JMPZ | Adds status register (SR) |
| HMv3 | + CALL, RETURN | Adds subroutine support |
| HMv4 | + Indirect LOAD/STORE | Adds indirect addressing |

---

## 7. References

- ISA Specification: `docs/HM_ISA_Specification.md`
- Software Specification: `docs/HM_Software_Spec.md`
- GitHub CI: `.github/workflows/ci.yml`
