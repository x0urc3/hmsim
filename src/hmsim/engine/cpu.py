"""HMv1 CPU Engine - Core simulation for HM processor."""

from .isa import OP_LOAD, OP_STORE, OP_ADD, HMV1_ISA


class HMv1Engine:
    """Engine for HMv1 processor simulation."""

    def __init__(self) -> None:
        self.pc: int = 0x0000
        self.ir: int = 0x0000
        self.ac: int = 0x0000
        self._memory: list[int] = [0] * 65536

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
        if opcode == OP_LOAD:
            self.ac = self._memory[address]
            return HMV1_ISA["LOAD"][1]
        elif opcode == OP_STORE:
            self._memory[address] = self.ac
            return HMV1_ISA["STORE"][1]
        elif opcode == OP_ADD:
            self.ac = (self.ac + self._memory[address]) & 0xFFFF
            return HMV1_ISA["ADD"][1]
        else:
            raise ValueError(f"Unknown opcode: {opcode:#x}")

    def step(self) -> int:
        """Execute one instruction cycle.

        Fetches instruction at PC, decodes it, executes it,
        and increments PC.

        Returns:
            Number of cycles consumed.
        """
        instruction = self._memory[self.pc]
        opcode, address = self.decode(instruction)
        cycles = self.execute(opcode, address)
        self.pc = (self.pc + 1) & 0xFFFF
        return cycles
