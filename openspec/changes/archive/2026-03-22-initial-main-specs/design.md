## Context

HM-Sim is a multi-architecture simulator implemented in Python with a GTK4 (PyGObject) GUI. It uses a decoupled architectural engine to simulate various versions of the Hypothetical Microprocessor (HM). The current version of the project is a production-ready prototype that supports HMv1 through HMv4 features.

## Goals / Non-Goals

**Goals:**
- Formalize the architectural simulation patterns (Strategy Pattern, Observer Pattern)
- Document the session-bound provenance and audit logging system
- Establish the data format (16-bit signed magnitude) and word layout (4-bit opcode, 12-bit address)
- Define the incremental instruction set progression

**Non-Goals:**
- Introduce new features (this change is for baseline documentation)
- Refactor existing code (except where required for consistency with the new specs)

## Decisions

1. **Strategy Pattern for Instruction Logic** - Use different strategies for HMv1 through HMv4 to ensure opcode sets are strictly partitioned and inherited.
2. **Observer Pattern for UI State Sync** - Engine emits signals when registers or memory change. GUI widgets subscribe to these signals to update themselves.
3. **16-bit Signed Magnitude for Data** - MSB (Bit 15 in standard, Bit 0 in PDF terminology) is the sign bit, bits 0-14 (standard) are magnitude.
4. **JSON-based State Persistence** - Use structured JSON for `.hm` files to capture memory regions, architectural setup, and session metadata.
5. **Debounced Real-time Assembly Sync** - Assembly updates in the editor trigger a background assembly process with a slight debounce to prevent UI stuttering.

## Risks / Trade-offs

- **Risk**: Discrepancies between existing documentation (PDFs, Markdown) and the new OpenSpec baseline. -> **Mitigation**: Use `isa.py` and `cpu.py` as the ultimate source of truth for the baseline.
- **Trade-off**: The PDF documentation uses a 0-indexed MSB convention (Bit 0 is MSB), whereas Python/standard hardware logic uses 0-indexed LSB (Bit 15 is MSB). -> **Decision**: Standardize on standard 15-indexed MSB for internal logic, but allow the spec to reference the PDF bit indices where helpful for clarity.
