from fastapi import UploadFile
from app.utils.response import success, error
from app.utils.json_safe import to_python

from app.verifier.face_detector import detect_face
from app.verifier.eye_checker import check_eyes
from app.verifier.quality_checker import check_quality
from app.verifier.pose_checker import check_head_pose
from app.verifier.lighting_checker import check_lighting
from app.verifier.background_checker import check_background
from app.verifier.geometry_checker import check_face_geometry
from app.verifier.response_builder import build_response
from app.verifier.text_checker import check_text_presence
from app.verifier.background_uniform_checker import check_background_uniform_color


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

        # Run all checks
        result = build_response(
            detect_face(img),
            check_eyes(img),
            check_quality(img),
            check_head_pose(img),
            check_lighting(img),
            check_background(img),
            check_face_geometry(img),
            check_text_presence(img),
            check_background_uniform_color(img)
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
