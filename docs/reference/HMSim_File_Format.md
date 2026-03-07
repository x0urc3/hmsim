# HMSim State File Format

The HM Simulator uses a JSON-based state file format (extension `.hm`) to persist and restore simulator snapshots. This format separates executable code (text) from program data and supports inline commenting.

## Overview

State files capture the complete runtime context of the simulator. To improve readability and debugging, the memory is divided into two logical sections:

- **text**: Contains disassembled instructions (assembly mnemonics) starting from address `0x0000`. Supports inline comments using the `;` character.
- **data**: Contains hexadecimal representations of non-zero memory locations that are not part of the program code.

## JSON Schema

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `version` | string | `"HMv1"`, `"HMv2"` | Simulator version (HMv3/v4 loaded as HMv2) |
| `pc` | integer | 0 – 65535 | Program Counter (next instruction address) |
| `ac` | integer | 0 – 65535 | Accumulator (primary data register) |
| `ir` | integer | 0 – 65535 | Instruction Register (current instruction) |
| `sr` | integer | 0 – 65535 | Status Register (HMv2+ only) |
| `text` | object | keys: `0xXXXX`, values: string | Program section (assembly + optional `; comment`) |
| `data` | object | keys: `0xXXXX`, values: `0xXXXX` | Data section (hexadecimal values) |

## Field Details

### text (Program Section)

This section contains a linear disassembly of the program starting from address `0x0000`.
- **Heuristic**: The simulator starts at address `0x0000` and disassembles each word sequentially.
- **Boundary**: Disassembly continues until an invalid opcode for the current `version` is encountered.
- **Comments**: Assembly strings can include comments starting with `;`. These are ignored by the assembler but preserved in the `.hm` file.
- **Format**: `{"0x0000": "LOAD 0x00A ; My comment"}`.

### data (Data Section)

This section contains all non-zero memory locations that were not included in the `text` section.
- **Format**: `{"0x000A": "0x0005"}`.

## Example (`add_two_numbers.hm`)

```json
{
  "version": "HMv1",
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
