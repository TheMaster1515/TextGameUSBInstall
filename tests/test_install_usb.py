from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

import install_usb


class UsbInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.usb = self.root / "USB drive"
        self.usb.mkdir()

    def make_archive(self):
        path = self.root / "windows.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("TextGame/TextGame.exe", b"game")
            archive.writestr("TextGame/Chapter8/Chapter8.exe", b"chapter8")
            archive.writestr("TextGame/images/background.jpg", b"asset")
        return path

    def test_installs_windows_game_and_preserves_existing_files(self):
        marker = self.usb / "keep.txt"
        marker.write_text("keep")
        result = install_usb.install(self.usb, self.make_archive())
        self.assertTrue((result / "Windows/TextGame/TextGame.exe").is_file())
        self.assertTrue((result / "Windows/TextGame/Chapter8/Chapter8.exe").is_file())
        launcher = (result / "Play on Windows.bat").read_bytes()
        self.assertIn(b'%~dp0Windows\\TextGame\\TextGame.exe', launcher)
        self.assertIn(b"\r\n", launcher)
        self.assertEqual(marker.read_text(), "keep")

    def test_refuses_to_overwrite_an_installation(self):
        existing = self.usb / "TextGameUSB"
        existing.mkdir()
        save = existing / "save.txt"
        save.write_text("saved")
        with self.assertRaises(FileExistsError):
            install_usb.install(self.usb, self.make_archive())
        self.assertEqual(save.read_text(), "saved")

    def test_invalid_archive_is_rejected_before_installation(self):
        invalid = self.root / "bad.zip"
        with zipfile.ZipFile(invalid, "w") as archive:
            archive.writestr("TextGame/../../outside", "bad")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            install_usb.install(self.usb, invalid)
        self.assertFalse((self.usb / "TextGameUSB").exists())
        self.assertFalse((self.root / "outside").exists())

    def test_missing_executable_is_rejected(self):
        invalid = self.root / "bad.zip"
        with zipfile.ZipFile(invalid, "w") as archive:
            archive.writestr("TextGame/TextGame.exe", "game")
        with self.assertRaisesRegex(ValueError, "Chapter8"):
            install_usb.install(self.usb, invalid)
        self.assertFalse((self.usb / "TextGameUSB").exists())

    def test_command_line_installs_selected_windows_archive(self):
        subprocess.run(
            [sys.executable, str(Path(install_usb.__file__)), str(self.usb),
             "--windows", str(self.make_archive())],
            check=True, capture_output=True, text=True,
        )
        self.assertTrue((self.usb / "TextGameUSB/Play on Windows.bat").is_file())

    def test_bundled_archive_uses_pyinstaller_directory(self):
        with patch.object(sys, "_MEIPASS", str(self.root), create=True):
            self.assertEqual(install_usb.bundled_archive(), self.root / install_usb.BUILD_ARCHIVE)

    def test_window_installs_bundled_archive_and_reports_success(self):
        archive = self.make_archive()
        tkinter = MagicMock()
        tkinter.filedialog.askdirectory.return_value = str(self.usb)
        with patch.dict(sys.modules, {"tkinter": tkinter}), \
             patch.object(install_usb, "bundled_archive", return_value=archive):
            install_usb.install_with_window()
        self.assertTrue((self.usb / "TextGameUSB/Play on Windows.bat").is_file())
        tkinter.messagebox.showinfo.assert_called_once()
        tkinter.Tk.return_value.destroy.assert_called_once()

    def test_window_reports_installation_errors(self):
        tkinter = MagicMock()
        tkinter.filedialog.askdirectory.return_value = str(self.usb)
        with patch.dict(sys.modules, {"tkinter": tkinter}), \
             patch.object(install_usb, "bundled_archive", return_value=self.root / "missing.zip"):
            install_usb.install_with_window()
        tkinter.messagebox.showerror.assert_called_once()
        tkinter.Tk.return_value.destroy.assert_called_once()
        self.assertFalse((self.usb / "TextGameUSB").exists())


if __name__ == "__main__":
    unittest.main()
