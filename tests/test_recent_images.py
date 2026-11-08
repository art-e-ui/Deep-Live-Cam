import os
import tempfile
import unittest

from modules import recent_images


class RecentImagesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        recent_images.RECENT_IMAGES_PATH = os.path.join(self.temp_dir.name, "recent_images.json")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_record_recent_image_keeps_latest_first_and_deduplicates(self) -> None:
        first = "/tmp/face_a.png"
        second = "/tmp/face_b.png"

        recent_images.record_recent_image("source", first)
        recent_images.record_recent_image("source", second)
        recent_images.record_recent_image("source", first)

        self.assertEqual(
            recent_images.get_recent_images("source"),
            [first, second],
        )

    def test_record_recent_image_tracks_separate_kinds(self) -> None:
        face = "/tmp/face.png"
        bg = "/tmp/background.png"

        recent_images.record_recent_image("source", face)
        recent_images.record_recent_image("background", bg)

        self.assertEqual(recent_images.get_recent_images("source"), [face])
        self.assertEqual(recent_images.get_recent_images("background"), [bg])


if __name__ == "__main__":
    unittest.main()
