import cv2, numpy as np

def check_background(image_bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img, 100, 200)

    ratio = (edges > 0).sum() / (img.shape[0] * img.shape[1])

    return {
        "edge_ratio": round(ratio, 4),
        "background_ok": ratio < 0.05
    }
