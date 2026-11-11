# Portable USB builds

The game can be installed on a single USB drive for Windows, Linux, and macOS.
It does not automatically start or display a prompt when the drive is plugged
in: modern operating systems restrict USB autorun. Open the drive and launch
the game yourself instead. No Python installation is needed on computers used
to play.

## Get the builds

1. Push this repository, including `.github/workflows/portable-build.yml`, to
   GitHub.
2. On GitHub, open **Actions > Portable builds > Run workflow**.
3. When all four jobs finish, download each build artifact. Extract the GitHub
   artifact downloads if necessary to obtain the inner `TextGame-*.zip`
   files. Do not extract those inner ZIP files.
4. Download or copy this repository to the computer you will use for
   installation. That computer needs Python 3.11 or newer; the installer uses
   only the Python standard library.

Use an exFAT-formatted USB drive if it must work on Windows, macOS, and Linux.
Formatting erases the drive; back up its contents first. The drive must be
writable and have enough space for the extracted builds and saves.

## Install onto the USB

From the repository directory, run the installer with the USB mount point and
the paths to the downloaded inner ZIP files. For example, on Linux or macOS:

```sh
python3 install_usb.py "/path/to/USB" \
  --windows "/path/to/TextGame-windows-x86_64.zip" \
  --linux "/path/to/TextGame-linux-x86_64.zip" \
  --mac-intel "/path/to/TextGame-macos-intel.zip" \
  --mac-apple "/path/to/TextGame-macos-apple-silicon.zip"
```

On Windows, use the USB drive letter and your actual ZIP paths, for example:

```bat
py -3 install_usb.py "E:/" --windows "C:\Downloads\TextGame-windows-x86_64.zip" --linux "C:\Downloads\TextGame-linux-x86_64.zip" --mac-intel "C:\Downloads\TextGame-macos-intel.zip" --mac-apple "C:\Downloads\TextGame-macos-apple-silicon.zip"
```

Each build option is optional, but include both Mac options to support both
Intel and Apple silicon Macs. The Linux and Windows builds target x86-64.
The installer creates a `TextGameUSB` folder without touching other files on
the drive, and refuses to overwrite an existing `TextGameUSB` folder. This
protects existing saves. If an installation fails partway through, inspect the
folder and back up any saves before removing it and retrying.

If installing from Windows, Unix executable permissions may not be retained.
After connecting the drive to Linux or macOS, use the commands below if needed.
Some exFAT mounts do not allow individual executable permissions to be changed.

## Play

Open the USB drive, then its `TextGameUSB` folder:

* **Windows:** double-click `Play on Windows.bat`.
* **Linux:** run `Play on Linux.sh`. Some desktop environments require
  right-clicking and choosing to run it, or running it in a terminal:
  `./Play\ on\ Linux.sh`.
* **macOS:** double-click `Play on Mac.command`. It selects the Intel or Apple
  silicon build for the current Mac.

On Linux, if executable permissions need fixing, open a terminal in
`TextGameUSB` and run:

```sh
chmod +x "Play on Linux.sh" Linux/TextGame/TextGame Linux/TextGame/Chapter8/Chapter8
```

On macOS, use the appropriate command for the installed build(s):

```sh
chmod +x "Play on Mac.command"
chmod +x Mac-Intel/TextGame/TextGame Mac-Intel/TextGame/Chapter8/Chapter8
chmod +x Mac-Apple/TextGame/TextGame Mac-Apple/TextGame/Chapter8/Chapter8
```

Skip the line for any Mac build you did not install. Linux desktop environments
differ in whether double-clicking executables on a USB drive is allowed. Some
drives are mounted `noexec`; in that case, copy the folder to the computer or
remount the drive with execution enabled. macOS or Windows may warn that these
unsigned builds are from an unknown developer. Only open builds you trust;
macOS may require approval in System Settings > Privacy & Security.

Character data and chapter progress are stored in the `files` folder inside
each platform's `TextGame` folder. Chapter 8 scores are stored inside
`Chapter8/files`. Each platform's copy has its own saves. Safely eject the
drive after closing the game.

## Build locally

Build on the operating system and architecture you intend to run on. Python
3.11 is used in the workflow:

```sh
python -m pip install -r requirements-build.txt
python build_portable.py portable-output
```

The output directory must not already exist. Copy the complete
`portable-output/dist/TextGame` folder to the USB drive and run `TextGame.exe`
on Windows or `TextGame` on Linux or macOS. To use the USB installer instead,
create a ZIP containing the `TextGame` folder (as the workflow does), then
pass it using the matching platform option. Each build bundles Python and its
Python dependencies. Linux still requires compatible system libraries and a
graphical desktop.
