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

### Data Format

HM uses 16-bit signed magnitude representation for integers:

- **Bit 15**: Sign bit (0 = positive, 1 = negative)
- **Bits 0-14**: Magnitude (absolute value)

Note: This differs from two's complement, which is common in modern processors.

## Instruction Set Reference

Each HM version adds new instructions while preserving all previous ones:

| Version | Incremental Instructions | Opcode Map |
|---------|--------------------------|------------|
| **HMv1** | `LOAD`, `STORE`, `ADD` | 0x1, 0x2, 0x5 |
| **HMv2** | `SUB`, `JMP`, `JMPZ` | 0x6, 0x8, 0x9 |
| **HMv3** | `CALL`, `RETURN` | 0xA, 0xB |
| **HMv4** | `LOAD` (Ind), `STORE` (Ind) | 0x3, 0x4 |

For full cycle counts and descriptions, see the [ISA Specification](docs/reference/HM_ISA_Specification.md).

## Getting Started

### Installation

```bash
pip install -e .
```

### Usage

The HM Simulator suite includes both a graphical interface and command-line tools:

- **Tutorial**: Follow the [Step-by-Step Tutorial](docs/user/Tutorial.md) to write and run your first program.
- **GUI**: Launch the interactive simulator with `hmsim_gui`. For interface details, see the [GUI User Guide](docs/user/GUI_User_Guide.md).
- **CLI**: Headless execution (`hmsim`), assembly (`hmasm`), and disassembly (`hmdas`). See the [Development Guide](docs/developer/DEVELOPMENT.md) for CLI usage.

## Example Programs

The `examples/` directory contains sample programs:

- **add_two_numbers.hm**: A complete HMv1 program that adds 5 + 7 = 12.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Documentation Index

### User Guides
- [Step-by-Step Tutorial](docs/user/Tutorial.md) - **Start here** for a guided introduction.
- [GUI User Guide](docs/user/GUI_User_Guide.md) - Complete reference for the graphical interface.

### Technical Reference
- [ISA Specification](docs/reference/HM_ISA_Specification.md) - Complete opcode and timing reference.
- [File Format](docs/reference/HMSim_File_Format.md) - `.hm` JSON state file structure.

### Developer Documentation
- [Development Guide](docs/developer/DEVELOPMENT.md) - CLI tools and internal architecture.
- [Software Specification](docs/developer/HM_Software_Spec.md) - Technical requirements and design.
