import argparse
import os
from pathlib import Path, PurePosixPath
import stat
import zipfile


TARGETS = {
    "windows": ("Windows", "TextGame.exe", "Chapter8/Chapter8.exe"),
    "linux": ("Linux", "TextGame", "Chapter8/Chapter8"),
    "mac-intel": ("Mac-Intel", "TextGame", "Chapter8/Chapter8"),
    "mac-apple": ("Mac-Apple", "TextGame", "Chapter8/Chapter8"),
}

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

LINUX_LAUNCHER = """#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
game="$base/Linux/TextGame/TextGame"
if [ ! -f "$game" ]; then
    echo "Linux game not found: $game" >&2
    exit 1
fi
exec "$game"
"""

MAC_LAUNCHER = """#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
case "$(uname -m)" in
    arm64) platform=Mac-Apple ;;
    x86_64) platform=Mac-Intel ;;
    *) echo "Unsupported Mac architecture: $(uname -m)" >&2; exit 1 ;;
esac
game="$base/$platform/TextGame/TextGame"
if [ ! -f "$game" ]; then
    echo "Game for $platform not found: $game" >&2
    exit 1
fi
exec "$game"
"""


def validate_archive(archive, target):
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
    _, game, chapter8 = TARGETS[target]
    for required in (f"TextGame/{game}", f"TextGame/{chapter8}"):
        if required not in seen or seen[required].is_dir():
            raise ValueError(f"{target} archive is missing {required}")


def install(usb, builds):
    if not usb.is_dir():
        raise ValueError(f"USB destination must be an existing directory: {usb}")
    if not builds:
        raise ValueError("Select at least one platform build")
    destination = usb / "TextGameUSB"
    if destination.exists():
        raise FileExistsError(f"Destination already exists; saves will not be overwritten: {destination}")

    # Validate all inputs before creating anything on the destination.
    for target, path in builds.items():
        with zipfile.ZipFile(path) as archive:
            validate_archive(archive, target)

    destination.mkdir()
    for target, path in builds.items():
        folder = destination / TARGETS[target][0]
        folder.mkdir()
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                extracted = Path(archive.extract(info, folder))
                if not info.is_dir() and info.external_attr >> 16 & 0o111:
                    extracted.chmod(extracted.stat().st_mode | 0o111)

    launchers = []
    if "windows" in builds:
        launchers.append(("Play on Windows.bat", WINDOWS_LAUNCHER, False))
    if "linux" in builds:
        launchers.append(("Play on Linux.sh", LINUX_LAUNCHER, True))
    if "mac-intel" in builds or "mac-apple" in builds:
        launchers.append(("Play on Mac.command", MAC_LAUNCHER, True))
    for name, content, executable in launchers:
        path = destination / name
        if name.endswith(".bat"):
            path.write_bytes(content.replace("\n", "\r\n").encode("utf-8"))
        else:
            path.write_text(content, encoding="utf-8")
        if executable:
            path.chmod(path.stat().st_mode | 0o111)
    return destination


def main():
    parser = argparse.ArgumentParser(
        description="Install downloaded portable build ZIPs onto a USB drive."
    )
    parser.add_argument("usb", type=Path, help="Existing USB drive directory")
    for target in TARGETS:
        parser.add_argument(f"--{target}", type=Path, metavar="ZIP")
    args = parser.parse_args()
    builds = {target: getattr(args, target.replace("-", "_"))
              for target in TARGETS if getattr(args, target.replace("-", "_")) is not None}
    try:
        destination = install(args.usb, builds)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Installation failed: {exc}\n")
    print(f"Installed to {destination}")


if __name__ == "__main__":
    main()
