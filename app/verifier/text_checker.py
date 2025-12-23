import cv2
import numpy as np
import pytesseract

# Optional: set path to tesseract.exe on Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TEXT_AREA_THRESHOLD = 0.06  # 6%

def check_text_presence(image_bytes: bytes):
    # Convert bytes to numpy array and decode image
    img_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Perform OCR
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    h, w = gray.shape
    img_area = h * w

    text_area = 0
    word_count = 0

    # Loop through all detected text elements
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        try:
            conf = float(data["conf"][i])
        except ValueError:
            conf = 0

        # Only count words with confidence > 60 and non-empty text
        if conf > 60 and text != "":
            x, y, bw, bh = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            text_area += bw * bh
            word_count += 1

    ratio = round(text_area / img_area, 4)

    return {
        "text_detected": word_count > 0,
        "word_count": word_count,
        "text_area_ratio": ratio,
        "text_ok": ratio < TEXT_AREA_THRESHOLD
    }