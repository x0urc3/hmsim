#!/usr/bin/env python3
# Copyright 2026 Khairulmizam Samsudin <xource@gmail.com>
# Licensed under the Apache License, Version 2.0; see LICENSE for details

"""
Build script to create HM Simulator executables using PyInstaller.
Supports both Linux and Windows (MSYS2) environments.
"""

import os
import subprocess
import sys
import shutil

# Add src to sys.path immediately so hmsim can be imported during build
_script_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_script_dir)
_src_dir = os.path.abspath(os.path.join(_root_dir, "src"))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    import hmsim
    print(f"DEBUG: Found hmsim at {hmsim.__file__}")
    print(f"DEBUG: hmsim path: {getattr(hmsim, '__path__', 'No __path__')}")
except ImportError:
    print("DEBUG: hmsim not found initially")


def get_venv_bin():
    """Get the virtual environment bin directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    venv_dir = os.path.join(root_dir, "venv", "bin")
    if os.path.exists(venv_dir):
        return venv_dir
    return None


def get_pyinstaller_path():
    """Get the path to pyinstaller executable."""
    venv_bin = get_venv_bin()
    if venv_bin:
        pyinstaller_path = os.path.join(venv_bin, "pyinstaller")
        if os.path.exists(pyinstaller_path):
            return pyinstaller_path
    return "pyinstaller"


def run_command(cmd, shell=False, env=None):
    """Utility to run a command and handle errors."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        subprocess.run(cmd, check=True, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def check_pyinstaller():
    """Check if pyinstaller is installed, install if missing."""
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} is already installed.")
        return True
    except ImportError:
        venv_bin = get_venv_bin()
        if venv_bin:
            pip_path = os.path.join(venv_bin, "pip")
            print("PyInstaller is not installed. Installing...")
            run_command([pip_path, "install", "pyinstaller"])
            return True
        print("PyInstaller is not installed and no venv found. Please install manually.")
        return False


def get_msys_prefix():
    """Detect MSYS2 subsystem and return the package prefix."""
    msystem = os.environ.get('MSYSTEM')
    if msystem == 'MINGW64':
        return 'mingw-w64-x86_64-'
    elif msystem == 'UCRT64':
        return 'mingw-w64-ucrt-x86_64-'
    return None


def get_msys_gtk4_path():
    """Get the path to GTK4 in MSYS2 environment."""
    msys_prefix = get_msys_prefix()
    if msys_prefix:
        if msys_prefix.startswith('mingw-w64-ucrt'):
            return "/ucrt64"
        else:
            return "/mingw64"
    return None


def is_windows():
    """Check if running on Windows (native or MSYS2)."""
    return sys.platform.startswith("win") or get_msys_prefix() is not None


def get_data_separator():
    """Get the appropriate path separator for --add-data arguments."""
    return ':' if sys.platform.startswith("linux") else ';'


def merge_internal_dirs(src_dirs, dest_dir):
    """Merge multiple _internal directories into one, avoiding duplicates."""
    os.makedirs(dest_dir, exist_ok=True)

    for src_base in src_dirs:
        src_internal = os.path.join(src_base, "_internal")
        if not os.path.exists(src_internal):
            continue

        for item in os.listdir(src_internal):
            src_path = os.path.join(src_internal, item)
            dest_path = os.path.join(dest_dir, item)

            if os.path.isdir(src_path):
                if os.path.exists(dest_path):
                    merge_internal_dirs([src_path], dest_path)
                else:
                    shutil.copytree(src_path, dest_path)
            else:
                if not os.path.exists(dest_path):
                    shutil.copy2(src_path, dest_path)


