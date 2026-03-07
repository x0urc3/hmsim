"""HM CPU Engine - Core simulation for HM processor family."""

from typing import Callable, List, Optional

from .isa import VERSION_ISA, HMV1_ISA
from .strategies import get_strategy


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
        self.total_cycles: int = 0
        self._memory: list[int] = [0] * 65536
        self._strategy = get_strategy(version)
        self._observers: List[Callable[[], None]] = []

    def register_observer(self, callback: Callable[[], None]) -> None:
        """Register a callback to be notified on state changes."""
        self._observers.append(callback)

    def _notify_observers(self) -> None:
        """Notify all observers of state change."""
        for callback in self._observers:
            callback()

    def write_memory(self, address: int, value: int) -> None:
        """Write a 16-bit value to memory."""
        if 0 <= address < 65536:
            self._memory[address] = value & 0xFFFF
            self._notify_observers()

    def read_memory(self, address: int) -> int:
        """Read a 16-bit value from memory."""
        return self._memory[address] if 0 <= address < 65536 else 0

    def reset(self) -> None:
        """Reset the engine to initial state."""
        self.pc = 0x0000
        self.ir = 0x0000
        self.ac = 0x0000
        self.sr = 0x0000
        self.total_cycles = 0
        self._memory = [0] * 65536
        self._notify_observers()

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
        self._check_version_support(opcode)
        return self._strategy.execute(self, opcode, address)

    def step(self, notify: bool = True) -> int:
        """Execute one instruction cycle.

        Fetches instruction at PC, decodes it, executes it,
        and increments PC (unless changed by JMP/JMPZ).

        Args:
            notify: If True, notify observers after execution.

        Returns:
            Number of cycles consumed.
        """
        instruction = self._memory[self.pc]
        self.ir = instruction
        opcode, address = self.decode(instruction)
        old_pc = self.pc
        cycles = self.execute(opcode, address)
        self.total_cycles += cycles
        if self.pc == old_pc:
            self.pc = (self.pc + 1) & 0xFFFF
        if notify:
            self._notify_observers()
        return cycles

    def run_batch(self, count: int = 1000) -> int:
        """Execute multiple instructions without UI updates.

        Args:
            count: Number of instructions to execute.

        Returns:
            Total number of cycles consumed in this batch.
        """
        batch_cycles = 0
        for _ in range(count):
            cycles = self.step(notify=False)
            batch_cycles += cycles
        self._notify_observers()
        return batch_cycles


class HMv1Engine(HMEngine):
    """Legacy HMv1 engine for backward compatibility."""

    def __init__(self) -> None:
        super().__init__("HMv1")
