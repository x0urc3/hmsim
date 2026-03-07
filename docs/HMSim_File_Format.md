# HMSim State File Format

The HM Simulator uses a JSON-based state file format to persist and restore simulator snapshots. This enhanced format separates executable code (text) from program data, providing a human-readable representation of the simulation state.

## Overview

State files capture the complete runtime context of the simulator. To improve readability and debugging, the memory is divided into two logical sections:

- **text**: Contains disassembled instructions (assembly mnemonics) starting from address `0x0000`.
- **data**: Contains hexadecimal representations of non-zero memory locations that are not part of the program code.

## JSON Schema

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `version` | string | `"HMv1"`, `"HMv2"` | Simulator version (HMv3/v4 loaded as HMv2) |
| `pc` | integer | 0 – 65535 | Program Counter (next instruction address) |
| `ac` | integer | 0 – 65535 | Accumulator (primary data register) |
| `ir` | integer | 0 – 65535 | Instruction Register (current instruction) |
| `sr` | integer | 0 – 65535 | Status Register (HMv2+ only) |
| `text` | object | keys: `0xXXXX`, values: string | Program section (disassembled assembly) |
| `data` | object | keys: `0xXXXX`, values: `0xXXXX` | Data section (hexadecimal values) |

## Field Details

### version

String identifying the HM processor version. Determines available instructions and behavior.

### pc, ac, ir, sr

16-bit registers stored as integers. `sr` is available in HMv2 and later.

### text (Program Section)

This section contains a linear disassembly of the program starting from address `0x0000`.
- **Heuristic**: The simulator starts at address `0x0000` and disassembles each word sequentially using the `hmdas` logic.
- **Boundary**: Disassembly continues until an invalid opcode for the current `version` is encountered or an error occurs.
- **Format**: Keys are 4-digit hex addresses (e.g., `"0x0000"`) and values are assembly strings (e.g., `"LOAD 0x00A"`).

### data (Data Section)

This section contains all non-zero memory locations that were not included in the `text` section.
- **Format**: Keys and values are stored as 4-digit hexadecimal strings (e.g., `"0x000A": "0x0005"`).
- **Scope**: Includes constants, variables, and any machine code that failed to disassemble.

## Saving Logic

When saving state, the simulator applies the following logic:

1.  Initialize `text` and `data` objects.
2.  Start at `address = 0`.
3.  While `address` is within memory bounds:
    - Attempt to disassemble the value at `address`.
    - If successful: Add to `text` and increment `address`.
    - If disassembly fails: Break the loop.
4.  For all remaining memory addresses where `value != 0`:
    - If not already in `text`, add to `data` as `{"0xADDR": "0xVAL"}`.

## Loading Logic

When loading state:

1.  Registers are restored directly.
2.  **Text Processing**: Each entry in the `text` section is passed to the `hmasm` logic to be converted back into a 16-bit machine code and written to the specified memory address.
3.  **Data Processing**: Each entry in the `data` section is parsed from hex and written to memory.

## Example

```json
{
  "version": "HMv1",
  "pc": 0,
  "ac": 12,
  "ir": 0,
  "sr": 0,
  "text": {
    "0x0000": "LOAD 0x00A",
    "0x0001": "ADD 0x00B",
    "0x0002": "STORE 0x00C"
  },
  "data": {
    "0x000A": "0x0005",
    "0x000B": "0x0007",
    "0x000C": "0x000C"
  }
}
```

## Limitations

- **Linear Code Only**: The heuristic assumes the program starts at `0x0000` and is contiguous. Code segments separated by data may be incorrectly placed in the `data` section.
- **Ambiguity**: If a data value happens to match a valid opcode, the heuristic may include it in the `text` section if it is contiguous with address `0x0000`.
