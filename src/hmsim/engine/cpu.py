"""HM CPU Engine - Core simulation for HM processor family."""

from typing import Optional

from .isa import VERSION_ISA, HMV1_ISA


class HMEngine:
    """Engine for HM processor simulation (supports HMv1-HMv4)."""

    VALID_VERSIONS = ("HMv1", "HMv2")

    def __init__(self, version: str = "HMv1") -> None:
        if version not in self.VALID_VERSIONS:
            raise ValueError(f"Invalid version: {version}. Valid: {self.VALID_VERSIONS}")
        self.version: str = version
        self.pc: int = 0x0000
        self.ir: int = 0x0000
        self.ac: int = 0x0000
        self.sr: int = 0x0000
        self._memory: list[int] = [0] * 65536

    @property
    def isa(self) -> dict:
        """Get the ISA definition for this version."""
        return VERSION_ISA[self.version]

    def _update_sr(self, result: int) -> None:
        """Update Status Register flags based on arithmetic result.

        SR Layout (HMv2+):
        - Bit 15 (SF): Sign Flag - IMPLEMENTED
        - Bit 14 (ZF): Zero Flag - IMPLEMENTED
        - Bit 13 (EF): Equality Flag - TODO: Not yet implemented
        - Bit 12 (OF): Overflow Flag - TODO: Not yet implemented
        """
        if self.version == "HMv2":
            self.sr = 0
            if result & 0x8000:
                self.sr |= 0x8000
            if result == 0:
                self.sr |= 0x4000
            # TODO: Implement EF (Equality Flag) - needed for CMP instruction
            # if equality detected: self.sr |= 0x2000
            # TODO: Implement OF (Overflow Flag) - needed for signed arithmetic
            # if overflow detected: self.sr |= 0x1000

    def _check_version_support(self, opcode: int) -> None:
        """Check if opcode is supported in current version."""
        opcode_to_mnemonic = {v[0]: k for k, v in HMV1_ISA.items()}
        mnemonic = opcode_to_mnemonic.get(opcode)
        if mnemonic and mnemonic not in self.isa:
            raise ValueError(f"Opcode {opcode:#x} not supported in {self.version}")

    def decode(self, instruction: int) -> tuple[int, int]:
        """Decode instruction into opcode and address.

        Args:
            instruction: 16-bit instruction word.

        Returns:
            Tuple of (opcode, address).
        """
        opcode = (instruction >> 12) & 0xF
        address = instruction & 0x0FFF
        return opcode, address

    def execute(self, opcode: int, address: int) -> int:
        """Execute instruction and return cycle count.

        Args:
            opcode: 4-bit opcode (from isa.py).
            address: 12-bit memory address.

        Returns:
            Number of cycles consumed.
        """
        from .isa import OP_LOAD, OP_STORE, OP_ADD, OP_SUB, OP_JMP, OP_JMPZ

        self._check_version_support(opcode)

        if opcode == OP_LOAD:
            self.ac = self._memory[address]
            return self.isa["LOAD"][1]
        elif opcode == OP_STORE:
            self._memory[address] = self.ac
            return self.isa["STORE"][1]
        elif opcode == OP_ADD:
            self.ac = (self.ac + self._memory[address]) & 0xFFFF
            self._update_sr(self.ac)
            return self.isa["ADD"][1]
        elif opcode == OP_SUB:
            self.ac = (self.ac - self._memory[address]) & 0xFFFF
            self._update_sr(self.ac)
            return self.isa["SUB"][1]
        elif opcode == OP_JMP:
            self.pc = address
            return self.isa["JMP"][1]
        elif opcode == OP_JMPZ:
            if self.sr & 0x4000:
                self.pc = address
            return self.isa["JMPZ"][1]
        else:
            raise ValueError(f"Unknown opcode: {opcode:#x}")

    def step(self) -> int:
        """Execute one instruction cycle.

        Fetches instruction at PC, decodes it, executes it,
        and increments PC (unless changed by JMP/JMPZ).

        Returns:
            Number of cycles consumed.
        """
        instruction = self._memory[self.pc]
        opcode, address = self.decode(instruction)
        old_pc = self.pc
        cycles = self.execute(opcode, address)
        if self.pc == old_pc:
            self.pc = (self.pc + 1) & 0xFFFF
        return cycles


class HMv1Engine(HMEngine):
    """Legacy HMv1 engine for backward compatibility."""

    def __init__(self) -> None:
        super().__init__("HMv1")
