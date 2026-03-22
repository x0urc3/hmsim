# isa-v2 Specification

## Purpose
TBD - created by archiving change initial-main-specs. Update Purpose after archive.
## Requirements
### Requirement: Inheritance from HMv1
The HMv2 architecture SHALL inherit all instructions and behaviors from HMv1.

#### Scenario: LOAD AC in HMv2
- **WHEN** architecture is set to HMv2
- **AND** memory address `0x0100` contains `0x1234`
- **AND** the instruction `0x1100` is executed
- **THEN** AC contains `0x1234`

### Requirement: SUB instruction (0x6)
The HMv2 architecture SHALL support a `SUB` instruction with opcode `0x6`.
- **Effect**: Subtract the value at memory address from AC. Update SR flags (SF, ZF, EF).
- **Cycles**: 10

#### Scenario: SUB from AC
- **WHEN** AC contains `0x000A` (10 decimal)
- **AND** memory address `0x0400` contains `0x0004` (4 decimal)
- **AND** the instruction `0x6400` is executed
- **THEN** AC contains `0x0006` (6 decimal)

### Requirement: JMP instruction (0x8)
The HMv2 architecture SHALL support an unconditional `JMP` instruction with opcode `0x8`.
- **Effect**: Load PC with the memory address specified in the instruction.
- **Cycles**: 5

#### Scenario: Unconditional jump
- **WHEN** the instruction `0x8500` is executed
- **THEN** PC is set to `0x0500`

### Requirement: JMPZ instruction (0x9)
The HMv2 architecture SHALL support a conditional `JMPZ` instruction (Jump if Zero) with opcode `0x9`.
- **Effect**: If the Zero Flag (ZF) is 1, load PC with the memory address.
- **Cycles**: 5

#### Scenario: Jump if zero (ZF=1)
- **WHEN** the Zero Flag (ZF) is 1
- **AND** the instruction `0x9600` is executed
- **THEN** PC is set to `0x0600`

#### Scenario: No jump if zero (ZF=0)
- **WHEN** the Zero Flag (ZF) is 0
- **AND** the instruction `0x9600` is executed
- **THEN** PC remains at the next instruction address

