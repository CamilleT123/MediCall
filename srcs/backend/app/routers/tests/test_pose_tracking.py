import unittest
import cv2
import numpy as np
from ..src.pose_tracking import extract_hip_y_series
from ..src.video_utils import load_and_preprocess_video

class TestPoseTracking(unittest.TestCase):

    def test_hip_y_series_shape(self):
        """Check that the returned hip Y values match the number of frames."""
        video_path = "data/test/sample_squat.mp4"
        frames = load_and_preprocess_video(video_path)
        hip_y = extract_hip_y_series(frames)

        self.assertEqual(len(hip_y), len(frames))
        self.assertTrue(all(isinstance(y, float) for y in hip_y))

    def test_no_frames(self):
        """Test with empty frame list."""
        hip_y = extract_hip_y_series([])
        self.assertEqual(hip_y, [])

    def test_static_frame(self):
        """Test with a single repeated frame to ensure consistent output."""
        frame = cv2.imread("data/test/static_person.png")
        frames = [frame] * 10
        hip_y = extract_hip_y_series(frames)

        self.assertEqual(len(hip_y), 10)
        self.assertTrue(np.std(hip_y) < 1e-4)  # Expect very little variation

if __name__ == '__main__':
    unittest.main()