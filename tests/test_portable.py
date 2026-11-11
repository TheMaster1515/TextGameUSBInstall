import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT))

import build_portable
import chapter8


class PortableBuildTests(unittest.TestCase):
    def test_build_refuses_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as output:
            marker = Path(output) / "keep.txt"
            marker.write_text("keep")
            with self.assertRaises(FileExistsError):
                build_portable.build(Path(output))
            self.assertEqual(marker.read_text(), "keep")

    def test_source_minigame_uses_current_interpreter(self):
        with patch.object(sys, "frozen", False, create=True), \
             patch.object(sys, "executable", "/python"), \
             patch.object(chapter8.subprocess, "run") as run:
            chapter8.launch_minigame()
        run.assert_called_once_with(
            ["/python", os.path.join("chapter8game", "EasterEgg.py")], check=True
        )

    def test_packaged_minigame_uses_bundled_executable(self):
        executable = os.path.abspath(os.path.join(os.sep, "usb", "TextGame"))
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "executable", executable), \
             patch.object(sys, "platform", "linux"), \
             patch.object(chapter8.subprocess, "run") as run:
            chapter8.launch_minigame()
        run.assert_called_once_with(
            [os.path.join(os.path.dirname(executable), "Chapter8", "Chapter8")], check=True
        )

    def test_packaged_minigame_adds_windows_extension(self):
        executable = os.path.abspath(os.path.join(os.sep, "usb", "TextGame.exe"))
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "executable", executable), \
             patch.object(sys, "platform", "win32"), \
             patch.object(chapter8.subprocess, "run") as run:
            chapter8.launch_minigame()
        run.assert_called_once_with(
            [os.path.join(os.path.dirname(executable), "Chapter8", "Chapter8.exe")], check=True
        )

    def test_minigame_failure_is_reported(self):
        with patch.object(chapter8.subprocess, "run", side_effect=OSError("cannot launch")):
            with self.assertRaisesRegex(OSError, "cannot launch"):
                chapter8.launch_minigame()


if __name__ == "__main__":
    unittest.main()
