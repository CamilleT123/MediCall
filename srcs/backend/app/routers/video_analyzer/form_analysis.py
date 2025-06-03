import numpy as np
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
import mediapipe as mp
# from mediapipe.solutions.pose import PoseLandmark


# ---------------------
# ANGLE COMPUTATION
# ---------------------

def compute_angle(a, b, c):
    """Compute angle ABC in degrees."""
    ba = np.array([a.x - b.x, a.y - b.y])
    bc = np.array([c.x - b.x, c.y - b.y])
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

def compute_back_angle(shoulder, hip):
    """
    Computes vertical angle of the back (in degrees) from shoulder to hip.
    90 = upright, lower = leaning forward.
    """    
    dy = hip.y - shoulder.y
    dx = hip.x - shoulder.x
    # return abs(np.degrees(np.arctan2(dy, dx)))
    return np.degrees(np.arctan2(dy, dx))


# ---------------------
# FRAME-LEVEL ANALYSIS
# ---------------------

def is_deep_enough(hip, knee, threshold=0.05):
    """True if hip is significantly below knee."""
    return (hip.y - knee.y) > threshold

def compute_joint_angles(landmarks, side="RIGHT"):
    """Return joint angles from a frame's landmarks."""
    if side == "RIGHT":
        hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]
        shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
    else:
        hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]

    return {
        "knee_angle": compute_angle(hip, knee, ankle),
        "hip_angle": compute_angle(shoulder, hip, knee),
        "back_angle": compute_angle(shoulder, hip, ankle)
    }

def evaluate_squat_frame(landmarks, side="RIGHT"):
    """Full form evaluation: depth + angles from one frame."""
    if side == "RIGHT":
        hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]
        shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
    else:
        hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]

    return {
        "depth_ok": is_deep_enough(hip, knee),
        "hip_y": round(hip.y, 3),
        "knee_y": round(knee.y, 3),
        "hip_knee_diff": round(hip.y - knee.y, 3),
        "back_angle": round(compute_back_angle(shoulder, hip), 1),
        "hip_angle": round(compute_angle(shoulder, hip, knee), 1),
        "knee_angle": round(compute_angle(hip, knee, ankle), 1)
    }

# ---------------------
# MULTI-FRAME ANALYSIS
# ---------------------

def _average_angles(angle_list):
    """Average each joint angle over multiple frames."""
    from collections import defaultdict
    avg = defaultdict(float)
    for angles in angle_list:
        for k, v in angles.items():
            avg[k] += v
    n = len(angle_list)
    return {k: v / n for k, v in avg.items()}

def compare_squat_forms(user_angles_seq, ref_angles_seq):
    """Compare average joint angles between user and reference."""
    joint_names = ["knee_angle", "hip_angle", "back_angle"]
    user_avg = _average_angles(user_angles_seq)
    ref_avg = _average_angles(ref_angles_seq)
    return {
        # joint: abs(user_avg[joint] - ref_avg[joint]) for joint in joint_names
        joint: (user_avg[joint] - ref_avg[joint]) for joint in joint_names
        # joint: (ref_avg[joint] - user_avg[joint]) for joint in joint_names

    }

def generate_feedback(diffs: dict):
    feedback = {}
    for joint, diff in diffs.items():
        if abs(diff) < 5:
            feedback[joint] = "✔️ Close to reference."
        elif diff > 5:
            feedback[joint] = f"⬆️ Too open (+{diff:.1f}°): reduce the angle slightly."
        elif diff < -5:
            feedback[joint] = f"⬇️ Too closed ({diff:.1f}°): ease off that joint slightly."
    return feedback


from collections import defaultdict
from typing import List

def compare_squat_forms_notworking(user_landmarks_series: List, ref_landmarks_series: List, side="RIGHT"):
    """
    Compares the squat form of a user to a reference across frames.
    
    Parameters:
        user_landmarks_series (List[List[landmarks]]): List of 33-keypoint lists (or None) from user's video
        ref_landmarks_series  (List[List[landmarks]]): Same structure from reference video
        side (str): "RIGHT" or "LEFT"

    Returns:
        {
            'average_difference': {joint: float},
            'per_frame_diff': List[Dict[str, float]],
            'user_average': Dict[str, float],
            'ref_average': Dict[str, float]
        }
    """
    from .form_analysis import evaluate_squat_frame

    # Safety: ensure same length
    length = min(len(user_landmarks_series), len(ref_landmarks_series))
    
    user_metrics = []
    ref_metrics = []
    diffs = []

    for i in range(length):
        u_lm = user_landmarks_series[i]
        r_lm = ref_landmarks_series[i]

        if u_lm is None or r_lm is None:
            continue

        u_metrics = evaluate_squat_frame(u_lm, side)
        r_metrics = evaluate_squat_frame(r_lm, side)

        # Keep angles only for comparison
        angle_keys = ["knee_angle", "hip_angle", "back_angle"]
        u_angles = {k: u_metrics[k] for k in angle_keys}
        r_angles = {k: r_metrics[k] for k in angle_keys}
        diff = {k: abs(u_angles[k] - r_angles[k]) for k in angle_keys}

        user_metrics.append(u_angles)
        ref_metrics.append(r_angles)
        diffs.append(diff)

    def _average(metrics_list):
        avg = defaultdict(float)
        for item in metrics_list:
            for k, v in item.items():
                avg[k] += v
        n = len(metrics_list)
        return {k: round(v / n, 2) for k, v in avg.items()} if n else {}

    return {
        "average_difference": _average(diffs),
        "per_frame_diff": diffs,
        "user_average": _average(user_metrics),
        "ref_average": _average(ref_metrics)
    }