# 📸 Image Verification Service - Professional ID Photo Validator

A production-ready **FastAPI microservice** for comprehensive face and ID photo verification. Ensures uploaded images meet formal standards for passport, driving license, and official ID applications.

---

## 🎯 What Does It Do?

When you upload an image, this service performs **11 professional verification checks** to ensure:

✅ **Exactly 1 human face** present (front-facing)  
✅ **Eyes are open and visible**  
✅ **Image is clear** (not blurry)  
✅ **Proper lighting** (not too dark/bright)  
✅ **Clean background** (no clutter or objects)  
✅ **Background color is uniform** (single color)  
✅ **Face size is correct** (15-45% of image)  
✅ **No text/watermarks** visible  
✅ **No extra people** in frame  
✅ **No objects/items** (phone, pen, etc.)  
✅ **Hands not covering face**  

Returns a **score out of 11** - image passes if score ≥ 8.

---

## 🚀 Quick Start

### **1️⃣ Prerequisites**

- Python 3.10+ 
- Docker (optional, for containerized deployment)
- Tesseract OCR (for text detection)

### **2️⃣ Installation**

```bash
# Clone repository
git clone <repo-url>
cd image-verification-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3️⃣ Install Tesseract (Windows)**

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH (or it's auto-detected)

**On Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### **4️⃣ Run Locally**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: **http://localhost:8000/docs** (Swagger UI)

### **5️⃣ Run with Docker**

```bash
docker compose up --build
```

---

## 📡 API Endpoints

### **1. Get Authentication Token**

```bash
POST /api/v1/get-token
Content-Type: application/json

