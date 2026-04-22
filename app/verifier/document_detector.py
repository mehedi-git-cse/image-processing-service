import cv2
import numpy as np


def check_held_document(image_bytes):
    """
    Detect held documents (passport, ID card, badge, book, certificate)
    using rotated-rectangle geometry and color uniformity, independent
    of YOLO class labels.

    Catches tilted / rounded-corner cards that 4-point polygon
    approximation would miss.

    Returns:
        {
            "document_present": bool,
            "candidates": int,
            "reason": str
        }
    """
    try:
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return _fail("Image decode failed")

        h, w = img.shape[:2]
        img_area = float(h * w)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Two edge strategies combined to catch low-contrast document borders
        edges1 = cv2.Canny(blurred, 30, 120)
        edges2 = cv2.Canny(blurred, 75, 200)
        edges = cv2.bitwise_or(edges1, edges2)

        # Close border gaps
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=2)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            area_ratio = area / img_area

            # Ignore noise and whole-image borders
            if area_ratio < 0.01 or area_ratio > 0.55:
                continue

            # Rotated minimum-area rectangle (handles tilted passports/cards)
            rect = cv2.minAreaRect(cnt)
            (_, _), (rw, rh), _ = rect
            if rw < 20 or rh < 20:
                continue

            rect_area = rw * rh
            if rect_area == 0:
                continue

            # Rectangularity: contour fills most of its rotated bounding rect
            rectangularity = area / rect_area
            if rectangularity < 0.70:
                continue

            # Aspect ratio typical of cards / passports / books / badges
            aspect = max(rw, rh) / min(rw, rh)
            if not (1.1 <= aspect <= 2.2):
                continue

            # Sample color uniformity inside the rect - documents have
            # large relatively uniform regions
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            masked_pixels = gray[mask == 255]
            if masked_pixels.size < 200:
                continue

            color_std = float(np.std(masked_pixels))
            # Passports/cards have moderate std (not random noise, not flat wall)
            if color_std > 75:
                continue

            candidates += 1

        document_present = candidates > 0

        return {
            "document_present": document_present,
            "candidates": candidates,
            "reason": (
                "A document / card / passport appears to be in the frame. Please remove it."
                if document_present
                else "No document detected in frame"
            ),
        }

    except Exception as e:
        return _fail(str(e))


def _fail(msg):
    return {
        "document_present": False,
        "candidates": 0,
        "reason": f"Document detection failed: {msg}",
    }
