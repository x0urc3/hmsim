# HM Simulator Development Guide

This document provides technical information for developers and advanced users of the HM Simulator suite. It covers command-line tools, internal architecture, and the development workflow.

## Command-Line Toolset

The HM Simulator includes a suite of CLI tools for headless execution, assembly, and disassembly. These are registered as system-wide commands when installed via `pip install -e .`.

### 1. Headless Simulator (`hmsim_cli`)

The `hmsim_cli` tool executes HM JSON state files without a graphical interface. This is ideal for automated testing, batch processing, or server-side execution.

**Usage:**
```bash
hmsim_cli <state_file.hm> [options]
```

**Options:**
- `-v, --version {HMv1,HMv2}`: Override the processor version (default: read from state file).
- `-m, --max-cycles N`: Set a hard limit on execution cycles to prevent infinite loops (default: 1,000,000).

**Example:**
```bash
hmsim_cli examples/add_two_numbers.hm
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

## Graphical User Interface (GTK 4)

The HM Simulator features a modern GTK 4 interface for real-time architectural exploration.

**Launch:**
```bash
# Using the entry point script
python3 src/hmsim/gui/hm_gui.py

# Or if installed via pip
hmsim
```

### Key Features:
- **Assembly Editor**: Real-time assembly of mnemonics into machine code. Supports inline comments and basic syntax highlighting.
- **Register View**: Live display of active Engine version, PC, AC, IR, SR, and execution cycles.
- **Memory Grid**: Scrollable 64KB memory view with "Go to Address" functionality. Supports direct cell editing (hex/decimal) which triggers real-time re-disassembly in the Assembly Editor.
- **Execution Controls**: Single-step execution (F10), continuous run (F5), and reset (F12).
- **Simulator Setup**: Hot-swapping between HMv1 through HMv4 architectures and defining memory regions.
- **Persistence**: Load and save complete simulator states as `.hm` JSON files (including setup metadata).


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

## Distribution & Packaging

The HM Simulator can be packaged as standalone executables for distribution without requiring Python or GTK4 installation.

### Build Script

The `scripts/build_gui.py` script uses PyInstaller to create self-contained executables:

```bash
# From project root
python scripts/build_gui.py
```

This builds all tools into the `dist/` directory:
- `hmsim` - GUI application
- `hmsim_cli` - Headless simulator
- `hmasm` - Assembler
- `hmdas` - Disassembler
- `_internal/` - Shared libraries
- `examples/` - Sample programs
- `docs/` - User documentation
- `LICENSE`, `NOTICE` - Legal files

### Platform-Specific Notes

**Linux:**
- Builds require GTK4 libraries installed on the build system
- Output goes to `dist/` directory (not archived)
- Run directly: `./dist/hmsim` or `./dist/hmasm "LOAD 0x100"`

**Windows (MSYS2):**
- Requires MSYS2 with MINGW64 or UCRT64 environment
- Install dependencies: `pacman -S mingw-w64-x86_64-python mingw-w64-x86_64-python-gobject mingw-w64-x86_64-gtk4`
- Output: Creates `hmsim_windows.zip` archive

**Windows (CI):**
- Use GitHub Actions workflow `.github/workflows/package_windows.yml`
- Trigger via: Release publication or manual workflow dispatch
- Downloads: `hmsim_windows.zip` artifact

### Offline Help

The GUI's Help menu uses documentation bundled in the package:
- Source: `docs/user/Tutorial.md`, `docs/user/hmsim_User_Guide.md`
- Bundled to: `dist/_internal/docs/`
- The application detects running from frozen bundle and locates docs appropriately.

---

## Internal Architecture

The HM Simulator is built on a modular architecture that separates the execution engine from the user interfaces.

### Core Engine (`src/hmsim/engine/`)
- `cpu.py`: The `HMEngine` class maintains the 16-bit state machine. It defines `VALID_VERSIONS` as the source of truth for supported architectures.
- `isa.py`: Single source of truth for opcodes, mnemonics, and cycle counts.
- `strategies/`: Version-specific instruction decoding and execution logic.
- `state.py`: Handles serialization/deserialization of JSON state files, including the `setup` block. Validates all `.hm` files against a strict JSON Schema (`schema.json`).

### GUI (`src/hmsim/gui/`)
A GTK 4 implementation using the Observer pattern. The GUI listens for `state-changed` signals from the `HMEngine` to update its visual components.

#### Version Management and Setup
- **`_on_setup`**: Triggered by the "Setup" menu. It spawns the `SetupDialog` and, upon application, orchestrates the update of memory regions and potential engine re-initialization.
- **`_on_version_changed`**: Centralized logic for hot-swapping engines. It preserves the current memory, registers, and comments, then re-assembles the program text for the new architecture.

### Markdown Renderer (`src/hmsim/gui/utils/markdown_renderer.py`)
A custom Markdown-to-GTK-TextBuffer renderer built on `markdown-it-py`. It supports:
- **Rich Styling:** Headings (h1-h3), bold, italic, and inline code.
- **Tables:** Aligned text-based tables with monospaced font and cell formatting.
- **Theme Support:** Uses semi-transparent backgrounds for code blocks to remain visible on both light and dark system themes.
- **Nested Formatting:** Employs a tag stack and recursive token processing for accurate rendering of nested styles.
