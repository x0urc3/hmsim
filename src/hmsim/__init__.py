# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details

try:
    from ._version import version as __version__
except ImportError:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError

    try:
        __version__ = _pkg_version("hmsim")
    except PackageNotFoundError:
        __version__ = "1.0.0"
