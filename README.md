# EKKO

Scaffold new projects from a template folder.

EKKO copies your `EXAMPLE` folder structure into any location on your machine,
renaming it to the project name you provide.

## Requirements

- Python 3.6 or later
- tkinter (Python's built-in GUI library)

### macOS notes

tkinter ships with the **python.org installer** out of the box. If you installed
Python via Homebrew and tkinter is missing, run:

```bash
brew install python-tk
```

EKKO is compatible with macOS 10.9 (Mavericks) and all later versions,
including macOS 14 Sonoma and macOS 15 Sequoia.

### Linux notes

On Debian/Ubuntu: `sudo apt install python3-tk`
On Fedora/RHEL: `sudo dnf install python3-tkinter`

## Install

```bash
cd ekko/
pip install .
```

This registers the `ekko` command system-wide.

## Set up your template

Place whatever folders and files you want every new project to start with inside:

```
ekko/ekko/EXAMPLE/
```

A sample structure is included (src/, docs/, tests/, README.md). Replace or edit
it to match your needs.

## Usage

From any directory, run:

```bash
ekko
```

A window appears asking for:

1. **Project name** — the name of the new top-level folder.
2. **File location** — defaults to your current directory. Click "Browse..." to
   pick a different location using the native folder picker.

Click **Create Project**. EKKO copies the EXAMPLE structure into the chosen
location and confirms when done.

## Uninstall

```bash
pip uninstall ekko
```
