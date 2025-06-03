from video_analyzer.video_utils import load_and_preprocess_video
from video_analyzer.pose_tracking import extract_landmarks_series
from video_analyzer.pose_tracking import extract_hip_y_series
from video_analyzer.form_analysis import compute_joint_angles
from video_analyzer.form_analysis import compare_squat_forms
from video_analyzer.form_analysis import evaluate_squat_frame
from video_analyzer.form_analysis import generate_feedback

from video_analyzer.counter import count_squats

# Load videos
user_frames = load_and_preprocess_video( "data/test/test.mp4")
ref_frames = load_and_preprocess_video("data/reference/perfectsquat.mp4")

# Extract pose landmarks over time
user_landmarks = extract_landmarks_series(user_frames)
ref_landmarks = extract_landmarks_series(ref_frames)

user_hip_y = extract_hip_y_series(user_frames)
user_count, x_user, _ = count_squats(user_hip_y)
print('abscisses? ', x_user)

ref_hip_y = extract_hip_y_series(ref_frames)
ref_count, x_ref, _ = count_squats(ref_hip_y)
print('abscisses? ', x_ref)



# Compute joint angles per frame
# user_angles = [compute_joint_angles(lm) for lm in user_landmarks]
# ref_angles = [compute_joint_angles(lm) for lm in ref_landmarks]

# Compute joint angles per frame at the bottom of squats
user_angles = [compute_joint_angles(user_landmarks[i]) for i in x_user if user_landmarks[i] is not None]
ref_angles = [compute_joint_angles(ref_landmarks[i]) for i in x_ref if ref_landmarks[i] is not None]

print("user angles",user_angles)
print("ref angles",ref_angles)

# Compare over time or at bottom of each squat
comparison_results = compare_squat_forms(user_angles, ref_angles)
print(f"Comparison result: {comparison_results}")
print(f"Squats counted: {user_count}")

# Evaluate form at first bottom position
for i in range(len(x_user)):
    idx_user = x_user[i]
    idx_ref = x_ref[0]
    user_eval = evaluate_squat_frame(user_landmarks[idx_user])
    ref_eval  = evaluate_squat_frame(ref_landmarks[idx_ref])

    angle_keys = ["knee_angle", "hip_angle", "back_angle"]
    frame_diff = {k: (user_eval[k] - ref_eval[k]) for k in angle_keys}

    print(f"Form difference at squat bottom number {i}:")
    print(frame_diff)
    print(generate_feedback(frame_diff))


# print("""🏋️ You're close, but there are important differences in your squat form:

# Work on increasing depth by bending your knees and hips more.

# Pay attention to your torso position — aim for a slight forward lean with a stable back.

# Consider doing mobility drills (e.g., hip and ankle flexibility) to improve your range of motion and squat mechanics.""")