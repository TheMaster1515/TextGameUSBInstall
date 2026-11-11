import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def build(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    dist = output / "dist"
    work = output / "build"
    specs = output / "specs"
    specs.mkdir()

    def run(name, script, assets):
        command = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--onedir", "--contents-directory", ".",
            "--name", name,
            "--distpath", str(dist),
            "--workpath", str(work / name),
            "--specpath", str(specs),
            "--paths", str(ROOT / "code"),
        ]
        for source, destination in assets:
            command.extend(["--add-data", f"{ROOT / source}{os.pathsep}{destination}"])
        command.append(str(ROOT / script))
        subprocess.run(command, cwd=ROOT, check=True)

    run("TextGame", "code/game_window.py", [("images", "images")])
    run("Chapter8", "chapter8game/EasterEgg.py", [
        ("chapter8game/images", "images"),
        ("chapter8game/sounds", "sounds"),
        ("chapter8game/icon", "icon"),
        ("chapter8game/font", "font"),
    ])
    shutil.move(str(dist / "Chapter8"), str(dist / "TextGame" / "Chapter8"))
    (dist / "TextGame" / "files").mkdir()
    (dist / "TextGame" / "Chapter8" / "files").mkdir()
    print(f"Portable game created at {dist / 'TextGame'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a portable game for the current OS and architecture.")
    parser.add_argument("output", type=Path, help="New directory for build output; must not already exist")
    args = parser.parse_args()
    build(args.output)
