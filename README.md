# HM Simulator

An educational 16-bit microprocessor simulator for learning Instruction Set Architecture (ISA) concepts.

## What is HM Simulator?

HM (Hypothetical Microprocessor) Simulator is a multi-version emulator designed specifically for teaching and learning microprocessor fundamentals. The simulator implements a clean, 16-bit RISC-style processor architecture that closely follows the educational examples found in William Stallings' classic textbook *Computer Organization and Architecture*.

The HM processor family evolves through four versions (HMv1 through HMv4), each adding new capabilities. This incremental design mirrors the historical evolution of real microprocessors, making it an ideal tool for:

- **Students** learning computer architecture for the first time
- **Educators** teaching ISA concepts with hands-on experimentation
- **Hobbyists** curious about how CPUs work under the hood

Unlike complex modern processors, HM uses a simple accumulator-based architecture that keeps the focus on fundamental concepts: instruction fetching, decoding, execution, and the mechanics of memory access.

## Why Learn with HM?

### Incremental Complexity

The four HM versions provide a natural learning progression:

- **HMv1**: Master the basics of LOAD, STORE, and ADD operations
- **HMv2**: Add branching (JMP, JMPZ) and learn about status flags
- **HMv3**: Understand subroutines with CALL and RETURN
- **HMv4**: Explore indirect addressing for pointer-like operations

Each version inherits all instructions from the previous version, so you can start simple and gradually tackle more advanced concepts.

### Cycle-Accurate Simulation

Every instruction simulates the exact number of clock cycles defined in the ISA. This helps you understand:

- Why LOAD takes 5 cycles but STORE takes 15
- How memory access time affects program performance
- The relationship between instruction complexity and execution time

### Clean 16-bit Architecture

The HM processor uses a unified 16-bit word for both instructions and data. This simplicity lets you focus on learning concepts without getting bogged down in architectural complexity.

## Understanding the Architecture

### Registers

The HM processor contains four primary registers:

| Register | Name | Description |
|----------|------|-------------|
| **PC** | Program Counter | A 16-bit register that holds the memory address of the next instruction to fetch |
| **IR** | Instruction Register | A 16-bit register that holds the current instruction being decoded/executed |
| **AC** | Accumulator | The primary data register used for all arithmetic operations |
| **SR** | Status Register | Contains flags (Sign, Zero) - available in HMv2 and later |
| **Cycles** | Total Cycles | Cumulative cycle count since last reset (displayed in register panel) |

### Memory Model

The HM processor has a flat 64KB (65,536 words) unified memory space. Both instructions and data occupy the same address space, using 16-bit words.

- Memory addresses: 0x0000 to 0xFFFF
- Each memory location holds a 16-bit value

### Instruction Format

All HM instructions are exactly 16 bits wide, using a fixed-length encoding scheme:

```
bits 15-12: Opcode (4 bits) - identifies the operation
bits 11-0:  Address (12 bits) - memory address (0-4095)
```

This simple format makes it easy to understand how the CPU decodes each instruction.

### Data Format

HM uses 16-bit signed magnitude representation for integers:

- **Bit 15**: Sign bit (0 = positive, 1 = negative)
- **Bits 0-14**: Magnitude (absolute value)

Note: This differs from two's complement, which is common in modern processors.

## Instruction Set Reference

Each HM version adds new instructions while preserving all previous ones:

### HMv1 - Base Instruction Set

| Opcode | Mnemonic | Cycles | Description |
|--------|----------|--------|-------------|
| 0x1 | LOAD | 5 | Load value from memory into AC |
| 0x2 | STORE | 15 | Store AC value to memory |
| 0x5 | ADD | 10 | Add memory value to AC |

### HMv2 - Branching and Status Flags

| Opcode | Mnemonic | Cycles | Description |
|--------|----------|--------|-------------|
| 0x6 | SUB | 10 | Subtract memory value from AC |
| 0x8 | JMP | 5 | Unconditional jump to address |
| 0x9 | JMPZ | 5 | Jump to address if Zero Flag is set |

### HMv3 - Subroutine Support

| Opcode | Mnemonic | Cycles | Description |
|--------|----------|--------|-------------|
| 0xA | CALL | 5 | Call subroutine: save PC+1 in AC, jump to address |
| 0xB | RETURN | 1 | Return from subroutine: jump to address in AC |

### HMv4 - Indirect Addressing

| Opcode | Mnemonic | Cycles | Description |
|--------|----------|--------|-------------|
| 0x3 | LOAD (indirect) | 10 | Load AC from address stored in memory |
| 0x4 | STORE (indirect) | 25 | Store AC to address stored in memory |

## Getting Started

### Installation

The HM Simulator can be installed as a Python package:

```bash
pip install -e .
```

This will register the `hmsim_gui` command to launch the simulator.

### Launching the Simulator

The HM Simulator provides a graphical user interface (GUI) built with GTK 4. To start the simulator, run:

```bash
hmsim_gui
```

Or using the source path:
```bash
python3 src/hmsim/gui/hm_gui.py
```

### CLI Tools and Development

For developers and advanced users, the suite includes headless execution (`hmsim`), assembly (`hmasm`), and disassembly (`hmdas`) tools.

For detailed information on using these tools and setting up a development environment, please refer to the [Development Guide](docs/DEVELOPMENT.md).

## The GUI Layout


When the simulator starts, you'll see:

- **Header Bar** (top): Contains file operations (New, Open, Save), version selector, and execution controls
- **Main Area** (center): Editor for entering your program (assembly or machine code)
- **Right Panel** (right): Shows register values (PC, AC, IR, SR) and memory contents
- **Status Bar** (bottom): Displays simulator status and error messages

### Selecting Your HM Version

Use the version dropdown in the header bar to select which HM version to simulate:

