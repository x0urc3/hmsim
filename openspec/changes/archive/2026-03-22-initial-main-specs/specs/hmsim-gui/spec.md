## ADDED Requirements

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
