import cv2
import numpy as np


def check_non_human_object_present(image_bytes,
                                   min_object_area_ratio: float = 0.01,
                                   edge_density_threshold: float = 0.02):
    """
    Check whether any non-human object is present in the image.

    This function ignores background color and only checks if there are
    any objects other than a human face/body.

    Args:
        image_bytes: Image in bytes format
        min_object_area_ratio: Minimum contour area ratio to be considered an object
        edge_density_threshold: Edge density threshold for object detection

    Returns:
        dict: {
            "non_human_object_present": bool,
            "edge_density": float,
            "object_count": int,
            "reason": str
        }
    """

    try:
        # Decode image
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return _fail("Image decode failed")

        h, w = img.shape[:2]
        total_area = h * w

        # Step 1: Detect face mask
        face_mask = _get_face_mask(img)

        # Step 2: Edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Remove face edges
        background_edges = cv2.bitwise_and(
            edges, edges, mask=cv2.bitwise_not(face_mask)
        )

        # Step 3: Edge density check
        background_area = np.sum(face_mask == 0)
        if background_area == 0:
            return _fail("No background area found")

        edge_pixels = np.sum(background_edges > 0)
        edge_density = edge_pixels / background_area

        # Step 4: Contour detection for objects
        contours, _ = cv2.findContours(
            background_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        significant_objects = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area / total_area >= min_object_area_ratio:
                significant_objects += 1

        # Step 5: Decision
        object_present = (
            significant_objects > 0 or edge_density > edge_density_threshold
        )

        if object_present:
            reason = (
                f"Non-human object detected "
                f"(objects={significant_objects}, edge_density={edge_density:.3f})"
            )
        else:
            reason = "No non-human object detected (PASS)"

        return {
            "non_human_object_present": bool(object_present),
            "edge_density": round(edge_density, 4),
            "object_count": significant_objects,
            "reason": reason
        }

    except Exception as e:
        return _fail(str(e))


def _get_face_mask(img):
    """
    Detect face and return expanded face mask.
    """
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5
    )

    for (x, y, fw, fh) in faces:
        expand = 0.25
        x1 = max(0, int(x - fw * expand))
        y1 = max(0, int(y - fh * expand))
        x2 = min(w, int(x + fw * (1 + expand)))
        y2 = min(h, int(y + fh * (1 + expand)))

        mask[y1:y2, x1:x2] = 255

    return mask


def _fail(msg):
    return {
        "non_human_object_present": True,
        "edge_density": 0.0,
        "object_count": 0,
        "reason": f"Validation failed: {msg}"
    }
