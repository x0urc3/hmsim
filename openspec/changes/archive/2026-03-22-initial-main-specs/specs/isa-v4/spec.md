## ADDED Requirements

### Requirement: Inheritance from HMv3
The HMv4 architecture SHALL inherit all instructions and behaviors from HMv3.

#### Scenario: CALL in HMv4
- **WHEN** architecture is set to HMv4
- **AND** current PC is `0x0100`
- **AND** the instruction `0xA300` is executed
- **THEN** AC contains `0x0101`
- **AND** PC is set to `0x0300`

### Requirement: LOAD indirect (0x3)
The HMv4 architecture SHALL support an indirect `LOAD` instruction with opcode `0x3`.
- **Effect**: Load AC from the memory address specified by the value stored at the address in the instruction.
- **Cycles**: 10

#### Scenario: Indirect load
- **WHEN** memory address `0x0100` contains `0x0200`
- **AND** memory address `0x0200` contains `0xABCD`
- **AND** the instruction `0x3100` is executed
- **THEN** AC contains `0xABCD`

### Requirement: STORE indirect (0x4)
The HMv4 architecture SHALL support an indirect `STORE` instruction with opcode `0x4`.
- **Effect**: Store the contents of AC to the memory address specified by the value stored at the address in the instruction.
- **Cycles**: 25

#### Scenario: Indirect store
- **WHEN** AC contains `0xCAFE`
- **AND** memory address `0x0100` contains `0x0300`
- **AND** the instruction `0x4100` is executed
- **THEN** memory address `0x0300` contains `0xCAFE`
