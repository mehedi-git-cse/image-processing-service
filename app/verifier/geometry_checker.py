import cv2, numpy as np

def check_face_geometry(image_bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) != 1:
        return {"geometry_ok": False}

    x, y, w, h = faces[0]
    ih, iw, _ = img.shape

    area_ratio = (w * h) / (iw * ih)
    cx, cy = x + w / 2, y + h / 2

    return {
        "geometry_ok": 0.15 <= area_ratio <= 0.45 and
                       abs(cx - iw / 2) / iw < 0.15 and
                       abs(cy - ih / 2) / ih < 0.15
    }
