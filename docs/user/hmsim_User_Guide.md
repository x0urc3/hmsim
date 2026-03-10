# hmsim User Guide

This guide provides detailed information on using the HM Simulator interactive interface (`hmsim`) for architectural exploration and learning.

---

## The hmsim Interface

When the simulator starts, you'll see:

- **Header Bar** (top): Contains file operations (New, Open, Save) and execution controls.
- **Main Area** (center): Editor for entering your program (assembly or machine code).
- **Right Panel** (right): Shows the active Processor Architecture, register values (PC, AC, IR, SR), and memory contents.
- **Status Bar** (bottom): Displays simulator status and error messages.

---

## Selecting Your HM Version

Processor Architecture selection is handled via the **Simulator Setup** dialog (Menu: **Setup** > **Simulator Setup...**).

In the Setup dialog, you can select the processor architecture:

- **HMv1**: Basic LOAD/STORE/ADD operations.
- **HMv2**: Adds SUB, JMP, JMPZ.
- **HMv3**: Adds CALL, RETURN.
- **HMv4**: Adds indirect addressing.

Switching versions updates the available instructions while preserving your current memory contents. The active version is always displayed at the top of the Register Display.

---

## Execution Controls

- **Run**: Execute instructions continuously at high speed (~60,000+ instructions/sec). Displays total cycles in real-time.
- **Step**: Execute one instruction and advance the program counter.
- **Reset**: Clear all registers (PC, AC, IR, SR, Cycles).

---

## Simulator Controls Reference

### File Operations
- **New**: Reset the simulator to initial state (clears registers and memory).
- **Open**: Load a saved state from a JSON file.
- **Save**: Save the current state to a JSON file.

### Execution Controls
- **Step**: Execute one instruction and update all displays.
- **Reset**: Clear all registers (PC, AC, IR, SR = 0).

### Simulator Setup
Accessible via the **Setup** menu. Allows you to configure:
- **Processor Architecture**: Switch between HMv1, HMv2, HMv3, and HMv4.
- **Memory Regions**: Define the start and end addresses for the **Text** (executable code) and **Data** sections.

### Memory View
The memory view displays the current contents of the 16-bit word-addressable memory (addresses 0x0000 to 0xFFFF).
- **PC Indicator**: A symbolic arrow (`→`) in the left-most gutter column indicates the memory address currently pointed to by the **Program Counter (PC)**. This helps you track execution flow visually as you step through a program.
- **Direct Editing**: You can directly edit memory contents by clicking on a value in the memory view. Values can be entered in hexadecimal (e.g., `0x1234`) or decimal format.
- **Real-time Sync**: When you edit a memory value, the Assembly Editor updates in real-time with the new disassembled mnemonic.
- **Go to Address**: Use the "Go to Address" entry at the top of the memory view to quickly scroll to a specific memory location.

### Register Display
The register panel shows the current configuration and register values.
- **Engine**: The active processor architecture (e.g., "Engine: HMv1").
- **PC, AC, IR, SR**: These registers can be **directly edited**. Click on a register value to enter a new one in hexadecimal (e.g., `0x1234`) or decimal format. Changes are immediately reflected across the simulator (e.g., changing the PC updates the execution highlight in the Memory View).
- **Cycles**: Total execution cycles since last reset (read-only).
- **Instructions**: Total instructions executed (read-only).

---

## Session Provenance and Audit Logs

The HM Simulator includes a built-in auditing system that tracks the "Chain of Custody" for every state file. This is particularly useful for educational settings to track project evolution.

### Automatic Metadata
Every `.hm` file automatically includes a `metadata` section (located at the bottom of the file) that contains:
- **Created At**: The exact timestamp when the simulation session was first started.
- **Updated At**: The timestamp of the most recent save operation.
- **Software Version**: The version of the HM Simulator used to save the file.

### The Audit Log
The simulator maintains a persistent **Log** of every unique environment where the file has been saved.
- **Session-Bound**: The log follows the simulation data. If you use "Save As" to create a new file, the entire history of the original session is preserved in the new file.
- **Latest Entry Logic**: To keep the file clean, the simulator only adds a new entry if the file is saved on a *different* machine. Multiple saves on the same computer will simply update the timestamp of the existing entry.
- **Information Captured**: When "Debug" mode is active (default), the log records the Operating System, Hostname, and Platform details.

### Starting a Fresh Session
To clear the audit trail and start a completely new project with a fresh "Created At" timestamp, use the **File > New** command. This resets the internal session metadata.

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
