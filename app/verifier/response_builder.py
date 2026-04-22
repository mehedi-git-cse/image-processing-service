def build_response(face, eyes, quality, pose, lighting, bg, geometry, text, object_detector, human_only, hands, ai_check=None, doc_check=None):
    """
    Build flexible, score-based verification response.
    
    Each check gives 1 point if passed. Minimum points required to pass = 10 (adjustable).
    """

    # Assign points for each criterion
    score = 0
    max_score = 13

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

    if object_detector.get("non_human_object_present", False) is False:
        score += 1
    
    if human_only.get("status") == "PASS":
        score += 1
    
    if hands.get("is_ok", False):
        score += 1

    if ai_check and not ai_check.get("is_ai_generated", False):
        score += 1

    if doc_check and not doc_check.get("document_present", False):
        score += 1

    # Define passing threshold (can be adjusted)
    passing_threshold = 10

    # Mandatory (hard-fail) criteria for official/formal photo.
    # If any of these fail, the image fails regardless of score.
    mandatory_failures = []

    if not face.get("face_detected", False):
        mandatory_failures.append("No clear single face detected. Please upload a photo with exactly one person's face clearly visible.")

    if human_only.get("status") != "PASS":
        mandatory_failures.append("Only one person should be in the photo. Please remove other people or objects from the frame.")

    if object_detector.get("non_human_object_present", True):
        mandatory_failures.append("Other objects were detected in the photo. Please use a plain background without any items.")

    if not hands.get("is_ok", False):
        mandatory_failures.append("Your hand is covering part of your face. Please keep your hands away from your face.")

    if not text.get("text_ok", False):
        mandatory_failures.append("Text or watermark detected in the photo. Please upload a clean photo without any text or logos.")

    if ai_check and ai_check.get("is_ai_generated", False):
        mandatory_failures.append("This photo appears to be AI-generated or heavily edited. Please upload a real, unedited photo of yourself.")

    if doc_check and doc_check.get("document_present", False):
        mandatory_failures.append("A document, card, or passport appears to be in the photo. Please take the photo without holding any document.")

    score_passed = score >= passing_threshold
    passed = score_passed and not mandatory_failures

    return {
        "image_status": "passed" if passed else "failed",
        "score": score,
        "max_score": max_score,
        "mandatory_failures": mandatory_failures,
        "details": {
            "face": face,
            "eyes": eyes,
            "quality": quality,
            "pose": pose,
            "lighting": lighting,
            "background": bg,
            "geometry": geometry,
            "text": text,
            "hands": hands,
            "object_detector": object_detector,
            "human_only": human_only,
            "ai_check": ai_check,
            "document_detector": doc_check,
        }
    }
