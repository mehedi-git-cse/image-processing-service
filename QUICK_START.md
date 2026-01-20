# 🚀 Quick Start Guide

Get the Image Verification Service running in 5 minutes!

---

## **Option 1: Docker (Easiest - Recommended)**

```bash
# 1. Clone repository
git clone <repo-url>
cd image-verification-service

# 2. Start with Docker Compose
docker compose up --build

# 3. Service is running at: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

That's it! ✅

---

## **Option 2: Local Python Setup**

### **Prerequisites**
- Python 3.10+
- Tesseract OCR (for text detection)

### **Step-by-Step**

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Tesseract (Choose your OS)

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use Chocolatey: choco install tesseract

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# 4. Run the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Open browser: http://localhost:8000/docs
```

---

## **Testing the API**

### **Using Swagger UI (Web Interface)**

1. Go to: **http://localhost:8000/docs**
2. Click on `POST /api/v1/get-token`
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "username": "test_user",
     "password": "test_password"
   }
   ```
5. Click "Execute" → Copy the token
6. Now test `/api/v1/verify-face`:
   - Click on `POST /api/v1/verify-face`
   - Click "Try it out"
   - Click "Authorize" (lock icon) → Paste token
   - Upload an image → Execute

### **Using Python**

```python
import requests

# Get token
response = requests.post(
    "http://localhost:8000/api/v1/get-token",
    json={"username": "test_user", "password": "test_password"}
)
token = response.json()["data"]["token"]

# Verify image
with open("your_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/verify-face",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": f}
    )
    result = response.json()
    
    print(f"Status: {result['data']['image_status']}")
    print(f"Score: {result['data']['score']}/11")
    print(f"Details: {result['data']['details']}")
```

### **Using cURL**

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/get-token \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}' \
  | jq -r '.data.token')

# Verify image
curl -X POST http://localhost:8000/api/v1/verify-face \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test_image.jpg"
```

---

## **Understanding the Response**

### **Successful Verification (PASSED)**

```json
{
  "status": 200,
  "response": "success",
  "data": {
    "image_status": "passed",
    "score": 11,
    "max_score": 11,
    "details": {
      "face": {"face_detected": true, "face_count": 1},
      "eyes": {"eyes_detected": true},
      "quality": {"is_blurry": false},
      "pose": {"head_pose": "frontal"},
      "lighting": {"lighting": "good"},
      "background": {"background_ok": true},
      "geometry": {"geometry_ok": true},
      "text": {"text_ok": true},
      "background_uniform": {"status": "PASS"},
      "object_detector": {"non_human_object_present": false},
      "human_only": {"status": "PASS"},
      "hands": {"is_ok": true}
    }
  }
}
```

✅ **Image PASSED** (score 11/11)

---

### **Verification FAILED**

```json
{
  "status": 200,
  "response": "success",
  "data": {
    "image_status": "failed",
    "score": 5,
    "max_score": 11,
    "details": {
      "face": {"face_detected": false, "face_count": 0},
      "eyes": {"eyes_detected": false},
      "quality": {"is_blurry": true},
      ...
    }
  }
}
```

❌ **Image FAILED** (score 5/11 - below threshold of 8)

---

## **Common Test Cases**

### **Test 1: Perfect ID Photo** ✅
- Single person, front-facing
- Clear and bright
- Plain background
- No objects or text
- **Expected Result**: PASS (11/11)

### **Test 2: Selfie with Background** ⚠️
- Person visible, but background has objects
- Good lighting
- **Expected Result**: FAIL (7/11) - objects detected

### **Test 3: Blurry Image** ❌
- Face detected but very blurry
- **Expected Result**: FAIL (quality check fails)

### **Test 4: Two People** ❌
- Two faces in image
- **Expected Result**: FAIL (face count != 1)

---

## **Troubleshooting**

### ❌ "Port 8000 already in use"
```bash
# Use different port
uvicorn app.main:app --port 8001
```

### ❌ "Tesseract not found"
```bash
# Set tesseract path in code or system PATH
export PATH="/usr/bin:$PATH"  # Linux/Mac
set PATH=C:\Program Files\Tesseract-OCR;%PATH%  # Windows
```

### ❌ "YOLO model download failed"
```bash
# Pre-download models
yolo export model=yolov8n.pt format=pt
yolo export model=yolov8n-seg.pt format=pt
```

### ❌ "Container exits immediately"
```bash
# Check logs
docker compose logs image-verification-service

# Rebuild
docker compose down
docker compose up --build
```

---

## **Next Steps**

1. **Read Full Documentation**: See [README.md](README_UPDATED.md)
2. **Understand Architecture**: See [ARCHITECTURE.md](ARCHITECTURE_UPDATED.md)
3. **Configure Thresholds**: Edit individual checkers in `app/verifier/`
4. **Deploy to Production**: Use Docker or cloud platform
5. **Integrate with Your App**: Use the Python/cURL examples above

---

## **Key Files**

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app & routes |
| `app/controllers/face_verification_controller.py` | Main verification logic |
| `app/verifier/` | All 11 verification checks |
| `docker-compose.yml` | Local development setup |
| `requirements.txt` | Python dependencies |

---

**Ready to verify images? Start with:** `docker compose up --build` 🚀
