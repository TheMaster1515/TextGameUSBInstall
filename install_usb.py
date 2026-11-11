import argparse
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile


BUILD_ARCHIVE = "TextGame-windows-x86_64.zip"

WINDOWS_LAUNCHER = r"""@echo off
set "GAME=%~dp0Windows\TextGame\TextGame.exe"
if not exist "%GAME%" (
    echo Windows game not found: "%GAME%"
    pause
    exit /b 1
)
"%GAME%"
if errorlevel 1 (
    echo The game exited with an error.
    pause
    exit /b 1
)
"""

def validate_archive(archive):
    seen = {}
    for info in archive.infolist():
        name = info.filename
        path = PurePosixPath(name)
        if (not name or "\\" in name or ":" in name or path.is_absolute()
                or ".." in path.parts or not path.parts or path.parts[0] != "TextGame"):
            raise ValueError(f"Unsafe or unexpected archive path: {name!r}")
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError(f"Archive contains a symbolic link: {name!r}")
        normalized = str(path)
        if normalized in seen:
            raise ValueError(f"Duplicate archive path: {name!r}")
        seen[normalized] = info
    for required in ("TextGame/TextGame.exe", "TextGame/Chapter8/Chapter8.exe"):
        if required not in seen or seen[required].is_dir():
            raise ValueError(f"Windows archive is missing {required}")


def install(usb, build):
    if not usb.is_dir():
        raise ValueError(f"USB destination must be an existing directory: {usb}")
    destination = usb / "TextGameUSB"
    if destination.exists():
        raise FileExistsError(f"Destination already exists; saves will not be overwritten: {destination}")

    with zipfile.ZipFile(build) as archive:
        validate_archive(archive)
        destination.mkdir()
        folder = destination / "Windows"
        folder.mkdir()
        archive.extractall(folder)

    (destination / "Play on Windows.bat").write_bytes(
        WINDOWS_LAUNCHER.replace("\n", "\r\n").encode("utf-8")
    )
    return destination


def bundled_archive():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / BUILD_ARCHIVE


def install_with_window():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.withdraw()
    try:
        usb = filedialog.askdirectory(
            parent=root, title="Select your USB drive", mustexist=True
        )
        if not usb:
            return
        try:
            destination = install(Path(usb), bundled_archive())
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            messagebox.showerror("Installation failed", str(exc), parent=root)
        else:
            messagebox.showinfo(
                "Installation complete",
                f"Installed to {destination}\n\n"
                "Open that folder and double-click Play on Windows.bat to play.",
                parent=root,
            )
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(
        description="Install the Windows game onto a USB drive."
    )
    parser.add_argument("usb", type=Path, nargs="?", help="Existing USB drive directory")
    parser.add_argument("--windows", type=Path, metavar="ZIP", help="Windows build ZIP")
    args = parser.parse_args()
    if args.usb is None:
        if args.windows is not None:
            parser.error("--windows requires a USB destination")
        install_with_window()
        return
    try:
        destination = install(args.usb, args.windows or bundled_archive())
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Installation failed: {exc}\n")
    print(f"Installed to {destination}")


if __name__ == "__main__":
    main()
