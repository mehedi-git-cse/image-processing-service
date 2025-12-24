def build_response(face, eyes, quality, pose, lighting, bg, geometry, text):
    """
    Build flexible, score-based verification response.
    
    Each check gives 1 point if passed. Minimum points required to pass = 6 (adjustable).
    """

    # Assign points for each criterion
    score = 0
    max_score = 8

    if face.get("face_detected", False):
        score += 1

    if eyes.get("eyes_detected", False):
        score += 1

    if not quality.get("is_blurry", True):
        score += 1

    # Flexible head pose check
    if pose.get("head_pose") in ["frontal", "slightly turned", "turned"]:
        score += 1

    if lighting.get("lighting") == "good":
        score += 1

    if bg.get("background_ok", False):
        score += 1

    if geometry.get("geometry_ok", False):
        score += 1

    if text.get("text_ok", False):
        score += 1

    # Define passing threshold (can be adjusted)
    passing_threshold = 7

    passed = score >= passing_threshold

    return {
        "image_status": "passed" if passed else "failed",
        "score": score,
        "max_score": max_score,
        "details": {
            "face": face,
            "eyes": eyes,
            "quality": quality,
            "pose": pose,
            "lighting": lighting,
            "background": bg,
            "geometry": geometry,
            "text": text
        }
    }
