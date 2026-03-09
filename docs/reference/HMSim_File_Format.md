# HMSim State File Format

The HM Simulator uses a JSON-based state file format (extension `.hm`) to persist and restore simulator snapshots. This format separates executable code (text) from program data and supports inline commenting.

## Overview

State files capture the complete runtime context of the simulator. To ensure data integrity, all `.hm` files are validated against a JSON Schema upon loading. This ensures that register values are within range and that required fields for specific processor versions (e.g., `sr` for HMv2+) are present.

Memory is divided into two logical sections:

- **setup**: Stores configuration for the simulation session, including memory region boundaries.
- **text**: Contains disassembled instructions (assembly mnemonics) within the specified text region. Supports inline comments using the `;` character.
- **data**: Contains hexadecimal representations of non-zero memory locations that are not part of the program code or text section.

## JSON Schema

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `version` | string | `"HMv1"`, `"HMv2"`, `"HMv3"`, `"HMv4"` | Simulator version |
| `setup` | object | See below | Simulation configuration (regions, etc.) |
| `pc` | integer | 0 – 65535 | Program Counter (next instruction address) |
| `ac` | integer | 0 – 65535 | Accumulator (primary data register) |
| `ir` | integer | 0 – 65535 | Instruction Register (current instruction) |
| `sr` | integer | 0 – 65535 | Status Register (HMv2+ only) |
| `text` | object | keys: `0xXXXX`, values: string | Program section (assembly + optional `; comment`) |
| `data` | object | keys: `0xXXXX`, values: `0xXXXX` | Data section (hexadecimal values) |

## Field Details

### setup (Simulation Configuration)

This block defines how the simulator should interpret memory.
- **text**: An array of two integers `[start, end]` defining the executable code region.
- **data**: An array of two integers `[start, end]` defining the data storage region.

### text (Program Section)

This section contains a linear disassembly of the program within the `setup.text` boundaries.
- **Heuristic**: The simulator starts at the text region start and disassembles each word sequentially.
- **Boundary**: Disassembly continues until an invalid opcode for the current `version` is encountered or the end of the text region is reached.
- **Comments**: Assembly strings can include comments starting with `;`. These are ignored by the assembler but preserved in the `.hm` file.
- **Format**: `{"0x0000": "LOAD 0x00A ; My comment"}`.

### data (Data Section)

This section contains all non-zero memory locations that are not part of the `text` section.
- **Format**: `{"0x000A": "0x0005"}`.

## Example (`add_two_numbers.hm`)

```json
{
  "version": "HMv1",
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
  }
}
```
