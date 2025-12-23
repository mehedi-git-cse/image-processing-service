import cv2, mediapipe as mp, numpy as np

mp_face_mesh = mp.solutions.face_mesh

def check_head_pose(image_bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with mp_face_mesh.FaceMesh(static_image_mode=True) as fm:
        res = fm.process(rgb)
        if not res.multi_face_landmarks:
            return {"head_pose": "unknown"}

        lm = res.multi_face_landmarks[0].landmark
        yaw = lm[263].x - lm[33].x
        return {"head_pose": "frontal" if abs(yaw) < 0.03 else "turned"}
