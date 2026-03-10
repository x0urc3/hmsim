# HMSim State File Format

The HM Simulator uses a JSON-based state file format (extension `.hm`) to persist and restore simulator snapshots. This format separates executable code (text) from program data and supports inline commenting.

## Overview

State files capture the complete runtime context of the simulator. To ensure data integrity, all `.hm` files are validated against a JSON Schema upon loading. This ensures that register values are within range and that required fields for specific processor architectures (e.g., `sr` for HMv2+) are present.

Memory is divided into two logical sections:

- **setup**: Stores configuration for the simulation session, including memory region boundaries.
- **text**: Contains disassembled instructions (assembly mnemonics) within the specified text region. Supports inline comments using the `;` character.
- **data**: Contains hexadecimal representations of non-zero memory locations that are not part of the program code or text section.

## JSON Schema

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `architecture` | string | `"HMv1"`, `"HMv2"`, `"HMv3"`, `"HMv4"` | HM processor architecture |
| `setup` | object | See below | Simulation configuration (regions, etc.) |
| `pc` | integer | 0 – 65535 | Program Counter (next instruction address) |
| `ac` | integer | 0 – 65535 | Accumulator (primary data register) |
| `ir` | integer | 0 – 65535 | Instruction Register (current instruction) |
| `sr` | integer | 0 – 65535 | Status Register (HMv2+ only) |
| `text` | object | keys: `0xXXXX`, values: string | Program section (assembly + optional `; comment`) |
| `data` | object | keys: `0xXXXX`, values: `0xXXXX` | Data section (hexadecimal values) |
| `metadata` | object | See below | File provenance and log (audit trail) |

## Field Details

### setup (Simulation Configuration)

This block defines how the simulator should interpret memory.
- **text**: An array of two integers `[start, end]` defining the executable code region.
- **data**: An array of two integers `[start, end]` defining the data storage region.

### text (Program Section)

This section contains a linear disassembly of the program within the `setup.text` boundaries.
- **Heuristic**: The simulator starts at the text region start and disassembles each word sequentially.
- **Boundary**: Disassembly continues until an invalid opcode for the current `architecture` is encountered or the end of the text region is reached.
- **Comments**: Assembly strings can include comments starting with `;`. These are ignored by the assembler but preserved in the `.hm` file.
- **Format**: `{"0x0000": "LOAD 0x00A ; My comment"}`.

### data (Data Section)

This section contains all non-zero memory locations that are not part of the `text` section.
- **Format**: `{"0x000A": "0x0005"}`.

### metadata (File Provenance and Audit Log)

This section tracks the lifecycle of the state file and is always placed at the bottom of the JSON object.
- **debug**: Boolean. If `true`, machine-specific information is recorded in the `log`.
- **software_version**: The version of `hmsim` that last saved the file.
- **created_at**: ISO 8601 timestamp of when the file was first created.
- **updated_at**: ISO 8601 timestamp of the most recent save.
- **log**: An array of objects tracking session metadata.
  - **timestamp**: ISO 8601 timestamp of the session.
  - **software_version**: Version of `hmsim` used.
  - **machine_info**: Environmental details (OS, Hostname, Platform).
  - **relevant_info**: Reserved for future use.

The simulator uses a **Latest Entry Logic** for the `log`: if a file is saved multiple times on the same machine (matched by `machine_info`), the last entry in the log is updated rather than appending a new one.

## Example (`add_two_numbers.hm`)

```json
{
  "architecture": "HMv1",
  "setup": {
    "text": [0, 256],
    "data": [257, 65535]
  },
  "pc": 0,
  "ac": 0,
  "ir": 0,
  "sr": 0,
  "text": {
    "0x0000": "LOAD 0x00A ; Load first number",
    "0x0001": "ADD 0x00B  ; Add second number",
    "0x0002": "STORE 0x00C ; Save result"
  },
  "data": {
    "0x000A": "0x0005",
    "0x000B": "0x0007"
  },
  "metadata": {
    "debug": true,
    "software_version": "1.0.0",
    "created_at": "2026-03-10T10:00:00",
    "updated_at": "2026-03-10T11:00:00",
    "log": [
      {
        "timestamp": "2026-03-10T11:00:00",
        "software_version": "1.0.0",
        "machine_info": {
          "os": "Linux",
          "hostname": "workstation",
          "platform": "Linux-6.5.0-amd64"
        },
        "relevant_info": ""
      }
    ]
  }
}
```
