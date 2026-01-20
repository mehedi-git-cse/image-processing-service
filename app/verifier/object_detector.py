import cv2
import numpy as np

# Lazy load model (to avoid numpy/torch initialization issues)
MODEL = None


def _get_model():
    """Lazy load YOLO model on first use"""
    global MODEL
    if MODEL is None:
        from ultralytics import YOLO
        try:
            MODEL = YOLO("yolov8n-seg.pt")  # nano = CPU optimized
        except Exception as e:
            print(f"ERROR loading YOLO model: {e}")
            raise
    return MODEL


def check_non_human_object_yolo(image_bytes,
                                conf_threshold: float = 0.4,
                                min_object_area_ratio: float = 0.005):
    """
    Detect whether any non-human object is present using YOLOv8 segmentation.

    Args:
        image_bytes: image in bytes
        conf_threshold: detection confidence threshold
        min_object_area_ratio: ignore very small objects

    Returns:
        dict:
        {
            "non_human_object_present": bool,
            "detected_objects": list,
            "reason": str
        }
    """

    try:
        # Decode image
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return _fail("Image decode failed")

        h, w = img.shape[:2]
        img_area = h * w

        # YOLO inference (CPU)
        model = _get_model()
        results = model.predict(
            source=img,
            conf=conf_threshold,
            device="cpu",
            verbose=False
        )[0]

        if results.masks is None:
            return _pass("No objects detected")

        detected_objects = []

        for box, cls, mask in zip(
            results.boxes.xyxy,
            results.boxes.cls,
            results.masks.data
        ):
            class_id = int(cls)
            class_name = MODEL.names[class_id]

            # Ignore humans
            if class_name == "person":
                continue

            # Area filtering
            mask_np = mask.cpu().numpy()
            obj_area = np.sum(mask_np > 0)

            if obj_area / img_area < min_object_area_ratio:
                continue

            detected_objects.append(class_name)

        if detected_objects:
            return {
                "non_human_object_present": True,
                "detected_objects": list(set(detected_objects)),
                "reason": f"Non-human objects detected: {set(detected_objects)}"
            }

        return _pass("Only human detected, no other objects")

    except Exception as e:
        return _fail(str(e))


def _pass(msg):
    return {
        "non_human_object_present": False,
        "detected_objects": [],
        "reason": msg
    }


def _fail(msg):
    return {
        "non_human_object_present": True,
        "detected_objects": [],
        "reason": f"Validation failed: {msg}"
    }
