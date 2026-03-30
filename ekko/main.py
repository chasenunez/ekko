#!/usr/bin/env python3
"""
EKKO — scaffold new projects from a template folder.

Copies the EXAMPLE folder (bundled inside EKKO's install directory) into
a destination you choose, renaming the top-level folder to your project name.

Usage:
    ekko          (launches the GUI prompt)
    ekko --help   (shows this help text)
"""

import os
import platform
import shutil
import subprocess
import sys


# ---------------------------------------------------------------------------
# macOS compatibility helpers
# ---------------------------------------------------------------------------

def _check_tkinter():
    """
    Return True if tkinter is importable.  On macOS the system Python and
    some Homebrew builds ship without tkinter, so we detect that early and
    give the user a clear message instead of a raw ImportError.
    """
    try:
        import tkinter  # noqa: F401
        return True
    except ImportError:
        return False


def _macos_fix_event_loop():
    """
    On macOS 12+ with Python installed via Homebrew, the Tk event loop
    can stall unless we nudge the NSApplication instance first.
    This is a no-op on non-macOS systems.
    """
    if platform.system() != "Darwin":
        return
    try:
        # PyObjC is pre-installed on macOS system Python.
        # If it is missing (e.g. Homebrew Python), this is a harmless no-op.
        from Foundation import NSBundle  # type: ignore
        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info and "CFBundleName" not in info:
                info["CFBundleName"] = "EKKO"
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core logic (no GUI dependency)
# ---------------------------------------------------------------------------

def get_example_dir():
    """Return the absolute path to the EXAMPLE folder bundled with EKKO."""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(package_dir, "EXAMPLE")


def copy_template(project_name, destination_dir, example_dir):
    """
    Copy the EXAMPLE tree into *destination_dir*, renaming the top-level
    folder to *project_name*.

    Returns the full path of the newly created project folder.
    Raises FileExistsError if the target already exists.
    Raises FileNotFoundError if the EXAMPLE folder is missing.
    """
    if not os.path.isdir(example_dir):
        raise FileNotFoundError(
            f"EXAMPLE folder not found at:\n{example_dir}\n"
            "Place your template file structure there and try again."
        )

    target = os.path.join(destination_dir, project_name)

    if os.path.exists(target):
        raise FileExistsError(
            f"A folder named '{project_name}' already exists at:\n{target}"
        )

    # copy2 preserves metadata; dirs_exist_ok was added in 3.8 but we
    # don't need it here because we already checked the target is absent.
    shutil.copytree(example_dir, target, copy_function=shutil.copy2)
    return target


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def run_gui():
    """Launch the EKKO window, collect inputs, and create the project."""

    # ---- Pre-flight checks ------------------------------------------------
    if not _check_tkinter():
        _print_tkinter_help()
        sys.exit(1)

    _macos_fix_event_loop()

    import tkinter as tk
    from tkinter import filedialog, messagebox

    example_dir = get_example_dir()
    if not os.path.isdir(example_dir):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "EKKO — Error",
            f"Could not find the EXAMPLE folder.\n\n"
            f"Expected location:\n{example_dir}\n\n"
            "Place your template file structure inside that folder and try again.",
        )
        sys.exit(1)

    # ---- Build window -----------------------------------------------------
    root = tk.Tk()
    root.title("EKKO")
    root.resizable(False, False)

    # On macOS, bring the window to the front.
    if platform.system() == "Darwin":
        root.attributes("-topmost", True)
        root.after(200, lambda: root.attributes("-topmost", False))

    # Centre on screen.
    win_w, win_h = 480, 260
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - win_w) // 2
    y = (screen_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    # Current working directory is the default destination.
    cwd = os.getcwd()
    chosen_dir = tk.StringVar(value=cwd)

    # ---- Project name -----------------------------------------------------
    tk.Label(root, text="Project name:", anchor="w").pack(
        fill="x", padx=20, pady=(20, 2),
    )
    name_entry = tk.Entry(root, width=50)
    name_entry.pack(padx=20)
    name_entry.focus_set()

    # ---- Destination folder -----------------------------------------------
    tk.Label(root, text="File location:", anchor="w").pack(
        fill="x", padx=20, pady=(16, 2),
    )

    loc_frame = tk.Frame(root)
    loc_frame.pack(fill="x", padx=20)

    loc_label = tk.Label(
        loc_frame, textvariable=chosen_dir, anchor="w", relief="sunken", padx=4,
    )
    loc_label.pack(side="left", fill="x", expand=True)

    def browse():
        """Open the native directory picker and update chosen_dir."""
        selected = filedialog.askdirectory(
            initialdir=chosen_dir.get(),
            title="EKKO — Choose destination folder",
        )
        if selected:
            chosen_dir.set(selected)

    tk.Button(loc_frame, text="Browse\u2026", command=browse).pack(
        side="right", padx=(8, 0),
    )

    # ---- Status label (shows validation / error messages) -----------------
    status_var = tk.StringVar(value="")
    tk.Label(root, textvariable=status_var, fg="red", wraplength=440).pack(
        padx=20, pady=(8, 0),
    )

    # ---- Create button ----------------------------------------------------
    def on_create():
        """Validate inputs, copy the template, report the result."""
        project_name = name_entry.get().strip()
        dest = chosen_dir.get().strip()

        if not project_name:
            status_var.set("Please enter a project name.")
            return
        if not os.path.isdir(dest):
            status_var.set("The selected location does not exist.")
            return

        try:
            created_path = copy_template(project_name, dest, example_dir)
        except (FileExistsError, FileNotFoundError, OSError) as exc:
            status_var.set(str(exc))
            return

        messagebox.showinfo(
            "EKKO — Done",
            f"Project '{project_name}' created successfully at:\n\n{created_path}",
        )
        root.destroy()

    tk.Button(
        root, text="Create Project", command=on_create, padx=16, pady=4,
    ).pack(pady=(16, 20))

    # Enter key also triggers creation.
    root.bind("<Return>", lambda _: on_create())

    root.mainloop()


# ---------------------------------------------------------------------------
# Fallback help when tkinter is missing
# ---------------------------------------------------------------------------

def _print_tkinter_help():
    """Print install instructions for tkinter, tailored to the current OS."""
    print("EKKO requires tkinter (Python's built-in GUI library).")
    print()
    if platform.system() == "Darwin":
        print("On macOS you can fix this by:")
        print()
        print("  Option A — Install Python from python.org (includes tkinter):")
        print("    https://www.python.org/downloads/macos/")
        print()
        print("  Option B — If you use Homebrew:")
        print("    brew install python-tk")
        print()
    else:
        print("On Debian / Ubuntu:")
        print("    sudo apt install python3-tk")
        print()
        print("On Fedora / RHEL:")
        print("    sudo dnf install python3-tkinter")
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point registered as the 'ekko' console script."""
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.strip())
        sys.exit(0)
    run_gui()


if __name__ == "__main__":
    main()
