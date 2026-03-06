# Software Requirements Specification: HM-Series Integrated Development Suite

This document defines the requirements for a multi-version simulator for the **HM** (Hypothetical Microprocessor) family. The suite enables architectural exploration from **HMv1** through **HMv4** using a unified GUI and CLI toolset.

---

## 1. Project Overview

This specification defines the development of a comprehensive simulation environment for the **HM** 16-bit microprocessor family, covering versions v1 through v4. The suite consists of a graphical user interface (GUI) for execution and debugging, complemented by high-performance Command Line Interface (CLI) utilities for assembly and disassembly.

---

## 2. Technical Stack & Deployment

* **Core Language:** Python 3.10+
* **GUI Framework:** PyGObject (GTK 4)
* **Development Host:** Linux (Primary)
* **Target Platforms:** Linux (Native) and Windows (via **PyInstaller** standalone executables).
* **Methodology:** Strict **Test-Driven Development (TDD)** and **Software Design Description (SDD)**.

---

## 3. Functional Requirements

### 3.1 Architectural Engine

* **Version Selection:** The user must be able to toggle between versions 1 through 4 at initialization.

* **Register Set:**
  * **PC (Program Counter):** 16-bit address tracking.
  * **IR (Instruction Register):** 16-bit instruction storage.
  * **AC (Accumulator):** 16-bit arithmetic register.
  * **SR (Status Register):** 16-bit register containing status flags (HMv2+).

* **Status Register (SR) Layout (HMv2+):**
  * **Bit 15 (SF):** Sign Flag (Result sign bit).
  * **Bit 14 (ZF):** Zero Flag (Set if result is 0).
  * **Bit 13 (EF):** Equality Flag (Set on logical equality).
  * **Bit 12 (OF):** Overflow Flag (Arithmetic overflow).
  * *Note: Bits 0–11 are reserved.*

* **Memory Model:** Implement a full **16-bit addressable memory** (65,536 words) to accommodate future indirect addressing modes.

* **Cycle Accuracy:** Instruction execution must strictly adhere to defined clock cycles: **LOAD (5)**, **STORE (15)**, and **ADD (10)**.

* **Data Format:** 16-bit signed magnitude representation.

* **Instruction Format (HMv1):** 16-bit fixed-length instructions.
  * **Opcode:** 4 bits. Occupies the most significant nibble (PDF bits 0–3 / Logic bits 15–12).
  * **Address:** 12 bits. Occupies the remaining bits (PDF bits 4–15 / Logic bits 11–0).
  * *Note: The PDF follows a 0-indexed MSB convention. The implementation uses standard 15-indexed MSB logic where Opcode = (instr >> 12) & 0xF.*

---

### 3.2 Instruction Set (Incremental Support)

Each version inherits all instructions from the previous version:

| Version | Incremental Instructions | Cycle Counts |
| --- | --- | --- |
| **HMv1** | `LOAD` (0x1), `STORE` (0x2), `ADD` (0x5) | 5, 15, 10 |
| **HMv2** | `SUB` (0x6), `JMP` (0x8), `JMPZ` (0x9) | 10, 5, 5 |
| **HMv3** | `CALL` (0xA), `RETURN` (0xB) | 5, 1 |
| **HMv4** | `LOAD` (0x3 - Indirect), `STORE` (0x4 - Indirect) | 10, 25 |

---

### 3.3 Command Line Interface (CLI)

The CLI tools must be cross-platform compatible:

* **`hmasm` (Assembler):**
  * Generates machine code based on the selected version profile.
  * Supports symbolic labels and integer (decimal), hexadecimal (`0x`), and binary (`0b`) literals.
  * Validates opcodes and address ranges.

* **`hmdas` (Disassembler):**
  * Translates hex binaries back into mnemonics based on the version-specific opcode map.

---

### 3.4 Graphical User Interface (GTK 4)

* **Version Toggle:** A global selector to switch between HMv1–HMv4 logic (preserves state when switching).
* **Integrated Code Editor:** A dual-mode text editor that supports:
  * **Assembly Input:** Direct writing of mnemonics with basic syntax highlighting.
  * **Machine Code Input:** A hex-editor mode for direct manipulation of the 16-bit binary memory image.
  * **Real-time Assembly:** Automated translation between the assembly view and the machine code view.
* **Execution Controls:** Step, Run (continuous), and Reset functionality.
* **Visual State Monitoring:** Real-time display of **PC**, **AC**, **IR**, and a scrollable memory grid.
* **Persistence:** Load/Save state as JSON files (.json).
* **Error Handling:** Error messages displayed in status bar with memory address highlighting.

