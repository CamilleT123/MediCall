from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import users, items
from app.routers.video_analysis import extract_squat_data, new_extract_squat_data
from app.routers.message import llm, stream_tts
import cv2
import asyncio
import base64
import numpy as np
import mediapipe as mp
import json
import tempfile
import math

# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Ajout du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(items.router)
# app.include_router(video_analysis.router)

@app.get("/api/")
def root():
	return {"message": "Bienvenue sur FastAPI avec PostgreSQL !"}

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

@app.websocket("/ws/video")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    frames_data = []
    prev_landmark = None
    try:    
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                data = json.loads(message)
                if data.get("action") == "close":
                    break
            except asyncio.TimeoutError:
                pass
            except json.JSONDecodeError:
                pass
            ret, frame = cap.read()
            if not ret:
                break

            # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # results = pose.process(rgb_frame)
            # squat_data = extract_squat_data(results)
            # frames_data.append(squat_data)
            # await llm(squat_data, websocket=websocket)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détection des points clés de la frame en cours
            cur_landmark = pose.process(frame_rgb)

            # Calcul des angles uniquement s'il y a un mouvement détecté
            angles, prev_landmark = new_extract_squat_data(cur_landmark, prev_landmark, 0.1)
            if len(angles)>0: # Vérifier si des angles ont été calculés
                frames_data.append(angles)
            
            # Envoi au LLM toutes les 20 frames (éviter trop d'appels inutiles)
            if len(frames_data) >= 25:
                # print("envoi")
                feedback = "TEST"
                min_left_knee, min_right_knee, min_back_angle = 180, 180, 180
                for el in frames_data:
                    if el["left_knee"]< min_left_knee:
                        min_left_knee = el["left_knee"]
                    if el["right_knee"]< min_right_knee:
                        min_right_knee = el["right_knee"]
                    if el["back_angle"]< min_back_angle:
                        min_back_angle = el["back_angle"]

                mean_knee = (min_left_knee+min_right_knee)/2
                if (mean_knee <120) & (min_back_angle<120):
                    if mean_knee - min_back_angle > 10:
                        feedback = "Keep your back straight"
                    elif mean_knee < 60:
                        if min_left_knee - min_right_knee > 10 :
                            feedback = "Bend your left knee more"
                        elif min_right_knee - min_left_knee > 10 :
                            feedback = "Bend your right knee more"
                        else:
                            feedback = "Good job"
                    elif (mean_knee < 45) and (min_back_angle < 45) :
                        feedback = "Good job"
                    elif (mean_knee > 45) and (mean_knee < 70) and (min_back_angle < 90) :

                        feedback = "Bend your knees more"

                    # await answer(frames_data, gt)
                await stream_tts(feedback, websocket)
                #await llm(frames_data, websocket=websocket)
                # await answer(frames_data, gt)
                frames_data.clear()
            
            if cur_landmark.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, cur_landmark.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )

            if len(angles)>0:
                cv2.putText(frame, f"Gauche: {angles.get('left_knee', 0):.2f}", 
                                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Droite: {angles.get('right_knee', 0):.2f}", 
                                (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Dos: {angles.get('back_angle', 0):.2f}", 
                                (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode()

            await websocket.send_text(json.dumps({"image": img_base64}))
            await asyncio.sleep(0.03)
    except WebSocketDisconnect:
        print("❌ WebSocket déconnecté par le client.")

    finally:
        cap.release()
        print("\n===== Fin du streaming WebSocket =====")
        print(f"Nombre total de frames collectées : {len(frames_data)}")
        print("Aperçu des données collectées :")
        for i, data in enumerate(frames_data[:5]):
            print(f"Frame {i+1} : {data}")

        json_filename = "dataMouv.json"
        with open(json_filename, "w") as f:
            json.dump(frames_data, f, indent=4)

        await websocket.close()
        print("✅ WebSocket fermé proprement.\n")
    # return {"message": "Analyse terminée", "data": frames_data}
