from fastapi import UploadFile
from app.utils.response import success, error
from app.utils.json_safe import to_python
import asyncio

from app.verifier.face_detector import detect_face
from app.verifier.eye_checker import check_eyes
from app.verifier.quality_checker import check_quality
from app.verifier.pose_checker import check_head_pose
from app.verifier.lighting_checker import check_lighting
from app.verifier.background_checker import check_background
from app.verifier.geometry_checker import check_face_geometry
from app.verifier.response_builder import build_response
from app.verifier.text_checker import check_text_presence
from app.verifier.object_detector import check_non_human_object_yolo
from app.verifier.human_only_detector import check_human_only
from app.verifier.hand_detector import check_hands


async def verify_face_image(image: UploadFile):
    try:
        # Read image
        img = await image.read()
        if not img:
            return error(
                msg="Empty image file",
                response_type="FACE_VERIFY",
                status_code=400
            )

        # Run all checks in parallel (async)
        face, eyes, quality, pose, lighting, bg, geometry, text, obj_detect, human, hands = await asyncio.gather(
            asyncio.to_thread(detect_face, img),
            asyncio.to_thread(check_eyes, img),
            asyncio.to_thread(check_quality, img),
            asyncio.to_thread(check_head_pose, img),
            asyncio.to_thread(check_lighting, img),
            asyncio.to_thread(check_background, img),
            asyncio.to_thread(check_face_geometry, img),
            asyncio.to_thread(check_text_presence, img),
            asyncio.to_thread(check_non_human_object_yolo, img),
            asyncio.to_thread(check_human_only, img),
            asyncio.to_thread(check_hands, img)
        )
        
        result = build_response(
            face, eyes, quality, pose, lighting, bg, geometry, text, obj_detect, human, hands
        )

        # Success response
        return success(
            data=to_python(result),
            msg="Face verification completed",
            response_type="FACE_VERIFY"
        )

    except Exception as e:
        # Any unexpected error
        return error(
            msg="Face verification failed",
            data={"error": str(e)},
            response_type="FACE_VERIFY",
            status_code=500
        )
