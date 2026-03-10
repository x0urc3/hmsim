# HM Simulator Tutorial: Your First Program

This tutorial walks you through the complete process of writing, entering, and running a simple program in the HM Simulator.

## The Problem
We want to compute: 5 + 7 = 12

---

## Step 1: Write the Program
Our program will:
1. LOAD the first number (5) from memory into the accumulator.
2. ADD the second number (7) to the accumulator.
3. STORE the result to memory for safekeeping.

Here's how we express this in HM assembly:

| Address | Instruction | Operation |
|---------|-------------|------------|
| 0 | LOAD 10 | Load value from address 10 into AC |
| 1 | ADD 11 | Add value at address 11 to AC |
| 2 | STORE 12 | Store AC value to address 12 |

---

## Step 2: Store the Data
We need to place our data values in memory. Let's put them at addresses 10, 11, and 12:
- **Address 10**: 5 (first number)
- **Address 11**: 7 (second number)
- **Address 12**: 0 (result storage - initially empty)

---

## Step 3: Enter and Run
1. **Launch the HM Simulator**: Open the application using `hmsim`.
2. **Select HMv1**: Go to **Setup** > **Simulator Setup...** in the menu, select **HMv1** from the architecture dropdown, and click **Apply**.
3. **Enter Instructions**: In the Assembly Editor (left pane), type the instructions:
   ```assembly
   LOAD 10
   ADD 11
   STORE 12
   ```
4. **Enter Data**:
   - In the Memory View (right pane), find address `0x000A` (10) and double-click the value cell. Enter `5`.
   - Find address `0x000B` (11), double-click, and enter `7`.
5. **Execute**:
   - Click the **Step** button in the toolbar. The PC advances to 1, and AC becomes 5.
   - Click **Step** again. The PC advances to 2, and AC becomes 12 (0xC).
   - Click **Step** a third time. The PC advances to 3, and memory address `0x000C` (12) now contains `12`.
6. **Verify**: Check address `0x000C` in the memory grid; it should now contain `0x000C` (which is 12 in decimal).

---

## Understanding What Happens
Let's trace through each instruction to see how the processor state changes:

### Instruction 0: `LOAD 10`
- **Fetch**: CPU fetches instruction `0x100A` (LOAD from address 10).
- **Decode**: Opcode is `1` (LOAD), operand address is `10`.
- **Execute**: CPU reads memory at address 10 (value `5`) and stores it in the **AC** register.
- **Update**: **AC** now contains `5`, and **PC** increments to `1`.

### Instruction 1: `ADD 11`
- **Fetch**: CPU fetches instruction `0x500B` (ADD from address 11).
- **Decode**: Opcode is `5` (ADD), operand address is `11`.
- **Execute**: CPU reads memory at address 11 (value `7`) and adds it to the current **AC** value (`5`).
- **Update**: **AC** now contains `12`, and **PC** increments to `2`.

### Instruction 2: `STORE 12`
- **Fetch**: CPU fetches instruction `0x200C` (STORE to address 12).
- **Decode**: Opcode is `2` (STORE), operand address is `12`.
- **Execute**: CPU writes the current **AC** value (`12`) to memory address `12`.
- **Update**: Memory address `12` now contains `12`, and **PC** increments to `3`.

Congratulations! You've successfully written and executed your first HM program.
