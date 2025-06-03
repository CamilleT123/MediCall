# 🏋️‍♂️ Squat Analyzer & Form Comparison

A Python-based tool to:
- ✅ Count squats from a video
- 📐 Extract joint angles using Mediapipe
- 🤝 Compare user squats to a reference ("perfect") squat
- 💬 Provide directional, per-joint feedback (e.g., "knees bent too much")

---

## 📦 Features

- 🧠 Uses [Mediapipe](https://google.github.io/mediapipe/) for pose estimation
- 🧮 Computes hip, knee, and back angles
- 📊 Detects squat bottoms and compares joint angles at those key frames
- 💬 Returns structured feedback per joint (too bent, too open, etc.)

---

## 🛠 Installation

### 🔧 Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate         # or .venv\Scripts\activate on Windows
```
### 📦 Install dependencies
```bash
pip install -r requirements.txt
```
### 🚀 Usage
Analyze and Compare Squats
```bash
python main.py --user data/user.mp4 --ref data/reference.mp4 --rotate
```
--user: path to user's squat video

--ref: path to reference squat video

--rotate: optional flag to rotate input (e.g., from iPhone videos)

Output
Prints number of squats detected

Shows per-angle comparison at squat bottoms

Prints per-joint feedback, e.g.:

```text
Comparison result: {'knee_angle': -11.2, 'hip_angle': -17.9, 'back_angle': 28.9}
Form difference at first squat bottom:
⬇️ Too closed (-11.2°): ease off that joint slightly.
⬇️ Too closed (-17.9°): ease off that joint slightly.
⬆️ Too open (+28.9°): reduce the angle slightly.
```
### 🧪 Project Structure
```bash
squat-analyzer/
├── main.py                   # Entry point
├── requirements.txt
├── src/
│   ├── video_utils.py        # Video loading, rotation
│   ├── pose_tracking.py      # Landmark extraction
│   ├── squat_counter.py      # Hip Y tracking and rep detection
│   ├── form_analysis.py      # Angle evaluation and feedback
│   └── cli/
│       └── analyze_video.py  # Full video analysis logic
└── data/
    ├── user.mp4
    └── reference.mp4

```
### 🔍 Future Ideas
📹 Output visual overlay (joint angle display)

🧾 Export per-rep feedback to CSV or PDF

🌐 Connect to web interface with realtime/upload & scoring


