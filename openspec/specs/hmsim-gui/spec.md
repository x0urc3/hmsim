# hmsim-gui Specification

## Purpose
The hmsim-gui specification defines the requirements for the GTK4-based graphical user interface of the HM Simulator, including editor modes, execution controls, configuration dialogs, and file operations.

## Requirements
### Requirement: GTK4-based Graphical Interface
The HM Simulator SHALL provide a graphical user interface implemented using GTK 4 (via PyGObject).

#### Scenario: Launch application GUI
- **WHEN** the `hmsim` command is executed
- **THEN** the main window appears with execution controls, editor, and state views

### Requirement: Dual-mode Integrated Editor
The GUI SHALL include an integrated code editor that supports:
- **Assembly mode**: For writing mnemonics.
- **Machine code mode**: For direct memory manipulation.

#### Scenario: Assembly to machine code sync
- **WHEN** a user types `LOAD 100` in the assembly editor
- **THEN** the machine code at the current PC address is updated to `0x1064` (100 in hex is 64)

#### Scenario: Memory to Assembly Sync
- **WHEN** a user types `0x1234` in the machine code editor at address `0x0100`
- **THEN** the assembly editor displays the corresponding mnemonic (e.g., `LOAD 0x1234`)

### Requirement: Persistent Theme Support
The GUI SHALL support Light, Dark, and System theme modes, with the selection persisting across application restarts.

#### Scenario: Change theme to Dark
- **WHEN** the user selects "View > Theme > Dark"
- **THEN** the UI colors update to the dark palette
- **AND** the preference is saved for the next session

### Requirement: Session Metadata and Audit Logging
Every saved `.hm` file SHALL contain a `metadata` object that tracks:
- `created_at`: Timestamp of initial creation.
- `updated_at`: Timestamp of last save.
- `software_version`: Version of HM-Sim used.
- `log`: An audit trail of machine environments (OS, Hostname, Platform) where the file was modified.

#### Scenario: Audit log deduplication
- **WHEN** a file is saved multiple times on the same machine
- **THEN** only the `updated_at` of the existing log entry for that machine is updated (no duplicate entries)

### Requirement: Simulator Configuration
The GUI SHALL provide a Setup dialog for configuring the simulator engine, including architecture selection and memory region definitions.

#### Scenario: Setup - Memory Regions
- **WHEN** the user opens Simulator → Setup
- **AND** enters Text Start: `0x0000`, Text End: `0x00FF`, Data Start: `0x0100`, Data End: `0xFFFF`
- **AND** clicks "Apply"
- **THEN** the memory is partitioned: Text region (0x0000-0x00FF) for code, Data region (0x0100-0xFFFF) for storage

#### Scenario: Setup - Architecture Selection
- **WHEN** the user opens Simulator → Setup
- **AND** selects "HMv3" from the Architecture dropdown
- **AND** clicks "Apply"
- **THEN** the engine switches to HMv3 architecture with CALL/RETURN support

#### Scenario: Setup - Invalid Address Format
- **WHEN** the user enters "XYZ" in a memory address field
- **AND** clicks "Apply"
- **THEN** an error message "Invalid address format" is displayed
- **AND** the dialog remains open for correction

#### Scenario: Setup - Overlapping Regions
- **WHEN** the user enters Text: 0x0000-0x0100 and Data: 0x00FF-0xFFFF
- **AND** clicks "Apply"
- **THEN** an error message "Text and Data regions cannot overlap" is displayed
- **AND** the configuration is not applied

#### Scenario: Setup - Address Out of Range
- **WHEN** the user enters address `0x20000` (beyond 16-bit range)
- **AND** clicks "Apply"
- **THEN** an error message "All addresses must be within 0x0000-0xFFFF and start <= end" is displayed
- **AND** the configuration is not applied

### Requirement: Execution Controls
The GUI SHALL provide controls for running, stepping, and resetting the simulator.

#### Scenario: Run - Continuous Execution
- **WHEN** the user clicks the "Run" button
- **THEN** instructions execute continuously in batches of 1000 cycles
- **AND** the UI updates every batch
- **AND** the Run button text changes to "Stop"

#### Scenario: Stop - Halt Execution
- **WHEN** the simulator is running (Run mode active)
- **AND** the user clicks the "Stop" button
- **THEN** execution halts at the next batch boundary
- **AND** the Run button text changes back to "Run"
- **AND** the status shows "Ready"

#### Scenario: Step - Single Instruction
- **WHEN** the user clicks the "Step" button
- **THEN** exactly one instruction is executed
- **AND** registers and memory are updated
- **AND** PC advances to the next instruction

#### Scenario: Reset - Clear CPU State
- **WHEN** the user clicks the "Reset" button
- **THEN** PC is set to 0
- **AND** AC (Accumulator) is set to 0
- **AND** SR (Status Register) is set to 0
- **AND** memory contents remain unchanged

#### Scenario: Execution Error
- **WHEN** the simulator encounters an invalid opcode during Run or Step
- **THEN** execution halts
- **AND** an error dialog shows the error message and PC address where the error occurred
- **AND** the status shows "Ready"

### Requirement: File Operations
The GUI SHALL support saving and loading simulator state files in `.hm` JSON format.

#### Scenario: Save State File
- **WHEN** the user selects File → Save
- **AND** chooses a location and filename
- **THEN** the current state is saved as JSON including: memory, registers (PC, AC, SR), architecture, and metadata
- **AND** the file is saved with `.hm` extension

#### Scenario: Load State File
- **WHEN** the user selects File → Open
- **AND** selects a valid `.hm` file
- **THEN** memory is restored
- **AND** registers (PC, AC, SR) are restored
- **AND** architecture is restored
- **AND** metadata is loaded into the engine

#### Scenario: Load - Invalid File
- **WHEN** the user attempts to open a corrupt or malformed `.hm` file
- **THEN** an error dialog displays "Invalid state file format"
- **AND** the current simulator state is unchanged
