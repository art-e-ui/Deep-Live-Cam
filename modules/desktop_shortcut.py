import argparse
import os
import re
import sys
from typing import Optional


DEFAULT_APP_NAME = "Artesys-DLC"
DEFAULT_DESCRIPTION = "Launch Deep-Live-Cam"


def _slugify(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return text.strip("-_.") or "deep-live-cam"


def _default_target_script() -> str:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(root_dir, "run.py")


def _desktop_entry_content(
    app_name: str,
    target_script: str,
    working_directory: str,
    icon_path: Optional[str],
    description: str,
) -> str:
    python_executable = os.path.abspath(sys.executable)
    target = os.path.abspath(target_script)
    working_dir = os.path.abspath(working_directory or os.path.dirname(target))
    icon = os.path.abspath(icon_path) if icon_path else ""

    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={app_name}",
        f"Comment={description}",
        "Categories=AudioVideo;Video;Graphics;",
        "Terminal=false",
        "StartupNotify=true",
        f"Path={working_dir}",
        f"Exec=\"{python_executable}\" \"{target}\"",
    ]
    if icon:
        lines.append(f"Icon={icon}")
    lines.append("MimeType=")
    return "\n".join(lines) + "\n"


def generate_desktop_shortcut(
    app_name: str = DEFAULT_APP_NAME,
    target_script: Optional[str] = None,
    working_directory: Optional[str] = None,
    icon_path: Optional[str] = None,
    install_dir: Optional[str] = None,
    description: str = DEFAULT_DESCRIPTION,
) -> str:
    target_script = target_script or _default_target_script()
    if not os.path.exists(target_script):
        raise FileNotFoundError(f"Target launcher script does not exist: {target_script}")

    if sys.platform.startswith("linux"):
        install_path = install_dir or os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
        os.makedirs(install_path, exist_ok=True)
        shortcut_path = os.path.join(install_path, f"{_slugify(app_name)}.desktop")
        with open(shortcut_path, "w", encoding="utf-8") as handle:
            handle.write(
                _desktop_entry_content(
                    app_name=app_name,
                    target_script=target_script,
                    working_directory=working_directory or os.getcwd(),
                    icon_path=icon_path,
                    description=description,
                )
            )
        os.chmod(shortcut_path, 0o755)

        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.isdir(desktop_dir):
            desktop_shortcut = os.path.join(desktop_dir, f"{_slugify(app_name)}.desktop")
            try:
                with open(desktop_shortcut, "w", encoding="utf-8") as handle:
                    handle.write(
                        _desktop_entry_content(
                            app_name=app_name,
                            target_script=target_script,
                            working_directory=working_directory or os.getcwd(),
                            icon_path=icon_path,
                            description=description,
                        )
                    )
                os.chmod(desktop_shortcut, 0o755)
            except OSError:
                pass
        return shortcut_path

    if sys.platform == "win32":
        install_path = install_dir or os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(install_path, exist_ok=True)
        shortcut_path = os.path.join(install_path, f"{_slugify(app_name)}.cmd")
        working_dir = working_directory or os.path.dirname(os.path.abspath(target_script))
        with open(shortcut_path, "w", encoding="utf-8", newline="") as handle:
            handle.write(
                '@echo off\r\n'
                f'cd /d "{working_dir}"\r\n'
                f'"{os.path.abspath(sys.executable)}" "{os.path.abspath(target_script)}"\r\n'
            )
        return shortcut_path

    # macOS fallback: a simple shell launcher in the desktop folder.
    install_path = install_dir or os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(install_path, exist_ok=True)
    shortcut_path = os.path.join(install_path, f"{_slugify(app_name)}.command")
    working_dir = working_directory or os.path.dirname(os.path.abspath(target_script))
    with open(shortcut_path, "w", encoding="utf-8") as handle:
        handle.write(
            "#!/bin/bash\n"
            f'cd "{working_dir}"\n'
            f'"{os.path.abspath(sys.executable)}" "{os.path.abspath(target_script)}"\n'
        )
    os.chmod(shortcut_path, 0o755)
    return shortcut_path


def _main() -> None:
    parser = argparse.ArgumentParser(description="Generate a desktop launcher for Deep-Live-Cam.")
    parser.add_argument("--name", default=DEFAULT_APP_NAME, help="Display name for the shortcut.")
    parser.add_argument("--target", default=None, help="Absolute or relative path to the app launcher script.")
    parser.add_argument("--working-directory", default=None, help="Working directory for the launch command.")
    parser.add_argument("--icon", default=None, help="Absolute path to an icon image.")
    parser.add_argument("--install-dir", default=None, help="Installation directory for the shortcut file.")
    args = parser.parse_args()

    shortcut = generate_desktop_shortcut(
        app_name=args.name,
        target_script=args.target,
        working_directory=args.working_directory,
        icon_path=args.icon,
        install_dir=args.install_dir,
    )
    print(shortcut)


if __name__ == "__main__":
    _main()
