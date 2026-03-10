# Software Requirements Specification: HM-Series Integrated Development Suite

This document defines the requirements for a multi-architecture simulator for the **HM** (Hypothetical Microprocessor) family. The suite enables architectural exploration from **HMv1** through **HMv4** using a unified GUI and CLI toolset.

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

* **Architecture Selection:** The user must be able to toggle between versions 1 through 4 via the **Simulator Setup** dialog. The current active architecture must be clearly indicated in the main UI.

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

Each architecture inherits all instructions from the previous version:

| Version | Incremental Instructions | Cycle Counts |
| --- | --- | --- |
| **HMv1** | `LOAD` (0x1), `STORE` (0x2), `ADD` (0x5) | 5, 15, 10 |
| **HMv2** | `SUB` (0x6), `JMP` (0x8), `JMPZ` (0x9) | 10, 5, 5 |
| **HMv3** | `CALL` (0xA), `RETURN` (0xB) | 5, 1 |
| **HMv4** | `LOAD` (0x3 - Indirect), `STORE` (0x4 - Indirect) | 10, 25 |

---

### 3.3 Command Line Interface (CLI)

The CLI tools must be cross-platform compatible:

* **`hmsim_cli` (Headless Simulator):**
  * Executes program states from JSON files without a GUI.
  * Supports cycle limits and provides a detailed final execution report.
  * Essential for automated regression testing and server-side processing.

* **`hmasm` (Assembler):**
  * Generates machine code based on the selected version profile.
  * Currently supports single-instruction assembly.

* **`hmdas` (Disassembler):**
  * Translates hex binaries back into mnemonics based on the version-specific opcode map.

---

### 3.4 Graphical User Interface (GTK 4)

* **Architecture Toggle:** A global selector to switch between HMv1–HMv4 logic (preserves state when switching).
* **Integrated Code Editor:** A dual-mode text editor that supports:
  * **Assembly Input:** Direct writing of mnemonics with basic syntax highlighting.
  * **Machine Code Input:** A direct-editing mode in the memory grid for manipulation of 16-bit binary memory values.
  * **Real-time Sync:** Automated translation between the assembly editor and the memory grid. Editing assembly updates machine code, and editing memory directly triggers re-disassembly in the editor.
* **Execution Controls:** Step, Run (continuous), and Reset functionality.
* **Visual State Monitoring:** Real-time display of **PC**, **AC**, **IR**, and a scrollable memory grid.
* **Persistence:** Load/Save state as HM files (.hm) with structured text, data, and setup sections.
* **Session-Bound Provenance & Audit:**
    * **Metadata Headers:** Every file must persist a `metadata` object containing `created_at`, `updated_at`, and `software_version`.
    * **Audit Log:** An automated `log` array that tracks every unique environment (OS, hostname, platform) where the file has been modified.
    * **Session Continuity:** Metadata must be bound to the simulation engine, not the file, ensuring that "Save As" correctly transfers the entire history of the session.
    * **State-Dependent Persistence:** "File > New" resets the engine's internal session metadata, whereas loading a file inherits its ancestral history.
* **Error Handling:** Error messages displayed in status bar with memory address highlighting.

### 3.5 GUI Layout & Interaction Specification

The GUI is designed as a professional IDE for architectural exploration, prioritizing clarity and real-time feedback.

#### 3.5.1 Layout Topology
*   **Header (Gtk.HeaderBar):**
    *   **Left:** File Operations (New, Open, Save).
    *   **Center:** HM Simulator Title.
* **Main Content (Gtk.Box - Vertical):**
    *   **MenuBar (Gtk.PopoverMenuBar):** File, Run, Setup, Help menus.
    *   **Toolbar (Gtk.Box):** Reset, Run, Step buttons.
    *   **Paned Content (Gtk.Paned - Horizontal):**
        *   **Left Pane (Editor):** `Gtk.TextView` for assembly input with real-time assembly.
        *   **Right Pane (State):** A vertical stack containing:
            1. **Active Engine Indicator:** Centered label showing "Engine: HMv?".
            2. **Register View:** Real-time display of PC, AC, IR, SR, and Cycles.
            3. **Memory Grid:** Scrollable grid showing 64KB memory with Address and Value columns.
            4. **Status Bar:** Displays "Ready" or error messages.


#### 3.5.2 State Synchronization (Observer Pattern)
*   **Engine-to-GUI:** Any change in the `HMEngine` state (registers or memory) emits a notification to observers. Visual widgets subscribe to this to update their buffers.
*   **GUI-to-Engine:**
    *   Editing a line in the Assembly Editor triggers `hmasm` to update the corresponding memory address in real-time (with a slight debounce).
    *   Editing a value in the Memory Grid triggers the disassembler to update the Assembly Editor. This action automatically removes the comment for the edited address to ensure the documentation reflects the new code.
    *   Changing the Architecture via the **Setup Dialog** re-initializes the `HMEngine` with the appropriate `ExecutionStrategy` and re-assembles the editor text.

#### 3.5.3 Component Architecture
*   **`src/hmsim/gui/hm_gui.py`**: Application entry point (`Gtk.Application`). Initializes the event loop, MenuBar, and main window.
*   **`src/hmsim/gui/main_window.py`**: Main container managing the HeaderBar, Paned layout, and widget coordination. Handles file I/O (New/Open/Save) with sparse JSON state format.
*   **`src/hmsim/gui/widgets/setup_dialog.py`**: A configuration dialog for switching processor architectures and defining memory regions (Text/Data).
*   **`src/hmsim/gui/widgets/register_view.py`**: Displays active engine version, PC, AC, IR, SR, and cycles in monospace hex format.
*   **`src/hmsim/gui/widgets/memory_view.py`**: `Gtk.TreeView` grid showing 64KB memory with Address and Value columns. Supports "Go to Address" search and error highlighting.
*   **`src/hmsim/gui/widgets/file_dialog.py`**: GTK4 FileDialog utilities for Open/Save operations.
*   **`src/hmsim/gui/widgets/editor_view.py`**: `Gtk.TextView` with bi-directional assembly/disassembly synchronization with the memory grid and error reporting.

---

## 4. Software Design & Testing (SDD/TDD)

### 4.1 Design Patterns

* **Strategy Pattern:** Used to swap instruction decoding logic based on the selected HM architecture.
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
│   ├── user/               # User-facing guides
│   │   ├── hmsim_User_Guide.md
│   │   └── Tutorial.md
│   ├── reference/          # Technical reference data
│   │   ├── HM_ISA_Specification.md
│   │   └── HMSim_File_Format.md
│   └── developer/          # Internal architecture and dev workflow
│       ├── HM_Software_Spec.md
│       └── DEVELOPMENT.md
├── src/
│   └── hmsim/              # Main application package
│       ├── __init__.py
│       ├── engine/         # Core Architectural Simulation
│       │   ├── __init__.py
│       │   ├── cpu.py      # Register and ALU simulation
│       │   ├── isa.py      # ISA definitions (SSOT for opcodes)
│       │   ├── state.py    # JSON persistence logic
│       │   └── strategies/ # Version-specific (HMv1-v4) instruction logic
│       ├── gui/            # GTK 4 GUI Module
│       │   ├── __init__.py
│       │   ├── hm_gui.py   # Entry point
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

---

For implementation details, see:
- **Distribution & Packaging**: [Development Guide](DEVELOPMENT.md#distribution--packaging)
- **CLI Tools & Architecture**: [Development Guide](DEVELOPMENT.md)