- **HMv1**: Basic LOAD/STORE/ADD operations
- **HMv2**: Adds SUB, JMP, JMPZ
- **HMv3**: Adds CALL, RETURN
- **HMv4**: Adds indirect addressing

Switching versions updates the available instructions while preserving your current memory contents.

### Execution Controls

- **Run**: Execute instructions continuously at high speed (~60,000+ instructions/sec). Displays total cycles in real-time.
- **Step**: Execute one instruction and advance the program counter
- **Reset**: Clear all registers (PC, AC, IR, SR, Cycles) and memory

## Tutorial: Your First Program

Let's write a simple program that adds two numbers together. This tutorial walks you through the complete process.

### The Problem

We want to compute: 5 + 7 = 12

### Step 1: Write the Program

Our program will:

1. LOAD the first number (5) from memory into the accumulator
2. ADD the second number (7) to the accumulator
3. STORE the result to memory for safekeeping

Here's how we express this in HM assembly:

| Address | Instruction | Operation |
|---------|-------------|------------|
| 0 | LOAD 10 | Load value from address 10 into AC |
| 1 | ADD 11 | Add value at address 11 to AC |
| 2 | STORE 12 | Store AC value to address 12 |

### Step 2: Store the Data

We need to place our data values in memory. Let's put them at addresses 10, 11, and 12:

- Address 10: 5 (first number)
- Address 11: 7 (second number)
- Address 12: 0 (result storage - initially empty)

### Step 3: Enter and Run

1. Launch the HM Simulator
2. Select HMv1 from the version dropdown
3. Enter the instructions at addresses 0, 1, 2
4. Enter the data values at addresses 10, 11, 12
5. Click **Step** three times to execute each instruction
6. Watch the AC register change: 0 → 5 → 12 → 12
7. Check address 12: it now contains 12 (our answer!)

### Understanding What Happens

Let's trace through each instruction:

**Instruction at address 0: LOAD 10**
1. CPU fetches instruction 0x100A (LOAD from address 10)
2. CPU decodes: opcode=1 (LOAD), address=10
3. CPU executes: reads memory at address 10 (value=5), stores in AC
4. AC now contains 5
5. PC increments to 1

**Instruction at address 1: ADD 11**
1. CPU fetches instruction 0x500B (ADD from address 11)
2. CPU decodes: opcode=5 (ADD), address=11
3. CPU executes: reads memory at address 11 (value=7), adds to AC
4. AC now contains 5 + 7 = 12
5. PC increments to 2

**Instruction at address 2: STORE 12**
1. CPU fetches instruction 0x200C (STORE to address 12)
2. CPU decodes: opcode=2 (STORE), address=12
3. CPU executes: writes AC value (12) to memory address 12
4. Memory address 12 now contains 12
5. PC increments to 3

Congratulations! You've written and executed your first HM program.

## GUI Controls Reference

### File Operations

- **New**: Reset the simulator to initial state (clears registers and memory)
- **Open**: Load a saved state from a JSON file
- **Save**: Save the current state to a JSON file

### Execution Controls

- **Step**: Execute one instruction and update all displays
- **Reset**: Clear all registers (PC, AC, IR, SR = 0) and memory (all zeros)

### Version Selector

Drop-down menu to switch between:

- HMv1 (LOAD, STORE, ADD)
- HMv2 (+ SUB, JMP, JMPZ)
- HMv3 (+ CALL, RETURN)
- HMv4 (+ Indirect LOAD/STORE)

### Memory Editor

You can directly edit memory contents by clicking on a cell in the memory view. Values can be entered in hexadecimal format (0x prefix) or decimal.

### Register Display

The register panel shows current register values in hexadecimal format:

- PC: Program Counter (next instruction address)
- AC: Accumulator (arithmetic result)
- IR: Instruction Register (current instruction)
- SR: Status Register (flags - HMv2+ only)
- Cycles: Total execution cycles since last reset

## Learning Path Suggestions

### Beginner Level - Master HMv1

Start by becoming comfortable with the three basic operations:

1. **LOAD**: Understand how data moves from memory to the CPU
2. **STORE**: Understand how data moves from the CPU to memory
3. **ADD**: Understand how the ALU performs arithmetic

Practice by writing programs that:
- Load values, add them together, store the result
- Chain multiple additions
- Move values between memory locations

### Intermediate Level - Move to HMv2

Once comfortable with HMv1, add branching:

1. **SUB**: Learn subtraction (and the concept of negative numbers)
2. **JMP**: Understand unconditional jumps and program flow
3. **JMPZ**: Learn conditional execution based on flags

Practice by writing programs that:
- Count down from a number to zero
- Implement loops
- Create simple decisions (if zero, do something)

### Advanced Level - HMv3 Subroutines

Add procedure calls:

1. **CALL**: Save return address and jump to subroutine
2. **RETURN**: Restore execution to after the call

Practice by writing programs that:
- Extract common code into reusable subroutines
- Implement a simple function with parameters (via memory)
- Create a loop using a subroutine

### Expert Level - HMv4 Indirect Addressing

Master pointer operations:

1. **LOAD (indirect)**: Load from an address stored in memory
2. **STORE (indirect)**: Store to an address stored in memory

Practice by writing programs that:
- Implement arrays and array indexing
- Use pointer arithmetic
- Create data structures (records)

## Example Programs

The `examples/` directory contains sample programs to study:

- **add_two_numbers.hm**: A complete HMv1 program that adds 5 + 7 = 12

Load this example in the simulator to see how a complete program looks in saved state format.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Learning More

For detailed technical specifications, refer to the documentation in the `docs/` folder:

- **HM_ISA_Specification.md**: Complete ISA documentation
- **HM_Software_Spec.md**: Technical software specification
- **HMSim_File_Format.md**: State file format documentation
