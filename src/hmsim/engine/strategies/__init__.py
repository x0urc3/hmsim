#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""Execution strategies for HM processor versions.

This module implements the Strategy pattern to support version-specific
instruction execution for HMv1-HMv4.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cpu import HMEngine


class ExecutionStrategy(ABC):
    """Base class for version-specific execution strategies."""

    def execute(self, engine: "HMEngine", opcode: int, address: int) -> int:
        """Execute instruction and return cycle count.

        Args:
            engine: The CPU engine instance.
            opcode: 4-bit opcode.
            address: 12-bit memory address.

        Returns:
            Number of cycles consumed.
        """
        from ..isa import OP_LOAD, OP_STORE, OP_ADD

        if opcode == OP_LOAD:
            engine.ac = engine._memory[address]
            return engine.isa["LOAD"][1]
        elif opcode == OP_STORE:
            engine.write_memory(address, engine.ac, notify=False)
            return engine.isa["STORE"][1]
        elif opcode == OP_ADD:
            engine.ac = (engine.ac + engine._memory[address]) & 0xFFFF
            engine._update_sr(engine.ac)
            return engine.isa["ADD"][1]
        else:
            return self._execute_extended(engine, opcode, address)

    @abstractmethod
    def _execute_extended(self, engine: "HMEngine", opcode: int, address: int) -> int:
        """Handle version-specific opcodes.

        Args:
            engine: The CPU engine instance.
            opcode: 4-bit opcode.
            address: 12-bit memory address.

        Returns:
            Number of cycles consumed.

        Raises:
            ValueError: If opcode is unknown.
        """
        pass


class HMv1Strategy(ExecutionStrategy):
    """Execution strategy for HMv1 processor."""

    def _execute_extended(self, engine: "HMEngine", opcode: int, address: int) -> int:
        raise ValueError(f"Unknown opcode: {opcode:#x}")


class HMv2Strategy(ExecutionStrategy):
    """Execution strategy for HMv2 processor."""

    def _execute_extended(self, engine: "HMEngine", opcode: int, address: int) -> int:
        from ..isa import OP_SUB, OP_JMP, OP_JMPZ

        if opcode == OP_SUB:
            engine.ac = (engine.ac - engine._memory[address]) & 0xFFFF
            engine._update_sr(engine.ac)
            return engine.isa["SUB"][1]
        elif opcode == OP_JMP:
            engine.pc = address
            return engine.isa["JMP"][1]
        elif opcode == OP_JMPZ:
            if engine.sr & 0x4000:
                engine.pc = address
            return engine.isa["JMPZ"][1]
        else:
            raise ValueError(f"Unknown opcode: {opcode:#x}")


class HMv3Strategy(ExecutionStrategy):
    """Execution strategy for HMv3 processor (subroutine support)."""

    def _execute_extended(self, engine: "HMEngine", opcode: int, address: int) -> int:
        from ..isa import OP_CALL, OP_RETURN

        if opcode == OP_CALL:
            engine.ac = (engine.pc + 1) & 0xFFFF
            engine.pc = address
            return engine.isa["CALL"][1]
        elif opcode == OP_RETURN:
            engine.pc = engine.ac
            return engine.isa["RETURN"][1]
        else:
            raise ValueError(f"Unknown opcode: {opcode:#x}")


class HMv4Strategy(ExecutionStrategy):
    """Execution strategy for HMv4 processor (indirect addressing)."""

    def _execute_extended(self, engine: "HMEngine", opcode: int, address: int) -> int:
        from ..isa import OP_LOAD_INDIRECT, OP_STORE_INDIRECT

        if opcode == OP_LOAD_INDIRECT:
            target_addr = engine._memory[address] & 0xFFFF
            engine.ac = engine._memory[target_addr]
            return 10
        elif opcode == OP_STORE_INDIRECT:
            target_addr = engine._memory[address] & 0xFFFF
            engine.write_memory(target_addr, engine.ac, notify=False)
            return 25
        else:
            raise ValueError(f"Unknown opcode: {opcode:#x}")


_STRATEGIES = {
    "HMv1": HMv1Strategy,
    "HMv2": HMv2Strategy,
    "HMv3": HMv3Strategy,
    "HMv4": HMv4Strategy,
}


def get_strategy(arch: str) -> ExecutionStrategy:
    """Get the execution strategy for a given HM architecture.

    Args:
        arch: HM architecture string (e.g., "HMv1", "HMv2").

    Returns:
        ExecutionStrategy instance for the architecture.

    Raises:
        ValueError: If architecture is not supported.
    """
    if arch not in _STRATEGIES:
        raise ValueError(f"Unsupported architecture: {arch}")
    return _STRATEGIES[arch]()
