## Why

HM-Sim is currently documented across multiple Markdown files (`HM_ISA_Specification.md`, `HM_Software_Spec.md`, `AGENTS.md`) and legacy PDF documents. While detailed, these documents are not integrated into a structured specification system that can track changes, verify implementations, and provide a single source of truth (SSOT) for the project's evolution. Establishing an OpenSpec baseline will allow for formal tracking of features, requirements, and design decisions as the simulator evolves from HMv1 to HMv4.

## What Changes

- Establish a core specification structure in `openspec/specs/`
- Formalize requirements for the HM Architectural Engine (registers, memory, cycles)
- Formalize requirements for the Instruction Set (HMv1-HMv4)
- Formalize requirements for the GUI and CLI tools
- Transition current documented requirements into trackable OpenSpec artifacts

## Capabilities

### New Capabilities
- `hm-engine`: Core simulation engine requirements (registers, memory, cycle accuracy, signed magnitude data format)
- `isa-v1`: Base instruction set architecture (LOAD, STORE, ADD)
- `isa-v2`: HMv2 incremental instructions (SUB, JMP, JMPZ) and Status Register (SR)
- `isa-v3`: HMv3 incremental instructions (CALL, RETURN) for subroutines
- `isa-v4`: HMv4 incremental instructions (indirect LOAD, STORE)
- `hmsim-gui`: Graphical User Interface requirements (GTK4, real-time sync, theme support, persistence, audit logging)
- `hmsim-cli`: Command Line Interface tools (assembler, disassembler, headless simulator)

### Modified Capabilities
- (none)

## Impact

- Documentation: This will become the primary reference for all future developments.
- Development Workflow: All new features or fixes will now be proposed as delta specs against these main specs.
- Testing: OpenSpec scenarios will guide the creation and verification of test cases.
