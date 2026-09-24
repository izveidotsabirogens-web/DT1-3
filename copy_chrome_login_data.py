#!/usr/bin/env python3
"""
Chrome Login Data Copier
------------------------
Finds the Google Chrome 'Login Data' SQLite file and copies it to the Desktop.

Supports: Windows, macOS, Linux.
License: MIT
"""

import os
import sys
import shutil
import platform
from pathlib import Path

# ----------------------------
# Configuration
# ----------------------------
CHROME_PROFILE = "Default"          # Change to "Profile 1", "Profile 2", etc. if needed
OUTPUT_FILENAME = "Chrome_LoginData.db"

# ----------------------------
# Helper functions
# ----------------------------

def get_desktop_path() -> Path:
    """Return the Desktop path for the current user."""
    if platform.system() == "Windows":
        return Path(os.environ["USERPROFILE"]) / "Desktop"
    return Path.home() / "Desktop"


def get_chrome_login_data_path() -> Path:
    """
    Build the default path to Chrome's Login Data file
    based on the operating system.
    """
    system = platform.system()

    if system == "Windows":
        base = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    elif system == "Linux":
        base = Path.home() / ".config" / "google-chrome"
    else:
        raise OSError(f"Unsupported operating system: {system}")

    return base / CHROME_PROFILE / "Login Data"


def copy_locked_file(src: Path, dst: Path) -> bool:
    """
    Try to copy a file that may be locked by Chrome.
    Returns True on success, False otherwise.
    """
    # First attempt: normal copy
    try:
        shutil.copy2(src, dst)
        return True
    except (PermissionError, OSError):
        pass

    # Second attempt: read raw bytes and write manually
    try:
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        return True
    except Exception as e:
        print(f"[!] Could not copy file: {e}")
        return False


# ----------------------------
# Main logic
# ----------------------------

def main():
    print("Chrome Login Data Copier")
    print("=" * 40)

    # 1. Locate the Login Data file
    try:
        login_data_path = get_chrome_login_data_path()
    except OSError as e:
        print(f"[✗] {e}")
        sys.exit(1)

    print(f"[*] Looking for: {login_data_path}")

    if not login_data_path.exists():
        print("[✗] Login Data file not found. Is Chrome installed?")
        print("    If you use a non-default profile, edit CHROME_PROFILE in the script.")
        sys.exit(1)

    # 2. Prepare the destination on the Desktop
    desktop = get_desktop_path()
    if not desktop.exists():
        print(f"[✗] Desktop folder not found: {desktop}")
        sys.exit(1)

    destination = desktop / OUTPUT_FILENAME
    print(f"[*] Copying to: {destination}")

    # 3. Copy the file (handling potential locks)
    if copy_locked_file(login_data_path, destination):
        print(f"[✓] Success! File copied to: {destination}")
        print("    You can now open it with any SQLite viewer.")
    else:
        print("[✗] Failed to copy the file. Try closing Chrome completely and run again.")


if __name__ == "__main__":
    main()
