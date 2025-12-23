import cv2, numpy as np

def check_lighting(image_bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    brightness = np.mean(img)

    if brightness < 70:
        status = "too_dark"
    elif brightness > 190:
        status = "too_bright"
    else:
        status = "good"

    return {"brightness": brightness, "lighting": status}