{
  "username": "test_user",
  "password": "test_password"
}
```

**Response:**
```json
{
  "response": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### **2. Verify Face Image** ⭐ Main Endpoint

```bash
POST /api/v1/verify-face
Authorization: Bearer <token>
Content-Type: multipart/form-data

image: <file.jpg>
```

**Success Response (200):**
```json
{
  "responseTime": 1768902705,
  "responseType": "FACE_VERIFY",
  "status": 200,
  "response": "success",
  "msg": "Face verification completed",
  "data": {
    "image_status": "passed",
    "score": 11,
    "max_score": 11,
    "details": {
      "face": {
        "face_detected": true,
        "face_count": 1
      },
      "eyes": {
        "eyes_detected": true
      },
      "quality": {
        "blur_score": 549.4,
        "is_blurry": false
      },
      "pose": {
        "head_pose": "frontal"
      },
      "lighting": {
        "brightness": 106.2,
        "lighting": "good"
      },
      "background": {
        "edge_ratio": 0.019,
        "background_ok": true
      },
      "geometry": {
        "geometry_ok": true
      },
      "text": {
        "text_detected": false,
        "text_ok": true
      },
      "background_uniform": {
        "status": "PASS"
      },
      "object_detector": {
        "non_human_object_present": false,
        "detected_objects": []
      },
      "human_only": {
        "status": "PASS"
      },
      "hands": {
        "is_ok": true,
        "hands_detected": false
      }
    }
  }
}
```

**Failure Response (500):**
```json
{
  "status": 500,
  "response": "error",
  "msg": "Face verification failed",
  "data": {
    "error": "No face detected in image"
  }
}
```

---

## 📊 Verification Checks Explained

| Check | What It Does | Pass Criteria |
|-------|-------------|--------------|
| **Face Detection** | Detects human faces | Exactly 1 face |
| **Eye Detection** | Checks if eyes are visible | Both eyes open |
| **Quality** | Detects blur | Blur score > 100 |
| **Head Pose** | Checks face direction | Front-facing |
| **Lighting** | Analyzes brightness | 70-190 brightness |
| **Background Edges** | Detects clutter | Edge ratio < 5% |
| **Face Geometry** | Validates face size/position | 15-45% of image |
| **Text Detection** | Finds watermarks/text | Text < 6% area |
| **Background Uniform** | Checks color uniformity | Single main color |
| **Object Detector** | Finds extra objects | No non-human objects |
| **Hand Detection** | Checks for hand occlusion | Hands not covering face |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      CLIENT REQUEST (Image)         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   JWT AUTHENTICATION (Token)        │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│    IMAGE VERIFICATION PIPELINE      │
│   (11 parallel verification checks) │
└────────────────┬────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────────┐
│ CV2/   │  │MediaPipe│  │ YOLO/     │
│Cascades│  │Face    │  │ Tesseract  │
│        │  │Mesh    │  │            │
└────────┘  └────────┘  └────────────┘
    │            │            │
    └────────────┼────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      SCORING & VALIDATION           │
│    (Score all checks, aggregate)    │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ PASS (≥8/11)    │
        │ or              │
        │ FAIL (<8/11)    │
        └────────────────┘
```

---

## 📁 Project Structure

```
image-verification-service/
├── app/
│   ├── main.py                              # FastAPI app & routes
│   ├── controllers/
│   │   ├── auth_controller.py               # Token generation
│   │   └── face_verification_controller.py  # Main verification logic
│   ├── utils/
│   │   ├── response.py                      # Response formatter
│   │   ├── security.py                      # JWT validation
│   │   ├── json_safe.py                     # JSON serialization
│   │   └── exception_handler.py             # Error handling
│   └── verifier/
│       ├── face_detector.py                 # Haar Cascade face detection
│       ├── eye_checker.py                   # Eye detection
│       ├── quality_checker.py               # Blur detection (Laplacian)
│       ├── pose_checker.py                  # Head pose (MediaPipe)
│       ├── lighting_checker.py              # Brightness analysis
│       ├── background_checker.py            # Edge ratio detection
│       ├── geometry_checker.py              # Face size & position
│       ├── text_checker.py                  # OCR (Tesseract)
│       ├── background_uniform_checker.py    # Color uniformity (KMeans)
│       ├── object_detector.py               # YOLO object detection
│       ├── human_only_detector.py           # YOLO person detection
│       ├── hand_detector.py                 # MediaPipe hand detection
│       └── response_builder.py              # Score aggregation
├── Dockerfile                               # Production image
├── docker-compose.yml                       # Development setup
├── requirements.txt                         # Python dependencies
└── README.md                                # This file
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | REST API framework |
| **OpenCV** | Image processing & face detection |
| **MediaPipe** | Head pose & hand detection |
| **YOLO (YOLOv8)** | Object & person detection |
| **Tesseract OCR** | Text/watermark detection |
| **scikit-learn** | Background color clustering |
| **Uvicorn** | ASGI server |
| **Docker** | Containerization |
| **JWT (PyJWT)** | Token authentication |

---

## ⚙️ Configuration

### Passing Score (Adjustable)

Edit in [response_builder.py](app/verifier/response_builder.py):
```python
passing_threshold = 8  # Change this (out of 11)
```

### Quality Thresholds

- **Blur detection**: blur_score > 100
- **Brightness**: 70-190
- **Edge ratio**: < 5%
- **Face size**: 15-45% of image
- **Text area**: < 6%

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Response Time | ~2-2.5 seconds |
| Parallel Processing | Yes (11 checks) |
| CPU Usage | ~80-90% (first request) |
| Memory | ~500MB-1GB |
| Accuracy | ~95% for formal images |

---

## 🔐 Security

- ✅ JWT token-based authentication
- ✅ Input validation (file type, size)
- ✅ Error handling (no sensitive data leaked)
- ✅ CORS support (configurable)

---

## 🐛 Common Issues & Solutions

### Issue: "Numpy is not available"
**Solution:** Models are lazy-loaded. Ensure torch/numpy are installed.
```bash
pip install numpy>=1.24.0,<2.0
```

### Issue: "Tesseract not found"
**Solution:** Install Tesseract or set path:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Issue: "YOLO model download timeout"
**Solution:** Download manually or set cache:
```bash
yolo export model=yolov8n.pt format=pt
```

---

## 📚 Usage Examples

### Python Client

```python
import requests

# Get token
token_response = requests.post(
    "http://localhost:8000/api/v1/get-token",
    json={"username": "test_user", "password": "test_password"}
)
token = token_response.json()["data"]["token"]

# Verify image
with open("photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/verify-face",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": f}
    )
    result = response.json()
    print(f"Status: {result['data']['image_status']}")
    print(f"Score: {result['data']['score']}/{result['data']['max_score']}")
```

### cURL

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/get-token \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}' | jq -r '.data.token')

# Verify image
curl -X POST http://localhost:8000/api/v1/verify-face \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@photo.jpg"
```

---

## 📝 License

MIT License - feel free to use in commercial projects

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Submit pull request

---

## 📞 Support

Issues or questions? Open an issue on GitHub or contact the maintainers.

---

**Created with ❤️ for professional ID verification**
