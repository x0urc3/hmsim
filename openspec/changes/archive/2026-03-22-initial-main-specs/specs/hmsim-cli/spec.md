## ADDED Requirements

### Requirement: Headless Simulator (hmsim_cli)
The HM Simulator SHALL provide a Command Line Interface (CLI) for headless execution of programs.
- **Input**: A valid JSON state file (`.hm`).
- **Output**: A final execution report including register state, memory regions, and cycles consumed.

#### Scenario: Headless program execution
- **WHEN** the `hmsim_cli program.hm` command is executed
- **THEN** the program is simulated to completion or until a cycle limit is reached
- **AND** a summary report is printed to standard output

### Requirement: Cross-architecture Assembler (hmasm)
The project SHALL provide an assembler (`hmasm`) that generates machine code based on the target architecture version (HMv1-HMv4).
- **Default**: HMv1 behavior.
- **Incremental support**: Supports new mnemonics for higher versions when the appropriate flag is set.

#### Scenario: Assemble LOAD for HMv1
- **WHEN** the `hmasm "LOAD 100"` command is executed
- **THEN** it outputs `0x1064`

### Requirement: Cross-architecture Disassembler (hmdas)
The project SHALL provide a disassembler (`hmdas`) that translates machine code back into mnemonics based on the target architecture version.

#### Scenario: Disassemble 0x3100 for HMv4
- **WHEN** the architecture is HMv4
- **AND** the `hmdas 0x3100` command is executed
- **THEN** it outputs `LOAD (0x0100)` (indirect)
