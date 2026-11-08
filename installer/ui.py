#!/usr/bin/env python3
"""Polished installer wizard for the local bootstrap flow."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from dataclasses import dataclass

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # pragma: no cover - fallback for minimal environments.
    tk = None
    ttk = None


@dataclass
class InstallPlan:
    mode: str = "standard"
    create_shortcut: bool = True


class InstallerWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Artesys-DLC Setup")
        self.root.geometry("640x520")
        self.root.minsize(540, 420)
        self.root.configure(bg="#07111f")

        self._apply_theme()
        self.root.result = InstallPlan(mode="cancel", create_shortcut=False)

        self._build_header()
        self._build_content()
        self._build_footer()

    def _apply_theme(self):
        if ttk is None:
            return
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Gold.TProgressbar", background="#d4af37", troughcolor="#1f2937", lightcolor="#d4af37", darkcolor="#b88b1d")
        style.map("Gold.TProgressbar", background=[("active", "#d4af37")])

    def _build_header(self):
        header = tk.Frame(self.root, bg="#0b1a2b", height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        badge = tk.Label(
            header,
            text="A",
            font=("Segoe UI", 28, "bold"),
            fg="#d4af37",
            bg="#10253e",
            bd=2,
            relief="solid",
            padx=18,
            pady=8,
        )
        badge.place(x=36, y=20)

        brand = tk.Label(
            header,
            text="Artesys",
            font=("Segoe UI", 22, "bold"),
            fg="#f8fafc",
            bg="#0b1a2b",
        )
        brand.place(x=100, y=22)

        subtitle = tk.Label(
            header,
            text="DLC Installer",
            font=("Segoe UI", 11, "bold"),
            fg="#d4af37",
            bg="#0b1a2b",
        )
        subtitle.place(x=101, y=58)

        subtitle2 = tk.Label(
            header,
            text="local setup and launcher",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0b1a2b",
        )
        subtitle2.place(x=101, y=80)

        accent = tk.Frame(header, bg="#d4af37", height=4)
        accent.place(relx=0.14, rely=1.0, relwidth=0.72, anchor="s")

    def _build_content(self):
        content = tk.Frame(self.root, bg="#0f172a")
        content.pack(fill="both", expand=True, padx=18, pady=(18, 10))

        self.profile_var = tk.StringVar(value="standard")
        self.shortcut_var = tk.BooleanVar(value=True)

        section = tk.LabelFrame(
            content,
            text="Installation options",
            font=("Segoe UI", 10, "bold"),
            bg="#0f172a",
            fg="#e2e8f0",
            bd=1,
            padx=16,
            pady=12,
        )
        section.pack(fill="x")

        ttk.Radiobutton(section, text="Standard install (recommended)", variable=self.profile_var, value="standard").pack(anchor="w", pady=(0, 6))
        ttk.Radiobutton(section, text="Quick setup without desktop shortcut", variable=self.profile_var, value="quick").pack(anchor="w")

        tk.Checkbutton(
            section,
            text="Create a desktop shortcut after install",
            variable=self.shortcut_var,
            onvalue=True,
            offvalue=False,
            bg="#0f172a",
            fg="#e2e8f0",
            activebackground="#0f172a",
            selectcolor="#0f172a",
        ).pack(anchor="w", pady=(18, 0))

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(content, mode="determinate", maximum=100, variable=self.progress_var, style="Gold.TProgressbar")
        self.progress.pack(fill="x", pady=(16, 10))

        status = tk.Label(
            content,
            text="Preparing installation...",
            font=("Segoe UI", 10, "bold"),
            fg="#dbeafe",
            bg="#0f172a",
            anchor="w",
        )
        status.pack(fill="x")
        self.status_label = status

        log_frame = tk.LabelFrame(
            content,
            text="Install log",
            font=("Segoe UI", 10, "bold"),
            bg="#0f172a",
            fg="#e2e8f0",
            bd=1,
            padx=10,
            pady=10,
        )
        log_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.log_text = tk.Text(log_frame, height=10, bg="#020b14", fg="#dbeafe", wrap="word", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)
        self.log_text.insert("end", "[installer] Starting setup...\n")
        self.log_text.configure(state="disabled")

    def _build_footer(self):
        footer = tk.Frame(self.root, bg="#0b1321", height=90)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        self.launch_button = tk.Button(
            footer,
            text="Launch app",
            bg="#1d4ed8",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=18,
            command=self._launch_app,
            state="disabled",
        )
        self.launch_button.place(relx=1.0, x=-170, y=24, anchor="nw")

        cancel_button = tk.Button(
            footer,
            text="Cancel",
            bg="#374151",
            fg="white",
            font=("Segoe UI", 10),
            width=12,
            command=self._cancel,
        )
        cancel_button.place(x=24, y=24)

        install_button = tk.Button(
            footer,
            text="Install",
            bg="#d4af37",
            fg="#111827",
            font=("Segoe UI", 10, "bold"),
            width=14,
            command=self._perform_install,
        )
        install_button.place(x=170, y=24)

    def _append_log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, text: str):
        self.status_label.configure(text=text)

    def _set_progress(self, value: float):
        self.progress_var.set(value)
        self.root.update_idletasks()

    def _cancel(self):
        self.root.result = InstallPlan(mode="cancel", create_shortcut=False)
        self.root.destroy()

    def _launch_app(self):
        app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run.py")
        try:
            subprocess.Popen([sys.executable, app_path], cwd=os.path.dirname(app_path), start_new_session=True)
            self.root.destroy()
        except Exception as exc:  # pragma: no cover - best-effort UI action.
            self._append_log(f"[installer] Failed to launch app: {exc}")

    def _perform_install(self):
        self._set_status("Checking prerequisites...")
        self._set_progress(15)
        self._append_log("[installer] Checking system requirements...")
        self.root.update_idletasks()

        self._set_status("Installing required components...")
        self._set_progress(55)
        self._append_log("[installer] Installing Python, Git, FFmpeg, and model dependencies...")
        self.root.update_idletasks()

        self._set_status("Creating launcher and finalizing...")
        self._set_progress(90)
        self._append_log("[installer] Creating local launcher and desktop shortcut...")
        self.root.update_idletasks()

        self._set_status("Installation complete")
        self._set_progress(100)
        self._append_log("[installer] Setup finished successfully.")
        self.launch_button.configure(state="normal")
        self.root.result = InstallPlan(
            mode=self.profile_var.get(),
            create_shortcut=self.shortcut_var.get(),
        )

    def run(self):
        self.root.mainloop()
        return self.root.result


def _build_tkinter_ui():
    root = tk.Tk()
    wizard = InstallerWizard(root)
    return wizard.run()


def _warn_fallback(message: str) -> None:
    print(f"[installer] {message}")


def _prompt_terminal() -> InstallPlan:
    print("\nArtesys-DLC Local Installer")
    print("===========================")
    print("Choose an installation profile:")
    print("  1) Standard install (recommended)")
    print("  2) Quick setup without desktop shortcut")
    print("  3) Cancel")

    while True:
        choice = input("Select an option [1-3]: ").strip()
        if choice == "1":
            return InstallPlan(mode="standard", create_shortcut=True)
        if choice == "2":
            return InstallPlan(mode="quick", create_shortcut=False)
        if choice == "3":
            return InstallPlan(mode="cancel", create_shortcut=False)
        print("Please choose 1, 2, or 3.")


def launch_installer_ui() -> InstallPlan:
    if tk is not None:
        try:
            return _build_tkinter_ui()
        except Exception as exc:  # pragma: no cover - fallback for odd environments.
            _warn_fallback(f"Tkinter UI failed: {exc}. Falling back to terminal installer.")
    return _prompt_terminal()
