#!/usr/bin/env python3
"""Cross-platform bootstrapper for local Deep-Live-Cam installs."""

import argparse
import os
import platform
import shutil
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def _run(cmd, cwd=None, check=True):
    subprocess.run(cmd, cwd=cwd, check=check)


def _console(message):
    print(f"[bootstrap] {message}")


def _resolve_script():
    system = platform.system()
    if system == "Windows":
        return os.path.join(ROOT_DIR, "installer", "windows", "install.ps1")
    if system == "Linux":
        return os.path.join(ROOT_DIR, "installer", "linux", "install.sh")
    if system == "Darwin":
        return os.path.join(ROOT_DIR, "installer", "macos", "install.sh")
    raise RuntimeError(f"Unsupported operating system: {system}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="One-click local installer for Deep-Live-Cam.")
    parser.add_argument("--skip-shortcut", action="store_true", help="Skip desktop shortcut creation at the end.")
    parser.add_argument("--non-interactive", action="store_true", help="Run without the installer wizard UI.")
    args = parser.parse_args(argv)

    if not args.non_interactive:
        try:
            from installer.ui import launch_installer_ui

            plan = launch_installer_ui()
            if plan.mode == "cancel":
                print("[bootstrap] Installation cancelled.")
                return 0
            args.skip_shortcut = not plan.create_shortcut
        except ImportError:
            pass

    system = platform.system()
    _console(f"Detected operating system: {system}")

    script = _resolve_script()
    if not os.path.exists(script):
        raise FileNotFoundError(f"Installer script was not found: {script}")

    if system == "Windows":
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            raise RuntimeError("PowerShell is required to run the Windows installer.")
        command = [powershell, "-ExecutionPolicy", "Bypass", "-File", script]
        if args.skip_shortcut:
            command.append("-SkipShortcut")
        _run(command, cwd=ROOT_DIR)
        return 0

    bash = shutil.which("bash")
    if not bash:
        raise RuntimeError("bash is required to run the Unix installer.")
    command = [bash, script]
    if args.skip_shortcut:
        command.append("--skip-shortcut")
    _run(command, cwd=ROOT_DIR)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n[bootstrap] Installation cancelled by user.")
        raise SystemExit(130)
