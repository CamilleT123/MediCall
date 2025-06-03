import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose

def extract_hip_y_series(frames, side="RIGHT"):
    """
    Extracts a list of normalized hip Y positions (0 = top, 1 = bottom)
    from a list of frames using Mediapipe.
    """
    y_series = []
    with mp_pose.Pose(static_image_mode=False) as pose:
        for frame in frames:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                if side == "RIGHT":
                    hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y
                else:
                    hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
                y_series.append(hip_y)
            else:
                y_series.append(float('nan'))  # pose not found

    # Optional: interpolate or fill missing data
    y_series = _fill_missing(y_series)
    return y_series

def extract_landmarks_series(frames):
    """
    Extracts pose landmarks from a list of frames using Mediapipe Pose.
    
    Parameters:
        frames (List[np.ndarray]): list of BGR frames from a video

    Returns:
        List of 33-landmark lists (or None if no pose found in that frame)
    """
    landmarks_series = []

    with mp_pose.Pose(static_image_mode=False) as pose:
        for frame in frames:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                # Copy the list of 33 landmark objects
                landmarks_series.append(results.pose_landmarks.landmark)
            else:
                landmarks_series.append(None)  # Could interpolate later

    return landmarks_series

def _fill_missing(series):
    """
    Simple linear interpolation to fill NaNs.
    """
    import numpy as np
    s = np.array(series, dtype=np.float32)
    isnan = np.isnan(s)
    if isnan.any():
        not_nan = ~isnan
        s[isnan] = np.interp(isnan.nonzero()[0], not_nan.nonzero()[0], s[not_nan])
    return s.tolist()
