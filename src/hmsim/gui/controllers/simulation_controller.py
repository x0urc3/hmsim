#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details
"""HM Simulator - Simulation Controller."""

from typing import Callable, Optional
try:
    from gi.repository import GLib
except ImportError:
    pass


class SimulationController:
    """Manages the execution flow of the simulator."""
    RUN_BATCH_SIZE = 1000

    def __init__(self, engine,
                 update_ui_callback: Callable[[], None],
                 show_error_callback: Callable[[str, int], None],
                 status_callback: Callable[[str, bool], None],
                 controls_callback: Callable[[bool], None]):
        self.engine = engine
        self._update_ui_callback = update_ui_callback
        self._show_error_callback = show_error_callback
        self._status_callback = status_callback
        self._controls_callback = controls_callback

        self._is_running = False
        self._run_source_id = None

    @property
    def is_running(self) -> bool:
        return self._is_running

    def set_engine(self, engine):
        """Update the engine instance if it changes (e.g. architecture change)."""
        self.engine = engine

    def step(self):
        """Execute a single instruction."""
        try:
            self.engine.step()
        except Exception as e:
            self._show_error_callback(str(e), self.engine.pc)

    def run(self):
        """Toggle the run/stop state."""
        if self._is_running:
            self.stop()
        else:
            self.start()

    def start(self):
        """Start the continuous execution loop."""
        if self._is_running:
            return
        self._is_running = True
        self._controls_callback(False) # Disable other controls
        self._status_callback("Running...", False)
        self._run_source_id = GLib.idle_add(self._run_loop)

    def stop(self):
        """Stop the continuous execution loop."""
        if not self._is_running:
            return
        self._is_running = False
        if self._run_source_id is not None:
            GLib.source_remove(self._run_source_id)
            self._run_source_id = None
        self._controls_callback(True) # Enable other controls
        self._status_callback("Ready", False)

    def reset(self):
        """Reset the engine state."""
        if self._is_running:
            self.stop()
        self.engine.reset()

    def _run_loop(self):
        if not self._is_running:
            return GLib.SOURCE_REMOVE
        try:
            self.engine.run_batch(self.RUN_BATCH_SIZE)
        except Exception as e:
            self._update_ui_callback()
            self.stop()
            self._show_error_callback(str(e), self.engine.pc)
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE
