# hmsim User Guide

This guide provides detailed information on using the HM Simulator interactive interface (`hmsim`) for architectural exploration and learning.

---

## The hmsim Interface

When the simulator starts, you'll see:

- **Header Bar** (top): Contains file operations (New, Open, Save, Save As), edit operations (Undo, Redo), view operations (Theme switching), and execution controls.
- **Main Area** (center): Assembly Editor for entering your program and comments.
- **Right Panel** (right): Shows the active Processor Architecture, register values (PC, AC, IR, SR), and memory contents.
- **Status Bar** (bottom): Displays real-time simulator status (e.g., "Loading...", "Saved to...") and error messages.

---

## Window Title and State

The window title provides immediate feedback on the state of your project:
- **Filename**: Displays the name of the currently open `.hm` file.
- **Modified Indicator**: An asterisk (`*`) appears next to the filename when there are unsaved changes. The simulator uses an intelligent snapshot system to detect changes—if you manually revert your changes to match the last saved state, the asterisk will automatically disappear.

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

- **Run** (`F5`): Execute instructions continuously at high speed (~60,000+ instructions/sec). Displays total cycles in real-time.
- **Step** (`F10`): Execute one instruction and advance the program counter.
- **Reset** (`F12`): Clear all registers (PC, AC, IR, SR, Cycles).

---

## Simulator Controls Reference

### File Operations (Menu: File)
- **New** (`Ctrl+N`): Reset the simulator to initial state (clears registers and memory). Prompts to save if there are unsaved changes.
- **Open** (`Ctrl+O`): Load a saved state from a JSON file. Prompts to save if the current state is modified.
- **Save** (`Ctrl+S`): Save the current state to the active file.
- **Save As...** (`Ctrl+Shift+S`): Save the current state to a new file and make it the active file.
- **Quit** (`Ctrl+Q`): Exit the simulator. Prompts to save if there are unsaved changes.

### Editor Operations (Menu: Edit)
- **Undo** (`Ctrl+Z`): Revert the last change to the assembly or memory.
- **Redo** (`Ctrl+Shift+Z` or `Ctrl+Y`): Re-apply the last undone change.
- The simulator tracks a complete history of your session, including assembly edits, memory modifications, and architecture changes.

### View Operations (Menu: View)
- **Theme**: Toggle between **Light**, **Dark**, and **System** themes.
    - **Light**: A crisp, high-contrast light interface.
    - **Dark**: A modern dark interface designed for reduced eye strain.
    - **System**: Automatically follows your operating system's dark/light preference.
- Theme settings are automatically saved and will persist the next time you open the application.

### Execution Controls (Menu: Run)
- **Step** (`F10`): Execute one instruction and update all displays.
- **Reset** (`F12`): Clear all registers (PC, AC, IR, SR = 0).

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
