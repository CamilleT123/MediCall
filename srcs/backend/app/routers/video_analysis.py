from fastapi import APIRouter, UploadFile, File, HTTPException
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import json

router = APIRouter()

# Initialisation de MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Liste des landmarks importants
KEY_LANDMARKS = {
    "LEFT_HIP": 23, "RIGHT_HIP": 24,
    "LEFT_KNEE": 25, "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27, "RIGHT_ANKLE": 28,
    "LEFT_SHOULDER": 11, "RIGHT_SHOULDER": 12
}

# Fonction pour calculer un angle entre 3 points
def calculate_angle(a, b, c):
    a = np.array(a)  # Premier point
    b = np.array(b)  # Milieu (point d'articulation)
    c = np.array(c)  # Troisième point
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)

# Fonction pour extraire les angles du squat
def extract_squat_data(results):
    data = {"angles": {}}
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        data["angles"]["left_knee"] = calculate_angle(
            [landmarks[KEY_LANDMARKS["LEFT_HIP"]].x, landmarks[KEY_LANDMARKS["LEFT_HIP"]].y],
            [landmarks[KEY_LANDMARKS["LEFT_KNEE"]].x, landmarks[KEY_LANDMARKS["LEFT_KNEE"]].y],
            [landmarks[KEY_LANDMARKS["LEFT_ANKLE"]].x, landmarks[KEY_LANDMARKS["LEFT_ANKLE"]].y]
        )

        data["angles"]["right_knee"] = calculate_angle(
            [landmarks[KEY_LANDMARKS["RIGHT_HIP"]].x, landmarks[KEY_LANDMARKS["RIGHT_HIP"]].y],
            [landmarks[KEY_LANDMARKS["RIGHT_KNEE"]].x, landmarks[KEY_LANDMARKS["RIGHT_KNEE"]].y],
            [landmarks[KEY_LANDMARKS["RIGHT_ANKLE"]].x, landmarks[KEY_LANDMARKS["RIGHT_ANKLE"]].y]
        )

        data["angles"]["back_angle"] = calculate_angle(
            [landmarks[KEY_LANDMARKS["LEFT_SHOULDER"]].x, landmarks[KEY_LANDMARKS["LEFT_SHOULDER"]].y],
            [landmarks[KEY_LANDMARKS["LEFT_HIP"]].x, landmarks[KEY_LANDMARKS["LEFT_HIP"]].y],
            [landmarks[KEY_LANDMARKS["LEFT_KNEE"]].x, landmarks[KEY_LANDMARKS["LEFT_KNEE"]].y]
        )

    return data["angles"]

@router.post("/analyze_video/")
async def analyze_video(file: UploadFile = File(...)):
    try:
        # Sauvegarde temporaire du fichier
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            temp_video.write(await file.read())
            temp_video_path = temp_video.name
        
        cap = cv2.VideoCapture(temp_video_path)
        frames_data = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convertir l'image en RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détection des points clés
            results = pose.process(frame_rgb)
            
            # Extraction des angles
            squat_data = extract_squat_data(results)
            frames_data.append(squat_data)
        
        cap.release()

        return {"message": "Analyse terminée", "data": frames_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def has_movement(prev_points, curr_points, threshold=2):
    """
    Vérifie si le mouvement est significatif entre les deux frames en comparant la distance entre les points.
    """
    if prev_points is None:
        return True  # Premier frame, donc on considère qu'il y a du mouvement
    
    for body_element in curr_points:
      for coordinate in ["x", "y", "z"]:
        if (np.linalg.norm(np.array(prev_points[body_element][coordinate]) - np.array(curr_points[body_element][coordinate])))> threshold:
            return True
        
    return False


def new_extract_squat_data(cur_landmark, prev_landmark, threshold = 0.1):
  data = {"landmarks": {}, "angles": {}}

  if cur_landmark.pose_landmarks:
    landmarks = cur_landmark.pose_landmarks.landmark
    
    # Récupération des coordonnées des points clés
    for name, idx in KEY_LANDMARKS.items():
        data["landmarks"][name] = {
            "x": landmarks[idx].x,
            "y": landmarks[idx].y,
            "z": landmarks[idx].z
        }
    # Calcul des angles et Incrémenter que s'il y a une différence entre la position actuelle et celle d'avant
    if has_movement(prev_landmark, data["landmarks"], threshold):
      # Calcul des angles importants pour le squat
      data["angles"]["left_knee"] = calculate_angle(
          [landmarks[KEY_LANDMARKS["LEFT_HIP"]].x, landmarks[KEY_LANDMARKS["LEFT_HIP"]].y],
          [landmarks[KEY_LANDMARKS["LEFT_KNEE"]].x, landmarks[KEY_LANDMARKS["LEFT_KNEE"]].y],
          [landmarks[KEY_LANDMARKS["LEFT_ANKLE"]].x, landmarks[KEY_LANDMARKS["LEFT_ANKLE"]].y]
      )
      
      data["angles"]["right_knee"] = calculate_angle(
          [landmarks[KEY_LANDMARKS["RIGHT_HIP"]].x, landmarks[KEY_LANDMARKS["RIGHT_HIP"]].y],
          [landmarks[KEY_LANDMARKS["RIGHT_KNEE"]].x, landmarks[KEY_LANDMARKS["RIGHT_KNEE"]].y],
          [landmarks[KEY_LANDMARKS["RIGHT_ANKLE"]].x, landmarks[KEY_LANDMARKS["RIGHT_ANKLE"]].y]
      )
      
      data["angles"]["back_angle"] = calculate_angle(
          [landmarks[KEY_LANDMARKS["LEFT_SHOULDER"]].x, landmarks[KEY_LANDMARKS["LEFT_SHOULDER"]].y],
          [landmarks[KEY_LANDMARKS["LEFT_HIP"]].x, landmarks[KEY_LANDMARKS["LEFT_HIP"]].y],
          [landmarks[KEY_LANDMARKS["LEFT_KNEE"]].x, landmarks[KEY_LANDMARKS["LEFT_KNEE"]].y]
      )
      prev_landmark = data["landmarks"]
  return data["angles"], prev_landmark