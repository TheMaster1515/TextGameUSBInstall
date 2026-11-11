# Portable USB builds

Modern computers generally block automatic execution when a USB drive is
connected. To play, open the drive and launch the game manually.

## Get the builds

1. Push this repository, including `.github/workflows/portable-build.yml`, to
   GitHub.
2. On GitHub, open **Actions > Portable builds > Run workflow**.
3. When all four jobs finish, download each build artifact.
4. Extract each inner `TextGame-*.zip` into a different folder on the USB drive,
   for example `Windows`, `Linux`, `Mac-Intel`, and `Mac-Apple`. Keep each
   extracted `TextGame` folder and its contents together.

Use an exFAT-formatted USB drive if it must work on Windows, macOS, and Linux.
Formatting erases the drive; back up its contents first.

## Play

Open the folder for the computer you're using, then open the `TextGame` folder.
Run `TextGame.exe` on Windows, or `TextGame` on Linux or macOS. On Unix systems,
the executable may need permission after extraction:

```sh
chmod +x TextGame Chapter8/Chapter8
./TextGame
```

Linux desktop environments differ in whether double-clicking executables on a
USB drive is allowed. Some USB drives are mounted `noexec`; in that case, copy
the folder to the computer or remount the drive with execution enabled.
macOS or Windows may warn that these unsigned builds are from an unknown
developer. Only open builds you trust; macOS may require approval in System
Settings > Privacy & Security.

Character data and chapter progress are stored in the `files` folder inside
that platform's `TextGame` folder. Chapter 8 scores are stored inside
`Chapter8/files`. Each platform's copy has its own saves. The USB must be
writable; safely eject it after closing the game.

## Build locally

Build on the operating system and architecture you intend to run on. Python
3.11 is used in the workflow:

```sh
python -m pip install -r requirements-build.txt
python build_portable.py portable-output
```

The output directory must not already exist. Copy the complete
`portable-output/dist/TextGame` folder to the USB drive. Each build bundles
Python and its Python dependencies; target computers do not need to install
Python. Linux still requires compatible system libraries and a graphical
desktop.
