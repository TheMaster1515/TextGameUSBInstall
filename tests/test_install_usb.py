import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

import install_usb


class UsbInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.usb = self.root / "USB drive"
        self.usb.mkdir()

    def make_archive(self, target):
        path = self.root / f"{target}.zip"
        _, game, chapter8 = install_usb.TARGETS[target]
        with zipfile.ZipFile(path, "w") as archive:
            for name in (game, chapter8):
                info = zipfile.ZipInfo(f"TextGame/{name}")
                info.create_system = 3
                info.external_attr = (0o100755 << 16)
                archive.writestr(info, '#!/bin/sh\nprintf "launched:%s" "$0"\n')
            archive.writestr("TextGame/images/background.jpg", b"asset")
        return path

    def test_installs_all_platforms_and_preserves_existing_files(self):
        marker = self.usb / "keep.txt"
        marker.write_text("keep")
        builds = {target: self.make_archive(target) for target in install_usb.TARGETS}
        result = install_usb.install(self.usb, builds)
        for target, (folder, game, chapter8) in install_usb.TARGETS.items():
            self.assertTrue((result / folder / "TextGame" / game).is_file(), target)
            self.assertTrue((result / folder / "TextGame" / chapter8).is_file(), target)
        for launcher in ("Play on Windows.bat", "Play on Linux.sh", "Play on Mac.command"):
            self.assertTrue((result / launcher).is_file())
        self.assertEqual(marker.read_text(), "keep")
        self.assertIn(b"\r\n", (result / "Play on Windows.bat").read_bytes())

    @unittest.skipIf(os.name == "nt", "Unix launchers require a Unix shell")
    def test_linux_launcher_runs_from_another_working_directory(self):
        result = install_usb.install(self.usb, {"linux": self.make_archive("linux")})
        game = result / "Linux" / "TextGame" / "TextGame"
        self.assertTrue(os.access(game, os.X_OK))
        output = subprocess.check_output([result / "Play on Linux.sh"], cwd=self.root, text=True)
        self.assertEqual(output, f"launched:{game}")

    @unittest.skipIf(os.name == "nt", "Unix launchers require a Unix shell")
    def test_mac_launcher_selects_architecture(self):
        result = install_usb.install(self.usb, {
            "mac-intel": self.make_archive("mac-intel"),
            "mac-apple": self.make_archive("mac-apple"),
        })
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        uname = bin_dir / "uname"
        for arch, platform in (("x86_64", "Mac-Intel"), ("arm64", "Mac-Apple")):
            uname.write_text(f"#!/bin/sh\nprintf '{arch}\\n'\n")
            uname.chmod(0o755)
            env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
            output = subprocess.check_output([result / "Play on Mac.command"], env=env, text=True)
            self.assertEqual(output, f"launched:{result / platform / 'TextGame' / 'TextGame'}")

    def test_refuses_to_overwrite_an_installation(self):
        existing = self.usb / "TextGameUSB"
        existing.mkdir()
        save = existing / "save.txt"
        save.write_text("saved")
        with self.assertRaises(FileExistsError):
            install_usb.install(self.usb, {"windows": self.make_archive("windows")})
        self.assertEqual(save.read_text(), "saved")

    def test_invalid_archive_is_rejected_before_installation(self):
        valid = self.make_archive("linux")
        invalid = self.root / "bad.zip"
        with zipfile.ZipFile(invalid, "w") as archive:
            archive.writestr("TextGame/../../outside", "bad")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            install_usb.install(self.usb, {"linux": valid, "windows": invalid})
        self.assertFalse((self.usb / "TextGameUSB").exists())
        self.assertFalse((self.root / "outside").exists())

    def test_missing_executable_and_empty_selection_are_rejected(self):
        invalid = self.root / "bad.zip"
        with zipfile.ZipFile(invalid, "w") as archive:
            archive.writestr("TextGame/TextGame.exe", "game")
        with self.assertRaisesRegex(ValueError, "Chapter8"):
            install_usb.install(self.usb, {"windows": invalid})
        with self.assertRaisesRegex(ValueError, "at least one"):
            install_usb.install(self.usb, {})
        self.assertFalse((self.usb / "TextGameUSB").exists())


if __name__ == "__main__":
    unittest.main()
