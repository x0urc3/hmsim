# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details

from importlib.metadata import version, PackageNotFoundError
import subprocess
import os

FALLBACK_VERSION = "1.0.0"


def _get_version() -> str:
    """Get the package version dynamically from metadata or Git."""
    try:
        return version("hmsim")
    except PackageNotFoundError:
        pass

    git_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".git")
    if not os.path.exists(git_dir):
        return FALLBACK_VERSION

    try:
        result = subprocess.run(
            ["git", "describe", "--dirty", "--always", "--tags"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().lstrip("v")
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return FALLBACK_VERSION


__version__ = _get_version()
