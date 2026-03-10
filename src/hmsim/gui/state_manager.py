#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - State and History Manager."""

import hashlib
from dataclasses import dataclass
from typing import Optional, List, Callable


@dataclass(frozen=True)
class Snapshot:
    """Represents an atomic state of the simulator for comparison and history."""
    editor_text: str
    memory_hash: bytes
    architecture: str
    text_region: tuple[int, int]
    data_region: tuple[int, int]

    def __eq__(self, other):
        if not isinstance(other, Snapshot):
            return False
        return (self.editor_text == other.editor_text and
                self.memory_hash == other.memory_hash and
                self.architecture == other.architecture and
                self.text_region == other.text_region and
                self.data_region == other.data_region)


class StateManager:
    """Manages application state snapshots and undo/redo history."""

    def __init__(self, apply_snapshot_callback: Callable[[Snapshot], None]):
        self._apply_snapshot_callback = apply_snapshot_callback
        self._base_snapshot: Optional[Snapshot] = None
        self._history_stack: List[Snapshot] = []
        self._history_index: int = -1
        self._max_history = 100

    @property
    def is_modified(self) -> bool:
        """Check if current state differs from the base snapshot."""
        if not self._base_snapshot or self._history_index < 0:
            return False
        return self._history_stack[self._history_index] != self._base_snapshot

    def capture_snapshot(self, editor_text: str, memory_data: bytes,
                         architecture: str, text_region: tuple[int, int],
                         data_region: tuple[int, int]) -> Snapshot:
        """Create a lightweight representation of the current application state."""
        mem_hash = hashlib.md5(memory_data).digest()
        return Snapshot(
            editor_text=editor_text,
            memory_hash=mem_hash,
            architecture=architecture,
            text_region=text_region,
            data_region=data_region
        )

    def push_history(self, snapshot: Snapshot):
        """Add a snapshot to the undo stack, discarding any redo history."""
        # If this snapshot is identical to the current one, skip
        if self._history_index >= 0 and self._history_stack[self._history_index] == snapshot:
            return

        # Truncate redo history
        self._history_stack = self._history_stack[:self._history_index + 1]
        self._history_stack.append(snapshot)
        self._history_index += 1

        # Limit history size
        if len(self._history_stack) > self._max_history:
            self._history_stack.pop(0)
            self._history_index -= 1

    def undo(self):
        """Restore the previous state from history."""
        if self._history_index > 0:
            self._history_index -= 1
            self._apply_snapshot_callback(self._history_stack[self._history_index])

    def redo(self):
        """Restore the next state from history."""
        if self._history_index < len(self._history_stack) - 1:
            self._history_index += 1
            self._apply_snapshot_callback(self._history_stack[self._history_index])

    def sync_base_snapshot(self):
        """Set the current state as the baseline for 'modified' detection."""
        if self._history_index >= 0:
            self._base_snapshot = self._history_stack[self._history_index]

    def reset(self, initial_snapshot: Snapshot):
        """Clear history and start with a fresh snapshot."""
        self._history_stack = [initial_snapshot]
        self._history_index = 0
        self._base_snapshot = initial_snapshot
