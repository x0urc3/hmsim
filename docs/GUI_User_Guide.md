# HM Simulator GUI User Guide

This guide provides detailed information on using the HM Simulator Graphical User Interface (GUI) for architectural exploration and learning.

---

## The GUI Layout

When the simulator starts, you'll see:

- **Header Bar** (top): Contains file operations (New, Open, Save), version selector, and execution controls.
- **Main Area** (center): Editor for entering your program (assembly or machine code).
- **Right Panel** (right): Shows register values (PC, AC, IR, SR) and memory contents.
- **Status Bar** (bottom): Displays simulator status and error messages.

---

## Selecting Your HM Version

Use the version dropdown in the header bar to select which HM version to simulate:

- **HMv1**: Basic LOAD/STORE/ADD operations.
- **HMv2**: Adds SUB, JMP, JMPZ.
- **HMv3**: Adds CALL, RETURN.
- **HMv4**: Adds indirect addressing.

Switching versions updates the available instructions while preserving your current memory contents.

---

## Execution Controls

- **Run**: Execute instructions continuously at high speed (~60,000+ instructions/sec). Displays total cycles in real-time.
- **Step**: Execute one instruction and advance the program counter.
- **Reset**: Clear all registers (PC, AC, IR, SR, Cycles) and memory.

---

## GUI Controls Reference

### File Operations
- **New**: Reset the simulator to initial state (clears registers and memory).
- **Open**: Load a saved state from a JSON file.
- **Save**: Save the current state to a JSON file.

### Execution Controls
- **Step**: Execute one instruction and update all displays.
- **Reset**: Clear all registers (PC, AC, IR, SR = 0) and memory (all zeros).

### Version Selector
Drop-down menu to switch between:
- HMv1 (LOAD, STORE, ADD)
- HMv2 (+ SUB, JMP, JMPZ)
- HMv3 (+ CALL, RETURN)
- HMv4 (+ Indirect LOAD/STORE)

### Memory Editor
You can directly edit memory contents by clicking on a value in the memory view. Values can be entered in hexadecimal (e.g., `0x1234`) or decimal format. When you edit a memory value, the Assembly Editor updates in real-time with the new disassembled mnemonic. Note that editing memory directly will remove any existing assembly comment for that specific address to ensure documentation remains accurate.

### Register Display
The register panel shows current register values in hexadecimal format:
- **PC**: Program Counter (next instruction address)
- **AC**: Accumulator (arithmetic result)
- **IR**: Instruction Register (current instruction)
- **SR**: Status Register (flags - HMv2+ only)
- **Cycles**: Total execution cycles since last reset

---

## Learning Path Suggestions

### Beginner Level - Master HMv1
Start by becoming comfortable with the three basic operations:
1. **LOAD**: Understand how data moves from memory to the CPU.
2. **STORE**: Understand how data moves from the CPU to memory.
3. **ADD**: Understand how the ALU performs arithmetic.

Practice by writing programs that:
- Load values, add them together, store the result.
- Chain multiple additions.
- Move values between memory locations.

### Intermediate Level - Move to HMv2
Once comfortable with HMv1, add branching:
1. **SUB**: Learn subtraction (and the concept of negative numbers).
2. **JMP**: Understand unconditional jumps and program flow.
3. **JMPZ**: Learn conditional execution based on flags.

Practice by writing programs that:
- Count down from a number to zero.
- Implement loops.
- Create simple decisions (if zero, do something).

### Advanced Level - HMv3 Subroutines
Add procedure calls:
1. **CALL**: Save return address and jump to subroutine.
2. **RETURN**: Restore execution to after the call.

Practice by writing programs that:
- Extract common code into reusable subroutines.
- Implement a simple function with parameters (via memory).
- Create a loop using a subroutine.

### Expert Level - HMv4 Indirect Addressing
Master pointer operations:
1. **LOAD (indirect)**: Load from an address stored in memory.
2. **STORE (indirect)**: Store to an address stored in memory.

Practice by writing programs that:
- Implement arrays and array indexing.
- Use pointer arithmetic.
- Create data structures (records).
