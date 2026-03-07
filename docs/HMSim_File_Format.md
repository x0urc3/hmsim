# HMSim State File Format

The HM Simulator uses a JSON-based state file format to persist and restore simulator snapshots. This enables saving the current execution state (registers and memory) and resuming later.

## Overview

State files capture the complete runtime context of the simulator, including all CPU registers and non-zero memory locations. The format is designed for:

- **Save/Resume**: Persist simulation state at any point
- **Debugging**: Capture and share reproduction states
- **Testing**: Load predefined states for test scenarios

## JSON Schema

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `version` | string | `"HMv1"`, `"HMv2"` | Simulator version (HMv3/v4 loaded as HMv2) |
| `pc` | integer | 0 – 65535 | Program Counter (next instruction address) |
| `ac` | integer | 0 – 65535 | Accumulator (primary data register) |
| `ir` | integer | 0 – 65535 | Instruction Register (current instruction) |
| `sr` | integer | 0 – 65535 | Status Register (HMv2+ only, zero flag) |
| `memory` | object | keys: 0–65535, values: 0–65535 | Sparse memory map (non-zero entries only) |

## Field Details

### version

String identifying the HM processor version. Determines available instructions and behavior.

- `"HMv1"`: Base instruction set (LOAD, STORE, ADD)
- `"HMv2"`: Adds SUB, JMP, JMPZ, and Status Register (SR)

When loading a state file with an unrecognized version (HMv3, HMv4), the simulator defaults to HMv2 and displays a warning.

### pc (Program Counter)

16-bit register holding the memory address of the next instruction to fetch. After each instruction executes, PC increments by 1 (or jumps to a new address for branch instructions).

### ac (Accumulator)

16-bit primary data register used for all arithmetic operations. Most instructions operate on AC as an implicit operand.

### ir (Instruction Register)

16-bit register that latches the current instruction during decode and execution phases. Contains the raw opcode and operand bits.

### sr (Status Register)

16-bit status register available in HMv2 and later versions. Contains flag bits including:

- **Zero Flag (bit 0)**: Set when the result of the last arithmetic operation was zero

For HMv1 states, this field is present but always 0.

### memory

Sparse dictionary mapping memory addresses (0–65535) to 16-bit values. Only non-zero memory locations are stored to minimize file size.

- **Keys**: Decimal or string representation of memory addresses
- **Values**: 16-bit unsigned integers (0–65535)

Addresses with value 0 are omitted from the file.

## Saving

When saving state:

1. All register values are written as integers
2. Memory is serialized as a sparse map: `{str(addr): val for addr, val in enumerate(memory) if val != 0}`
3. The file is written with 2-space indentation for readability

```python
memory = {str(addr): val for addr, val in enumerate(self.engine._memory) if val != 0}
state = {
    "version": self.current_version,
    "pc": self.engine.pc,
    "ac": self.engine.ac,
    "ir": self.engine.ir,
    "sr": self.engine.sr,
    "memory": memory
}
```

## Loading

When loading state:

1. Version is read and validated (defaults to HMv1 if missing)
2. Unknown versions (HMv3, HMv4) are mapped to HMv2 with a warning
3. Registers are restored directly from the file
4. Each memory entry is validated (0 ≤ address < 65536) before writing
5. Values are masked to 16 bits: `val & 0xFFFF`

```python
self.engine.pc = state.get("pc", 0)
self.engine.ac = state.get("ac", 0)
self.engine.ir = state.get("ir", 0)
self.engine.sr = state.get("sr", 0)

for addr_str, val in memory.items():
    addr = int(addr_str)
    if 0 <= addr < 65536:
        self.engine._memory[addr] = val & 0xFFFF
```

## Example

```json
{
  "version": "HMv1",
  "pc": 0,
  "ac": 0,
  "ir": 0,
  "sr": 0,
  "memory": {
    "0": 4352,
    "256": 5
  }
}
```

In this example:
- Version is HMv1
- All registers are initialized to 0
- Memory address 0 contains the value 4352 (0x1100)
- Memory address 256 contains the value 5

## Limitations

- **Version Compatibility**: States saved with HMv3 or HMv4 are loaded as HMv2. Some state information specific to those versions may be lost.
- **Sparse Memory Only**: Zero-initialized memory is not persisted, which means loading a state file does not reset memory to zero—it only writes non-zero values.
- **No Metadata**: The format does not include timestamps, labels, or user notes.
