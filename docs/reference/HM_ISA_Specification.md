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

| Version | Opcode | Mnemonic | Description                           | Cycles |
|---------|--------|----------|---------------------------------------|--------|
| HMv1    | 0x1    | LOAD     | Load AC from memory                   | 5      |
| HMv1    | 0x2    | STORE    | Store AC to memory                    | 15     |
| HMv1    | 0x5    | ADD      | Add to AC from memory                 | 10     |
| HMv2    | 0x6    | SUB      | Subtract AC from memory               | 10     |
| HMv2    | 0x8    | JMP      | Jump to memory address                | 5      |
| HMv2    | 0x9    | JMPZ     | Jump to memory if ZF=1               | 5      |
| HMv3    | 0xa    | CALL     | Store PC+1 in AC; Load PC with memory | 5      |
| HMv3    | 0xb    | RETURN   | Load PC with AC                        | 1      |
| HMv4    | 0x3    | LOAD     | Load AC from memory (indirect)        | 10     |
| HMv4    | 0x4    | STORE    | Store AC to memory (indirect)         | 25     |

Note: HMv4 indirect addressing uses bracket syntax: `LOAD (address)` and `STORE (address)`.
