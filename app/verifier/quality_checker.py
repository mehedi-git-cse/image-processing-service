import cv2
import numpy as np

def check_quality(image_bytes, threshold: float = 100.0):
    """
    Check image quality using Laplacian variance.
    
    Args:
        image_bytes: Image in bytes
        threshold: Blur threshold (default=100)
        
    Returns:
        dict: {
            "blur_score": float,
            "is_blurry": bool
        }
    """
    # Decode image to grayscale
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    
    # Compute Laplacian variance (blur score)
    blur_score = float(cv2.Laplacian(img, cv2.CV_64F).var())
    
    # Determine if image is blurry
    is_blurry = blur_score < threshold
    
    # Debug output
    #print(f"Blur score: {blur_score:.2f}")
    #print("Blurry image" if is_blurry else "Clear image")
    
    # Return JSON-friendly response
    return {
        "blur_score": blur_score,
        "is_blurry": bool(is_blurry)
    }
