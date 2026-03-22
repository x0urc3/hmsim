## ADDED Requirements

### Requirement: 16-bit register set
The simulator engine SHALL maintain the following 16-bit registers:
- **PC (Program Counter)**: Stores the memory address of the next instruction.
- **IR (Instruction Register)**: Stores the current instruction being executed.
- **AC (Accumulator)**: Primary data register for arithmetic and logic.
- **SR (Status Register)** (HMv2+): Stores processor status flags.

#### Scenario: Register initialization
- **WHEN** the simulator is initialized
- **THEN** all registers are set to 0 by default

### Requirement: 16-bit two's complement data format
The HM simulator SHALL represent integer data as a 16-bit two's complement value:
- Standard Python integer arithmetic with `& 0xFFFF` masking.
- Bit 15 is the sign bit.

#### Scenario: Positive data representation
- **WHEN** the decimal value `42` is stored in AC
- **THEN** the AC contains `0x002A`

#### Scenario: Negative data representation
- **WHEN** the decimal value `-1` is stored in AC
- **THEN** the AC contains `0xFFFF`

### Requirement: Status Register (SR) Flags
In architecture versions HMv2 and above, the SR SHALL include the following status flags:
- **SF (Sign Flag)**: Set to 1 if the MSB of the result is 1 (bit 15).
- **ZF (Zero Flag)**: Set to 1 if the result of an operation is zero.
- **EF (Equality Flag)**: Set to 1 if two operands are equal (used by SUB).
- **OF (Overflow Flag)**: Set to 1 if an arithmetic overflow occurs.

#### Scenario: Sign Flag (SF) update
- **WHEN** an operation produces a negative result
- **THEN** the SR bit 15 (SF) is set to 1

#### Scenario: Zero Flag (ZF) update
- **WHEN** an operation produces a zero result
- **THEN** the SR bit 14 (ZF) is set to 1

### Requirement: 64KB Unified Memory
The simulator SHALL provide a unified 16-bit word-addressable memory of 65,536 (64KB) locations.

#### Scenario: Out of bounds memory access
- **WHEN** an instruction attempts to access a memory address outside the range `0x0000` to `0xFFFF`
- **THEN** the simulator raises a memory access error
