## HM Hypothetical Microprocessor High-Level Specification

The **HM** is a 16-bit RISC-style hypothetical microprocessor architecture designed for educational synthesis and Instruction Set Architecture (ISA) analysis. The device features a unified 16-bit word length for both instructions and data, utilizing a simplified load/store model.

### Architectural Register Set

The HMv1 architecture defines three primary 16-bit internal registers dedicated to control flow and arithmetic processing:

* **PC (Program Counter):** 16-bit register containing the memory address of the next instruction to be fetched.
* **IR (Instruction Register):** 16-bit register used to latch the current instruction during the decode and execution phases.
* **AC (Accumulator):** 16-bit primary data register used for all arithmetic operations and temporary operand storage.

### Word Formats

#### Instruction Format

Instructions are 16 bits wide, employing a fixed-length encoding scheme for single-cycle decode efficiency.

* **Opcode (Bits 0–3):** 4-bit operation code field.
* **Address (Bits 4–15):** 12-bit direct memory addressing field.

#### Integer Data Format

The HMv1 utilizes a 16-bit signed magnitude representation for integer arithmetic.

* **Sign (Bit 0):** MSB indicates value polarity.
* **Magnitude (Bits 1–15):** 15-bit field representing the absolute value of the integer.

### Instruction Set Summary

The following table outlines the supported machine instructions and their respective timing requirements:

| Opcode | Mnemonic | Operand | Description | Cycles |
| --- | --- | --- | --- | --- |
| `0x1` | **LOAD** | memory | Load AC with the contents of the specified memory address.  | 5 |
| `0x2` | **STORE** | memory | Store the current AC value to the specified memory address.  | 15 |
| `0x5` | **ADD** | memory | Add the value at the specified memory address to the AC.  | 10 |
