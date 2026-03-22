## ADDED Requirements

### Requirement: Inheritance from HMv2
The HMv3 architecture SHALL inherit all instructions and behaviors from HMv2.

#### Scenario: JMPZ in HMv3
- **WHEN** architecture is set to HMv3
- **AND** the Zero Flag (ZF) is 1
- **AND** the instruction `0x9700` is executed
- **THEN** PC is set to `0x0700`

### Requirement: CALL instruction (0xA)
The HMv3 architecture SHALL support a `CALL` instruction with opcode `0xA`.
- **Effect**: Store the return address (PC+1) in the Accumulator (AC) and load PC with the subroutine memory address.
- **Cycles**: 5

#### Scenario: Call subroutine
- **WHEN** current PC is `0x0100`
- **AND** the instruction `0xA200` is executed
- **THEN** AC contains `0x0101`
- **AND** PC is set to `0x0200`

### Requirement: RETURN instruction (0xB)
The HMv3 architecture SHALL support a `RETURN` instruction with opcode `0xB`.
- **Effect**: Load PC with the value currently in the Accumulator (AC).
- **Cycles**: 1

#### Scenario: Return from subroutine
- **WHEN** AC contains `0x0101` (return address)
- **AND** the instruction `0xB000` is executed
- **THEN** PC is set to `0x0101`
