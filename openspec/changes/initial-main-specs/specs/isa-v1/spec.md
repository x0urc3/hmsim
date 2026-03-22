## ADDED Requirements

### Requirement: LOAD instruction (0x1)
The HMv1 architecture SHALL support a `LOAD` instruction with opcode `0x1`.
- **Effect**: Load AC from the memory address specified in the instruction.
- **Cycles**: 5

#### Scenario: LOAD AC from memory
- **WHEN** memory address `0x0100` contains `0x1234`
- **AND** the instruction `0x1100` is executed
- **THEN** AC contains `0x1234`

### Requirement: STORE instruction (0x2)
The HMv1 architecture SHALL support a `STORE` instruction with opcode `0x2`.
- **Effect**: Store the contents of AC to the memory address specified in the instruction.
- **Cycles**: 15

#### Scenario: STORE AC to memory
- **WHEN** AC contains `0xABCD`
- **AND** the instruction `0x2200` is executed
- **THEN** memory address `0x0200` contains `0xABCD`

### Requirement: ADD instruction (0x5)
The HMv1 architecture SHALL support an `ADD` instruction with opcode `0x5`.
- **Effect**: Add the value from memory at the specified address to AC.
- **Cycles**: 10

#### Scenario: ADD to AC from memory
- **WHEN** AC contains `0x000A` (10 decimal)
- **AND** memory address `0x0300` contains `0x0005` (5 decimal)
- **AND** the instruction `0x5300` is executed
- **THEN** AC contains `0x000F` (15 decimal)
