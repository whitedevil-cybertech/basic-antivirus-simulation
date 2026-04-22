#!/usr/bin/env python3
"""Setup GUI directory structure."""

from pathlib import Path

# Create gui package structure
base = Path(".")
gui_dir = base / "gui"
widgets_dir = gui_dir / "widgets"
dialogs_dir = gui_dir / "dialogs"
utils_dir = gui_dir / "utils"
resources_dir = gui_dir / "resources"
icons_dir = resources_dir / "icons"

# Create all directories
for d in [gui_dir, widgets_dir, dialogs_dir, utils_dir, resources_dir, icons_dir]:
    d.mkdir(exist_ok=True, parents=True)
    init_file = d / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Package module."""\n')

print("[SUCCESS] GUI directory structure created!")
print(f"Directory: {gui_dir}")
print(f"   - widgets/")
print(f"   - dialogs/")
print(f"   - utils/")
print(f"   - resources/")
print(f"   - icons/")
print(f"   - __init__.py")
