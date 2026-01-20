import cv2
import numpy as np

# Lazy load model (to avoid numpy/torch initialization issues)
MODEL = None
ALLOWED_CLASS = "person"


def _get_model():
    """Lazy load YOLO model on first use"""
    global MODEL
    if MODEL is None:
        from ultralytics import YOLO
        try:
            MODEL = YOLO("yolov8n.pt")  # object detection only (lighter than seg)
        except Exception as e:
            print(f"ERROR loading YOLO model: {e}")
            raise
    return MODEL


def check_human_only(image_bytes, conf_threshold=0.4):
    """
    FAIL if any object other than 'person' is detected
    """

    print( "Running human-only detection..." )

    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return _fail("Image decode failed")

    model = _get_model()
    results = model.predict(
        source=img,
        conf=conf_threshold,
        device="cpu",
        verbose=False
    )[0]

    detected = []
    person_count = 0

    for cls in results.boxes.cls:
        class_name = model.names[int(cls)]
        detected.append(class_name)

        if class_name == "person":
            person_count += 1

    non_human_objects = [x for x in detected if x != ALLOWED_CLASS]

    if person_count != 1:
        return _fail(f"Invalid number of persons detected: {person_count}")

    if non_human_objects:
        return {
            "status": "FAIL",
            "reason": f"Non-human objects detected: {list(set(non_human_objects))}",
            "objects": list(set(non_human_objects))
        }

    return {
        "status": "PASS",
        "reason": "Only human detected",
        "objects": []
    }


def _fail(msg):
    return {
        "status": "FAIL",
        "reason": msg,
        "objects": []
    }
