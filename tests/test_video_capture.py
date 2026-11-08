import unittest
from unittest.mock import patch

import numpy as np

from modules.video_capture import VideoCapturer


class TestVideoCaptureNetworkSources(unittest.TestCase):
    @patch("cv2.VideoCapture")
    def test_start_accepts_rtsp_url(self, mock_capture):
        mock_cap = mock_capture.return_value
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            3: 640,
            4: 480,
            5: 30,
        }.get(prop, 0)
        mock_cap.read.side_effect = [
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
            (True, np.zeros((480, 640, 3), dtype=np.uint8)),
        ]

        capturer = VideoCapturer("rtsp://user:pass@192.168.1.20:554/stream")
        ok = capturer.start(640, 480, 30)

        self.assertTrue(ok)
        mock_capture.assert_called_with("rtsp://user:pass@192.168.1.20:554/stream", 0)

    @patch("cv2.VideoCapture")
    def test_start_accepts_mjpeg_http_url(self, mock_capture):
        mock_cap = mock_capture.return_value
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            3: 1280,
            4: 720,
            5: 20,
        }.get(prop, 0)
        mock_cap.read.side_effect = [
            (True, np.zeros((720, 1280, 3), dtype=np.uint8)),
            (True, np.zeros((720, 1280, 3), dtype=np.uint8)),
            (True, np.zeros((720, 1280, 3), dtype=np.uint8)),
        ]

        capturer = VideoCapturer("http://192.168.1.50:8080/video")
        ok = capturer.start(1280, 720, 20)

        self.assertTrue(ok)
        mock_capture.assert_called_with("http://192.168.1.50:8080/video", 0)


if __name__ == "__main__":
    unittest.main()
