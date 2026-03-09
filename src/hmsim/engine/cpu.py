#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM CPU Engine - Core simulation for HM processor family."""

from typing import Callable, Dict, List, Optional

from .isa import ARCH_ISA, HMV1_ISA
from .strategies import get_strategy
from .state import load_state, save_state


class HMEngine:
    """Engine for HM processor simulation (supports HMv1-HMv4)."""

    VALID_ARCHITECTURES = ("HMv1", "HMv2", "HMv3", "HMv4")

    def __init__(self, architecture: str = "HMv1") -> None:
        if architecture not in self.VALID_ARCHITECTURES:
            raise ValueError(f"Invalid architecture: {architecture}. Valid: {self.VALID_ARCHITECTURES}")
        self.architecture: str = architecture
        self.pc: int = 0x0000
        self.ir: int = 0x0000
        self.ac: int = 0x0000
        self.sr: int = 0x0000
        self.total_cycles: int = 0
        self.total_instructions: int = 0
        self.comments: Dict[int, str] = {}
        self._memory: list[int] = [0] * 65536
        self.modified_addresses: set[int] = set()
        self._strategy = get_strategy(architecture)
        self._observers: List[Callable[[], None]] = []
        self._text_region: tuple[int, int] = (0x0000, 0x0100)
        self._data_region: tuple[int, int] = (0x0101, 0xFFFF)

    @property
    def text_region(self) -> tuple[int, int]:
        return self._text_region

    @text_region.setter
    def text_region(self, value: tuple[int, int]) -> None:
        start, end = value
        if not (0 <= start <= end <= 0xFFFF):
            raise ValueError(f"Invalid text region: {start:#06x}-{end:#06x}")
        if self._data_region:
            ts, te = start, end
            ds, de = self._data_region
            if not (te < ds or ts > de):
                raise ValueError("Text region cannot overlap with data region")
        self._text_region = (start, end)

    @property
    def data_region(self) -> tuple[int, int]:
        return self._data_region

    @data_region.setter
    def data_region(self, value: tuple[int, int]) -> None:
        start, end = value
        if not (0 <= start <= end <= 0xFFFF):
            raise ValueError(f"Invalid data region: {start:#06x}-{end:#06x}")
        if self._text_region:
            ts, te = self._text_region
            ds, de = start, end
            if not (te < ds or ts > de):
                raise ValueError("Data region cannot overlap with text region")
        self._data_region = (start, end)

    def set_regions(self, text_region: tuple[int, int], data_region: tuple[int, int]) -> None:
        ts, te = text_region
        ds, de = data_region
        if not (te < ds or ts > de):
            raise ValueError("Text and data regions cannot overlap")
        if not (0 <= ts <= te <= 0xFFFF and 0 <= ds <= de <= 0xFFFF):
            raise ValueError("Regions must be within 0x0000-0xFFFF")
        self._text_region = (ts, te)
        self._data_region = (ds, de)
        self._notify_observers()

    def load_state(self, file_path: str) -> str:
        """Load engine state from a JSON file.

        Args:
            file_path: Path to the input JSON file.

        Returns:
            The architecture string from the state file.
        """
        architecture = load_state(self, file_path)
        self._notify_observers()
        return architecture

    def save_state(self, file_path: str) -> None:
        """Save engine state to a JSON file.

        Args:
            file_path: Path to the output JSON file.
        """
        save_state(self, file_path)

    def register_observer(self, callback: Callable[[], None]) -> None:
        """Register a callback to be notified on state changes."""
        self._observers.append(callback)

    def _notify_observers(self) -> None:
        """Notify all observers of state change."""
        for callback in self._observers:
            callback()

    def write_memory(self, address: int, value: int, notify: bool = True) -> None:
        """Write a 16-bit value to memory.

        Args:
            address: 16-bit memory address.
            value: 16-bit value to write.
            notify: If True, notify observers after write.
        """
        if 0 <= address < 65536:
            self._memory[address] = value & 0xFFFF
            self.modified_addresses.add(address)
            if notify:
                self._notify_observers()

    def clear_modified(self) -> None:
        """Clear the set of modified addresses."""
        self.modified_addresses.clear()

    def read_memory(self, address: int) -> int:
        """Read a 16-bit value from memory."""
        return self._memory[address] if 0 <= address < 65536 else 0

    def reset(self) -> None:
        """Reset registers and statistics to initial state.

        Preserves memory content so user can re-run loaded/edited programs.
        """
        self.pc = 0x0000
        self.ir = 0x0000
        self.ac = 0x0000
        self.sr = 0x0000
        self.total_cycles = 0
        self.total_instructions = 0
        self._notify_observers()

    @property
    def isa(self) -> dict:
        """Get the ISA definition for this architecture."""
        return ARCH_ISA[self.architecture]

    def _update_sr(self, result: int) -> None:
        """Update Status Register flags based on arithmetic result.

        SR Layout (HMv2+):
        - Bit 15 (SF): Sign Flag - IMPLEMENTED
        - Bit 14 (ZF): Zero Flag - IMPLEMENTED
        - Bit 13 (EF): Equality Flag - TODO: Not yet implemented
        - Bit 12 (OF): Overflow Flag - TODO: Not yet implemented
        """
        if self.architecture == "HMv2":
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
            raise ValueError(f"Opcode {opcode:#x} not supported in {self.architecture}")

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
        self.total_instructions += 1
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
        try:
            for _ in range(count):
                cycles = self.step(notify=False)
                batch_cycles += cycles
        finally:
            self._notify_observers()
        return batch_cycles
