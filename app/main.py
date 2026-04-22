from fastapi import FastAPI, File, UploadFile, Request, Header
from fastapi.exceptions import RequestValidationError

from app.utils.security import verify_api_key_plain
from app.utils.exception_handler import validation_exception_handler
from app.utils.file_validation import validate_uploaded_image

from app.controllers.auth_controller import TokenRequest, generate_token
from app.controllers.face_verification_controller import verify_face_image
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Image Verification Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= Health Check Routes =================
@app.get("/")
async def root():
    """
    Root endpoint - Health check
    Returns service status and documentation links
    """
    return {
        "status": "running",
        "service": "Image Verification Service",
        "message": "✅ Image Processing Service is running",
        "version": "1.0.0",
        "documentation": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc",
        "endpoints": {
            "get_token": "POST /api/v1/get-token",
            "verify_face": "POST /api/v1/verify-face"
        }
    }

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
    validation_error = await validate_uploaded_image(image)
    if validation_error:
        return validation_error

    auth_result = verify_api_key_plain(authorization)

    # If auth failed → response engine returned
    if isinstance(auth_result, dict) and auth_result.get("response") == "error":
        return auth_result

    # Token valid → continue
    return await verify_face_image(image)

# ================= Global Exception Handler =================
app.add_exception_handler(RequestValidationError, validation_exception_handler)