### 3.5 GUI Layout & Interaction Specification

The GUI is designed as a professional IDE for architectural exploration, prioritizing clarity and real-time feedback.

#### 3.5.1 Layout Topology
*   **Header (Gtk.HeaderBar):**
    *   **Left:** File Operations (New, Open, Save), Version Selector (HMv1–HMv4).
    *   **Right:** Execution Controls (Reset, Step, Run).
*   **Main Content (Gtk.Paned - Horizontal):**
    *   **Left Pane (Editor):** Placeholder for future dual-mode editor.
    *   **Right Pane (State):** A vertical stack containing:
        1. **Register View:** Real-time display of PC, AC, IR, SR, and Cycles.
        2. **Memory Grid:** Scrollable grid showing 64KB memory with Address and Value columns.
        3. **Status Bar:** Displays "Ready" or error messages (e.g., "Error at 0x0000: Invalid opcode").

#### 3.5.2 State Synchronization (Observer Pattern)
*   **Engine-to-GUI:** Any change in the `HMEngine` state (registers or memory) emits a `state-changed` signal. Visual widgets subscribe to this signal to update their buffers.
*   **GUI-to-Engine:**
    *   Editing a line in the Assembly Editor triggers `hmasm` to update the corresponding memory address.
    *   Changing the Version Toggle re-initializes the `HMEngine` with the appropriate `ExecutionStrategy`.

#### 3.5.3 Component Architecture
*   **`src/hmsim/gui/hm_gui.py`**: Application entry point (`Gtk.Application`). Initializes the event loop and main window.
*   **`src/hmsim/gui/main_window.py`**: Main container managing the HeaderBar, Paned layout, and widget coordination. Handles file I/O (New/Open/Save) with sparse JSON state format.
*   **`src/hmsim/gui/widgets/register_view.py`**: Displays PC, AC, IR, SR in monospace hex format.
*   **`src/hmsim/gui/widgets/memory_view.py`**: `Gtk.TreeView` grid showing 64KB memory with Address and Value columns. Supports "Go to Address" search and error highlighting.
*   **`src/hmsim/gui/widgets/file_dialog.py`**: GTK4 FileDialog utilities for Open/Save operations.
*   **`src/hmsim/gui/widgets/editor_view.py`**: (Future) Dual-pane `Gtk.Notebook` with real-time assembly/disassembly sync.

---

## 4. Software Design & Testing (SDD/TDD)

### 4.1 Design Patterns

* **Strategy Pattern:** Used to swap instruction decoding logic based on the selected HM version.
* **Observer Pattern:** The Engine notifies the GUI of register/memory changes to decouple logic from the view.

### 4.2 Testing Strategy

* **Unit Tests:** Validate each opcode's effect on the **AC** and **PC**.
* **Version Regression:** Ensure that selecting **HMv1** restricts the instruction set to only `LOAD`, `STORE`, and `ADD`.
* **Binary Compatibility:** Test that the Windows build generated by PyInstaller produces identical simulation results to the Linux build.

---

## 5. Project Structure & Naming Convention

To ensure scalability and maintain clear separation of concerns, the project will follow a modular Python package structure:

```text
hmsim/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI
├── docs/                   # Engineering specifications and ISA documentation
│   ├── HM_Software_Spec.md
│   └── HM_ISA_Specification.md
├── src/
│   └── hmsim/              # Main application package
│       ├── __init__.py
│       ├── engine/         # Core Architectural Simulation
│       │   ├── __init__.py
│       │   ├── cpu.py      # Register and ALU simulation
│       │   ├── isa.py      # ISA definitions (SSOT for opcodes)
│       │   └── strategies/ # Version-specific (HMv1-v4) instruction logic
│       ├── gui/            # GTK 4 GUI Module
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   └── widgets/    # Custom Gtk.Widgets (Registers, Memory view)
│       └── tools/          # CLI Utility Suite
│           ├── __init__.py
│           ├── hmasm.py    # Assembler
│           └── hmdas.py    # Disassembler
├── tests/                  # TDD Suite
│   ├── unit/               # Opcode and logic verification
│   └── integration/        # GUI/CLI end-to-end tests
├── pyproject.toml          # Build system & dependencies
└── AGENTS.md              # Development guide for AI agents
```

### 5.1 Module Responsibilities

