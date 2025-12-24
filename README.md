# Image Verification Service 🔍

**Image Verification Service** is a FastAPI microservice that provides face verification checks on uploaded images. It includes a simple token-based authentication endpoint and a face verification endpoint that runs a set of checks (face detection, eye check, lighting, background, pose, quality, geometry) and returns a structured JSON result.

---

## ✅ Features

- Token-based authentication (JWT)
- Face verification endpoint that accepts multipart image uploads
- Multiple verification checks (face detection, eyes, lighting, background, head pose, quality, geometry)
- Simple, consistent response format for both success and error
- Runs with Uvicorn and ships a Dockerfile for containerized deployment

---

## 🔧 Requirements

- Python 3.11 (project uses `python:3.11-slim` in Dockerfile)
- See `requirements.txt` for Python dependencies:
  - fastapi, uvicorn, opencv-python, mediapipe, numpy, pillow, python-multipart, pyjwt

---

## 🚀 Quickstart (local)

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

1️⃣ Install Tesseract OCR

Download the installer from: https://github.com/tesseract-ocr/tesseract
https://github.com/UB-Mannheim/tesseract/wiki
 → Go to Windows release section.
 Video for setup in windows mechine 
 https://www.youtube.com/watch?v=2kWvk4C1pMo

Install it, e.g., in:

C:\Program Files\Tesseract-OCR


Make sure tesseract.exe exists in that folder.

2️⃣ Add Tesseract to your PATH (optional but recommended)

Open Environment Variables → Edit Path → Add:

C:\Program Files\Tesseract-OCR


Restart your terminal/IDE.

3️⃣ Specify Tesseract path in your code (safer)
import pytesseract

# Set the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


3. Run the app with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

---

## 🐳 Docker

Run with Docker Compose (recommended for development — mounts local code and enables live reload):

```bash
# First run (build required)
docker compose up --build
# Afterwards you can start without rebuilding:
docker compose up
```

The compose file mounts your project into the container and runs Uvicorn with `--reload`, so changes to code are picked up automatically. The API will be available at: http://localhost:7000

Alternate: classic Docker build and run (if you prefer):

```bash
docker build -t image-verification-service .
docker run -p 7000:8000 image-verification-service
```

---

## 🔐 Authentication

- Obtain a token with the auth endpoint (see below) and include it in the `Authorization` header in the format: `Bearer <token>`.
- Default token generation credentials are defined in `app/controllers/auth_controller.py` (for development):
  - `client_id`: `image-8989`
  - `client_secret`: `atik-check-8888`
- Secret key used to sign tokens: `app/utils/security.py` → `SECRET_KEY`. Edit the file to change the value for production.

---

## 📡 API Endpoints

### 1) Generate Token

- URL: `POST /api/v1/get-token`
- Body (JSON):

```json
{
  "client_id": "image-8989",
  "client_secret": "atik-check-8888"
}
```

- Response: standard response object with `data.access_token` and `data.token_type`

Example (curl):

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/get-token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"image-8989","client_secret":"atik-check-8888"}'
```

### 2) Verify Face

- URL: `POST /api/v1/verify-face`
- Headers: `Authorization: Bearer <access_token>`
- Body: `multipart/form-data` with key `image` (file)

Example (curl):

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/verify-face \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "image=@/path/to/image.jpg"
```

- Response: structured JSON with results from each verifier. On validation/auth errors the service returns consistent error responses.

---

## 🧠 Response Format

All responses follow the same pattern defined in `app/utils/response.py`:

```json
{
  "responseTime": 1670000000,
  "responseType": "FACE_VERIFY|AUTH|VALIDATION",
  "status": 200,
  "response": "success|error",
  "msg": "Human readable message",
  "data": { /* response-specific payload */ }
}
```

---

## 🧩 Notes & Internals

- Main routes are in `app/main.py`.
- Auth logic is in `app/controllers/auth_controller.py` and uses `pyjwt` to sign tokens.
- Face verification logic is implemented by orchestrating smaller checks in `app/verifier/*.py` with `app/controllers/face_verification_controller.py` exposed as an endpoint.
- Utility helpers for responses and error handling live in `app/utils/`.

---

## ✅ Development Tips

- Update `SECRET_KEY` before deploying to production.
- Consider moving credentials and secrets to environment variables or a secrets manager.
- Add unit and integration tests for the verifier modules and controllers.

---

## ✨ Contribution

Contributions are welcome — please open issues or PRs for bug fixes and improvements.

---

If you'd like, I can also add a short example script that requests a token and calls the `verify-face` endpoint automatically. Want me to add that? 💡
