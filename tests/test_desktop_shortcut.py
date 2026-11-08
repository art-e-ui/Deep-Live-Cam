import os
import tempfile
import unittest

from modules import desktop_shortcut


class DesktopShortcutTests(unittest.TestCase):
    def test_generate_linux_desktop_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app_name = "Artesys-DLC-Shortcut-Test"
            script_path = os.path.join(temp_dir, "run.py")
            icon_path = os.path.join(temp_dir, "icon.png")

            with open(script_path, "w", encoding="utf-8") as handle:
                handle.write("print('shortcut-test')\n")
            with open(icon_path, "wb") as handle:
                handle.write(b"not-a-real-image")

            shortcut_path = desktop_shortcut.generate_desktop_shortcut(
                app_name=app_name,
                target_script=script_path,
                working_directory=temp_dir,
                icon_path=icon_path,
                install_dir=os.path.join(temp_dir, "desktop"),
            )

            self.assertTrue(os.path.exists(shortcut_path))
            with open(shortcut_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            self.assertIn("Name=Artesys-DLC-Shortcut-Test", content)
            self.assertIn("Exec=", content)
            self.assertIn("Terminal=false", content)


if __name__ == "__main__":
    unittest.main()