def build():
    """Main build function."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(root_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # Try to import hmsim to ensure it is found
    try:
        import hmsim
        print(f"  Found hmsim package at: {hmsim.__file__}")
    except ImportError:
        print("  Warning: hmsim package not found in sys.path")
    os.chdir(root_dir)
    print(f"Building from: {root_dir}")

    is_linux = sys.platform.startswith("linux")
    is_windows_msys = get_msys_prefix() is not None

    if is_linux:
        print("Detected Linux environment.")
    elif is_windows_msys:
        print(f"Detected MSYS2 environment: {os.environ.get('MSYSTEM')}")
    else:
        print("Error: This script must be run on Linux or in an MSYS2 MINGW64/UCRT64 shell.")
        sys.exit(1)

    if is_windows_msys:
        msys_prefix = get_msys_prefix()
        system_pkgs = [
            f"{msys_prefix}python",
            f"{msys_prefix}python-gobject",
            f"{msys_prefix}gtk4",
        ]
        print(f"Ensuring system dependencies: {', '.join(system_pkgs)}")
        run_command(["pacman", "-S", "--needed", "--noconfirm"] + system_pkgs)

    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} is already installed.")
    except ImportError:
        check_pyinstaller()

    dist_dir = os.path.join(root_dir, "dist")
    temp_build_dir = os.path.join(root_dir, "build_temp")
    build_dir = os.path.join(root_dir, "build")

    if os.path.exists(dist_dir):
        print(f"Cleaning existing dist directory: {dist_dir}")
        shutil.rmtree(dist_dir)
    if os.path.exists(temp_build_dir):
        shutil.rmtree(temp_build_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(temp_build_dir, exist_ok=True)

    print("Building executables...")

    wrapper_scripts = {
        "hmsim": '''#!/usr/bin/env python3
import sys
import os

# PyInstaller onedir mode: dependencies are in the _internal directory
if getattr(sys, 'frozen', False):
    internal_dir = os.path.join(os.path.dirname(sys.executable), "_internal")
    if os.path.exists(internal_dir) and internal_dir not in sys.path:
        sys.path.insert(0, internal_dir)

try:
    from hmsim.gui.hm_gui import main
    if __name__ == "__main__":
        main()
except Exception as e:
    import traceback
    with open("error_log.txt", "w") as f:
        f.write(f"Exception: {str(e)}\\n")
        f.write("sys.path:\\n")
        f.write("\\n".join(sys.path))
        f.write("\\n\\nFull Traceback:\\n")
        traceback.print_exc(file=f)
    raise
''',
    }

    scripts_dir = os.path.join(root_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    for name, content in wrapper_scripts.items():
        script_path = os.path.abspath(os.path.join(scripts_dir, f"{name}_wrapper.py"))
        print(f"  Creating wrapper script: {script_path}")
        with open(script_path, "w") as f:
            f.write(content)
        print(f"  Wrapper content first 100 chars: {content[:100]}...")

    entry_points = [
        ("hmsim", os.path.join(scripts_dir, "hmsim_wrapper.py"), True),
    ]

    hidden_imports = [
        "gi",
        "gi.repository.Gtk",
        "gi.repository.Gio",
        "gi.repository.GLib",
        "hmsim",
        "hmsim.engine",
        "hmsim.engine.cpu",
        "hmsim.engine.isa",
        "hmsim.engine.strategies",
        "hmsim.gui",
        "hmsim.gui.hm_gui",
        "hmsim.gui.main_window",
        "hmsim.gui.widgets",
    ]

    pyinstaller_cmd = get_pyinstaller_path()
    build_outputs = []

    for name, entry, is_gui in entry_points:
        print(f"\n=== Building {name} ===")

        temp_dir = os.path.join(temp_build_dir, name)

        src_abs_path = os.path.abspath(os.path.join(root_dir, "src"))
        cmd = [
            pyinstaller_cmd,
            "--onedir",
            "--name", name,
            "--distpath", temp_dir,
            "--workpath", os.path.join(temp_build_dir, f"work_{name}"),
            "--collect-all", "gi",
            "--collect-all", "hmsim",
            "--collect-submodules", "hmsim",
            "--paths", src_abs_path,
            "--add-data", f"{os.path.join(src_abs_path, 'hmsim')}{os.pathsep}hmsim",
        ]

        if is_gui:
            cmd.append("--windowed")
        else:
            cmd.append("--console")

        for imp in hidden_imports:
            cmd.extend(["--hidden-import", imp])

        cmd.append(f"--specpath={build_dir}")
        cmd.append(entry)

        try:
            subprocess.run(cmd, check=True, cwd=root_dir)
            print(f"{name} built successfully!")
            build_outputs.append((name, temp_dir, is_gui))
        except subprocess.CalledProcessError as e:
            print(f"Build failed for {name} with exit code {e.returncode}")
            sys.exit(e.returncode)

    print("\n=== Creating shared _internal ===")

    shared_internal = os.path.join(dist_dir, "_internal")
    os.makedirs(shared_internal, exist_ok=True)

    first_internal = os.path.join(build_outputs[0][1], build_outputs[0][0], "_internal")
    if os.path.exists(first_internal):
        for item in os.listdir(first_internal):
            src = os.path.join(first_internal, item)
            dst = os.path.join(shared_internal, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    print(f"  Copied base _internal from first build")

    for i in range(1, len(build_outputs)):
        name, temp_dir, _ = build_outputs[i]
        other_internal = os.path.join(temp_dir, name, "_internal")
        if os.path.exists(other_internal):
            for item in os.listdir(other_internal):
                src = os.path.join(other_internal, item)
                dst = os.path.join(shared_internal, item)
                if os.path.isdir(src):
                    for subitem in os.listdir(src):
                        src_sub = os.path.join(src, subitem)
                        dst_sub = os.path.join(dst, subitem)
                        if not os.path.exists(dst_sub):
                            if os.path.isdir(src_sub):
                                shutil.copytree(src_sub, dst_sub)
                            else:
                                shutil.copy2(src_sub, dst_sub)
                else:
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
    print(f"  Merged additional _internal files")

    if is_linux:
        libpython_src = "/usr/lib/x86_64-linux-gnu/libpython3.12.so.1.0"
        libpython_dst = os.path.join(shared_internal, "libpython3.12.so.1.0")
        if os.path.exists(libpython_src) and not os.path.exists(libpython_dst):
            shutil.copy2(libpython_src, libpython_dst)
            print(f"  Copied libpython")
    elif is_windows_msys:
        msys_gtk_path = get_msys_gtk4_path()
        if msys_gtk_path:
            mingw_bin = f"/usr{msys_gtk_path}/bin"
            if os.path.exists(mingw_bin):
                for f in os.listdir(mingw_bin):
                    if f.endswith(".dll") and "lib" in f.lower() or f.startswith("lib"):
                        src = os.path.join(mingw_bin, f)
                        dst = os.path.join(shared_internal, f)
                        if not os.path.exists(dst):
                            shutil.copy2(src, dst)
                print(f"  Copied GTK4 DLLs from {mingw_bin}")

    print("\n=== Copying executables to dist root ===")

    exe_ext = ".exe" if is_windows() else ""

    for name, temp_dir, is_gui in build_outputs:
        src = os.path.join(temp_dir, name, name + exe_ext)
        dst = os.path.join(dist_dir, name + exe_ext)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            if not is_windows():
                os.chmod(dst, 0o755)
            print(f"  Copied {name}{exe_ext} to {dst}")

    print("\n=== Copying resources to dist ===")

    examples_src = os.path.join(root_dir, "examples")
    examples_dst = os.path.join(dist_dir, "examples")
    os.makedirs(examples_dst, exist_ok=True)
    if os.path.exists(examples_src):
        for f in os.listdir(examples_src):
            if f.endswith(".hm"):
                shutil.copy2(os.path.join(examples_src, f), examples_dst)
        print(f"  Copied examples to {examples_dst}")

    docs_user_src = os.path.join(root_dir, "docs", "user")
    docs_user_dst = os.path.join(dist_dir, "_internal", "docs", "user")
    os.makedirs(docs_user_dst, exist_ok=True)
    if os.path.exists(docs_user_src):
        for f in os.listdir(docs_user_src):
            if f.endswith(".md"):
                shutil.copy2(os.path.join(docs_user_src, f), docs_user_dst)
        print(f"  Copied docs/user to {docs_user_dst}")

    schema_src = os.path.join(root_dir, "src", "hmsim", "engine", "schema.json")
    schema_dst = os.path.join(dist_dir, "_internal", "hmsim", "engine", "schema.json")
    # Ensure hmsim/engine directory exists
    os.makedirs(os.path.dirname(schema_dst), exist_ok=True)
    if os.path.exists(schema_src):
        shutil.copy2(schema_src, schema_dst)
        print(f"  Copied schema.json to {schema_dst}")

    license_file = os.path.join(root_dir, "LICENSE")
    notice_file = os.path.join(root_dir, "NOTICE")
    if os.path.exists(license_file):
        shutil.copy2(license_file, dist_dir)
        print(f"  Copied LICENSE to {dist_dir}")
    if os.path.exists(notice_file):
        shutil.copy2(notice_file, dist_dir)
        print(f"  Copied NOTICE to {dist_dir}")

    print("\n=== Cleaning up ===")
    shutil.rmtree(temp_build_dir)
    print("  Removed temp build directory")

    for name in ["hmsim"]:
        wrapper_path = os.path.join(scripts_dir, f"{name}_wrapper.py")
        if os.path.exists(wrapper_path):
            os.remove(wrapper_path)
            print(f"  Removed {wrapper_path}")

    print("\n=== Creating distribution archive ===")

    if is_windows_msys:
        import zipfile
        zip_name = os.path.join(root_dir, "hmsim_windows.zip")
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, arcname)
        print(f"  Created {zip_name}")

    print("\n=== Build Summary ===")
    for name, _, _ in build_outputs:
        bin_path = os.path.join(dist_dir, name + (".exe" if is_windows() else ""))
        if os.path.exists(bin_path):
            print(f"  {name}: {bin_path}")

    print("\nBuild complete!")
    print(f"Executables are in: {dist_dir}")
    if is_windows_msys:
        print(f"Archive: {os.path.join(root_dir, 'hmsim_windows.zip')}")


if __name__ == "__main__":
    build()