*   **`hmsim.engine.isa`**: Single Source of Truth (SSOT) for instruction set definitions. Defines opcodes, mnemonics, and cycle counts for all HM versions.
*   **`hmsim.engine.cpu`**: Encapsulates the 16-bit state machine. No dependencies on UI libraries.
*   **`hmsim.gui`**: Implements the GTK 4 event loop and visualizes the engine state via the Observer pattern.
*   **`hmsim.tools`**: Independent CLI scripts that utilize the `engine` for opcode validation.

---

## 6. Implementation Roadmap

The development is divided into verifiable phases. At the end of each phase, the system state can be validated using the provided execution commands.

### Phase 1: HMv1 Core & Assembler (COMPLETED)
**Objective:** Establish the 16-bit state machine and basic CLI tooling.
*   **Deliverables:** `cpu.py`, `isa.py`, `hmasm.py`, and `test_cpu.py`.
*   **Verification:**
    ```bash
    pip install -e ".[dev]"
    pytest tests/unit/test_cpu.py
    # All 6 tests pass
    ```

### Phase 2: ISA Expansion (COMPLETED)
**Objective:** Implement the Strategy pattern to support multiple instruction sets.
*   **Deliverables:** `strategies/` directory with version-specific decoding logic, HMv2 support in engine and assembler.
*   **Verification:**
    ```bash
    pip install -e ".[dev]"
    pytest tests/unit/test_cpu.py
    # All 15 tests pass (HMv1 + HMv2)
    python3 src/hmsim/tools/hmasm.py -v HMv2 "SUB 100"
    # Output: 0x6064
    ```

### Phase 3: Disassembler & Tooling Refinement
**Objective:** Complete the CLI suite with reverse-engineering capabilities. Finalizing CLI tools first ensures the core engine and ISA logic is solid before building the GUI on top.
*   **Deliverables:** `hmdas.py`.
*   **Verification:**
    ```bash
    # Round-trip test: ASM -> BIN -> DASM
    python3 src/hmsim/tools/hmasm.py "ADD 300" > temp.bin
    python3 src/hmsim/tools/hmdas.py temp.bin
    # Output should return: ADD 0x300
    ```

### Phase 4: GTK 4 Graphical Interface (IN PROGRESS)
**Objective:** Provide a visual debugger for real-time architectural exploration.

*   **Reference:** See `docs/Phase4_Implementation_Plan.md` for detailed step-by-step implementation.
*   **Deliverables:**
    *   `src/hmsim/gui/hm_gui.py` - Application entry point
    *   `src/hmsim/gui/main_window.py` - Main window container with HeaderBar
    *   `src/hmsim/gui/widgets/register_view.py` - Register display widget
    *   `src/hmsim/gui/widgets/memory_view.py` - Scrollable memory grid
    *   `src/hmsim/gui/widgets/file_dialog.py` - File dialog utilities
    *   `src/hmsim/gui/widgets/editor_view.py` - (Future) Dual-mode editor
*   **Verification:**
    *   Launch GUI: `python3 src/hmsim/gui/hm_gui.py`
    *   Header shows: New, Open, Save, Version dropdown, Reset, Step buttons
    *   Right pane shows: Registers (PC, AC, IR, SR), Memory grid, Status bar
    *   Memory grid displays 65536 addresses with Address and Value columns
    *   Clicking "Step" executes one instruction and updates register values
    *   Clicking "Reset" clears registers and memory
    *   File > Open loads JSON state file; File > Save exports sparse JSON (non-zero memory only)
    *   Error at invalid instruction shows message in status bar and highlights address in memory
    *   Switching version dropdown preserves current memory and register state

### Phase 5: ISA Expansion II (HMv3 & HMv4)
**Objective:** Implement advanced architectural features and update GUI to support them.
*   **Deliverables:**
    *   HMv3: `CALL` (0xA) and `RETURN` (0xB) with stack support.
    *   HMv4: Indirect `LOAD` (0x3) and `STORE` (0x4).
    *   GUI updates: Stack visualization for subroutines, address redirection highlighting.
*   **Verification:**
    ```bash
    pytest tests/unit/test_cpu.py
    # All tests pass including HMv3 and HMv4 opcodes
    ```

### Phase 6: Distribution & Packaging
**Objective:** Produce standalone executables for Linux and Windows.
*   **Deliverables:** `pyinstaller` build scripts and `dist/hmsim` binaries.
*   **Verification:**
    ```bash
    # Run the standalone executable
    ./dist/hmsim/hmsim --version
    ```

