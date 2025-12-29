from fastapi import FastAPI, File, UploadFile, Request
from fastapi.exceptions import RequestValidationError

from app.utils.security import verify_api_key_plain
from app.utils.exception_handler import validation_exception_handler
from app.utils.response import error

from app.controllers.auth_controller import TokenRequest, generate_token
from app.controllers.face_verification_controller import verify_face_image
from fastapi import Header, UploadFile, File

app = FastAPI(title="Image Verification Service")

# ================= Auth Routes =================
@app.post("/api/v1/get-token")
async def get_token(request: Request,req: TokenRequest):
    # For debugging purposes: log raw body and headers
    # body = await request.body()
    # headers = dict(request.headers)
    # print("Raw body:", body)
    # print("Headers:", headers)

    return generate_token(req)

# ================= Face Verification =================
@app.post("/api/v1/verify-face")
async def verify_face(
    image: UploadFile = File(...),
    authorization: str | None = Header(default=None)
):
    # Validate uploaded file is JPG/JPEG/PNG
    allowed_exts = {"jpg", "jpeg", "png"}
    filename = (image.filename or "").lower()
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    content_type = (getattr(image, "content_type", "") or "").lower()

    if ext not in allowed_exts or not content_type.startswith("image/"):
        return error(msg="Uploaded file must be a JPG or PNG image", status_code=400)

    auth_result = verify_api_key_plain(authorization)

    # If auth failed → response engine returned
    if isinstance(auth_result, dict) and auth_result.get("response") == "error":
        return auth_result

    # Token valid → continue
    return await verify_face_image(image)

# ================= Global Exception Handler =================
app.add_exception_handler(RequestValidationError, validation_exception_handler)
