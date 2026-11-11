# Windows USB installer

The game runs from a USB drive on 64-bit Windows. Windows does not reliably
allow USB drives to start programs or show a custom launch window automatically,
so open the drive and launch the game yourself. Neither the installer nor the
game requires Python on the Windows computer.

## Get the installer

1. Push this repository, including `.github/workflows/portable-build.yml`, to
   GitHub.
2. On GitHub, open **Actions > Windows USB installer > Run workflow**.
3. When the workflow finishes, download the **Windows-USB-installer** artifact
   and extract it to obtain `InstallTextGameToUSB.exe`.

The USB drive must be writable and have room for the game and saves. An existing
FAT32, exFAT, or NTFS drive can be used; formatting is not required.

## Install and play

1. On a Windows computer, plug in the USB drive.
2. Double-click `InstallTextGameToUSB.exe` and select the USB drive in the
   folder picker.
3. Open the drive's `TextGameUSB` folder and double-click
   `Play on Windows.bat`.

The installer does not overwrite an existing `TextGameUSB` folder or touch
other files on the drive. To reinstall or update, back up any saves you want
to keep, then remove or rename the old `TextGameUSB` folder and run the new
installer. If installation fails partway through, inspect the folder before
removing it and retrying.

Windows may warn that the installer or game is unsigned. Only run builds you
trust. Character data and chapter progress are stored in
`TextGameUSB/Windows/TextGame/files`; Chapter 8 scores are stored in
`TextGameUSB/Windows/TextGame/Chapter8/files`. Close the game and safely eject
the drive when finished.

## Build locally

Build on 64-bit Windows with Python 3.11:

```bat
py -3.11 -m pip install -r requirements-build.txt
py -3.11 build_portable.py portable-output
cd portable-output\dist
py -3.11 -m zipfile -c ..\..\TextGame-windows-x86_64.zip TextGame
cd ..\..
py -3.11 -m PyInstaller --noconfirm --clean --onefile --windowed --name InstallTextGameToUSB --distpath portable-output/installer --workpath portable-output/installer-build --specpath portable-output/specs --add-data "TextGame-windows-x86_64.zip;." install_usb.py
```

The `portable-output` directory must not already exist. The finished installer
is `portable-output/installer/InstallTextGameToUSB.exe`. See the workflow for
the automated build and installer check.
