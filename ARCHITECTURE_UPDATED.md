# 🏗️ Image Verification Service - Complete Architecture

A comprehensive guide to understand how the Image Verification Service works.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Verification Pipeline](#verification-pipeline)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [Scoring System](#scoring-system)

---

## 🎯 Overview

**Purpose**: Validate that uploaded images are suitable for official ID/passport use

**Key Features**:
- 11 independent verification checks
- Parallel processing (all checks run simultaneously)
- Score-based decision (pass if score ≥ 8/11)
- JWT-based authentication
- Production-ready with Docker support

---

## 🏗️ System Architecture

```
                          ┌─────────────────────┐
                          │   CLIENT REQUEST    │
                          │  (Image + Token)    │
                          └──────────┬──────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │   AUTHENTICATION LAYER          │
                    │  (JWT Token Verification)       │
                    │  - Verify token signature       │
                    │  - Check expiration             │
                    └────────────────┬─────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │  IMAGE PROCESSING LAYER         │
                    │  (Input Validation)             │
                    │  - File format check (JPG/PNG)  │
                    │  - File size validation         │
                    └────────────────┬─────────────────┘
                                     │
        ┌────────────────────────────▼────────────────────────────┐
        │                                                          │
        │   PARALLEL VERIFICATION CHECKS (All run simultaneously) │
        │                                                          │
        └────────────────────────────▼────────────────────────────┘
                                     │
        ┌────────────────────────────┴────────────────────────────┐
        │                                                          │
    ┌───▼───┐  ┌───────┐  ┌────────┐  ┌──────┐  ┌────────┐      │
    │ Face  │  │ Eyes  │  │Quality │  │Pose  │  │Lighting│      │
    │Detect │  │Detect │  │ Check  │  │Check │  │ Check  │      │
    └───┬───┘  └───┬───┘  └────┬───┘  └──┬───┘  └────┬───┘      │
        │          │           │         │           │           │
    ┌───▼───┐  ┌───▼───┐  ┌───▼────┐  ┌▼──────┐  ┌──▼──────┐   │
    │ BG    │  │Text   │  │ BG     │  │Object │  │Human    │   │
    │Check  │  │OCR    │  │ Uniform│  │Detector   │Detector │   │
    │       │  │       │  │ Check  │  │       │  │         │   │
    └───┬───┘  └───┬───┘  └───┬────┘  └──┬────┘  └────┬────┘   │
        │          │           │         │           │           │
        │      ┌───▼───┐       │         │           │           │
        │      │ Hands │       │         │           │           │
        │      │Detect │       │         │           │           │
        │      └───┬───┘       │         │           │           │
        └─────────▼─────────────────────────────────────┘        │
                                     │
        ┌────────────────────────────▼────────────────────────────┐
        │  SCORING & DECISION ENGINE (response_builder.py)        │
        │  - Aggregate all check results                          │
        │  - Calculate total score (max 11)                       │
        │  - Apply passing threshold (≥8)                         │
        └────────────────────────────┬────────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │   FORMAT RESPONSE                │
                    │  - JSON with details             │
                    │  - Include all check results     │
                    │  - Add timing information        │
                    └────────────────┬─────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │   RETURN RESPONSE                │
                    │  (HTTP 200 or 500)               │
                    └──────────────────────────────────┘
```

---

## 🔄 Verification Pipeline

### **Complete Flow**

```
IMAGE UPLOAD
    │
    ├─ 1️⃣  FACE DETECTION (face_detector.py)
    │   └─ Uses: OpenCV Haar Cascade
    │   └─ Checks: Exactly 1 face present
    │   └─ Output: {face_detected: bool, face_count: int}
    │
    ├─ 2️⃣  EYE DETECTION (eye_checker.py)
    │   └─ Uses: OpenCV Haar Cascade (eye detector)
    │   └─ Checks: Both eyes visible and open
    │   └─ Output: {eyes_detected: bool}
    │
    ├─ 3️⃣  QUALITY CHECK (quality_checker.py)
    │   └─ Uses: Laplacian variance (blur detection)
    │   └─ Checks: Image not blurry (blur_score > 100)
    │   └─ Output: {blur_score: float, is_blurry: bool}
    │
    ├─ 4️⃣  HEAD POSE (pose_checker.py)
    │   └─ Uses: MediaPipe Face Mesh
    │   └─ Checks: Head is front-facing (yaw < 0.03)
    │   └─ Output: {head_pose: "frontal" | "turned"}
    │
    ├─ 5️⃣  LIGHTING CHECK (lighting_checker.py)
    │   └─ Uses: Mean brightness calculation
    │   └─ Checks: Brightness in 70-190 range
    │   └─ Output: {brightness: float, lighting: "good" | "too_dark" | "too_bright"}
    │
    ├─ 6️⃣  BACKGROUND CHECK (background_checker.py)
    │   └─ Uses: Canny edge detection
    │   └─ Checks: Edge ratio < 5% (clean background)
    │   └─ Output: {edge_ratio: float, background_ok: bool}
    │
    ├─ 7️⃣  GEOMETRY CHECK (geometry_checker.py)
    │   └─ Uses: Face bounding box analysis
    │   └─ Checks: Face 15-45% of image, centered
    │   └─ Output: {geometry_ok: bool}
    │
    ├─ 8️⃣  TEXT DETECTION (text_checker.py)
    │   └─ Uses: Tesseract OCR
    │   └─ Checks: No watermarks/text (< 6% area)
    │   └─ Output: {text_detected: bool, text_area_ratio: float}
    │
    ├─ 9️⃣  BACKGROUND UNIFORM (background_uniform_checker.py)
    │   └─ Uses: KMeans color clustering
    │   └─ Checks: Background is single uniform color
    │   └─ Output: {status: "PASS" | "FAIL"}
    │
    ├─ 🔟 OBJECT DETECTION (object_detector.py)
    │   └─ Uses: YOLOv8 segmentation
    │   └─ Checks: No non-human objects
    │   └─ Output: {non_human_object_present: bool, detected_objects: list}
    │
    └─ 1️⃣1️⃣ HAND DETECTION (hand_detector.py)
        └─ Uses: MediaPipe Hand Detection
        └─ Checks: Hands not covering face
        └─ Output: {hands_detected: bool, is_ok: bool}
    
    │
    ▼
AGGREGATE RESULTS (response_builder.py)
    │
    ├─ Sum all passed checks (each check = 1 point)
    ├─ Max score: 11
    ├─ Passing threshold: 8
    │
    ▼
DECISION
    ├─ score ≥ 8 → image_status = "PASSED" ✅
    └─ score < 8 → image_status = "FAILED" ❌
```

---

## 🔧 Component Details

### **1. Face Detector**
```
File: app/verifier/face_detector.py
Algorithm: OpenCV Haar Cascade Classifier
Input: Image bytes
Output: {face_detected, face_count}
Speed: ~50ms
Purpose: Ensure exactly 1 person in image
```

### **2. Eye Checker**
```
File: app/verifier/eye_checker.py
Algorithm: OpenCV Haar Cascade (eye detector)
Input: Image bytes
Output: {eyes_detected}
Speed: ~50ms
Purpose: Verify both eyes are visible
```

### **3. Quality Checker**
```
File: app/verifier/quality_checker.py
Algorithm: Laplacian variance (blur detection)
Input: Image bytes
Output: {blur_score, is_blurry}
Speed: ~20ms
Purpose: Reject blurry images
Threshold: blur_score > 100
```

### **4. Head Pose Detector**
```
File: app/verifier/pose_checker.py
Algorithm: MediaPipe Face Mesh (468 landmarks)
Input: Image bytes
Output: {head_pose}
Speed: ~100ms
Purpose: Ensure front-facing pose
Threshold: yaw < 0.03
```

### **5. Lighting Checker**
```
File: app/verifier/lighting_checker.py
Algorithm: Mean brightness calculation
Input: Image bytes
Output: {brightness, lighting}
Speed: ~20ms
Purpose: Validate proper lighting
Range: 70-190
```

### **6. Background Checker**
```
File: app/verifier/background_checker.py
Algorithm: Canny edge detection
Input: Image bytes
Output: {edge_ratio, background_ok}
Speed: ~50ms
Purpose: Detect background clutter
Threshold: edge_ratio < 5%
```

### **7. Geometry Checker**
```
File: app/verifier/geometry_checker.py
Algorithm: Bounding box analysis
Input: Image bytes
Output: {geometry_ok}
Speed: ~50ms
Purpose: Validate face size and centering
Rules:
  - Face area: 15-45% of image
  - Horizontal offset: < 15%
  - Vertical offset: < 15%
```

### **8. Text Checker (OCR)**
```
File: app/verifier/text_checker.py
Algorithm: Tesseract OCR
Input: Image bytes
Output: {text_detected, text_area_ratio, text_ok}
Speed: ~200-300ms
Purpose: Find watermarks/text overlays
Threshold: text_area < 6%
```

### **9. Background Uniform Checker**
```
File: app/verifier/background_uniform_checker.py
Algorithm: KMeans clustering (color analysis)
Input: Image bytes
Output: {status}
Speed: ~100ms
Purpose: Ensure single-color background
Method: Extract background, cluster colors, check uniformity
```

### **10. Object Detector (YOLO)**
```
File: app/verifier/object_detector.py
Algorithm: YOLOv8 segmentation
Input: Image bytes
Output: {non_human_object_present, detected_objects}
Speed: ~800-1000ms (YOLO inference)
Purpose: Detect non-human objects
Model: yolov8n-seg.pt (nano, CPU optimized)
COCO Classes: 80 object types
```

### **11. Human-Only Detector**
```
File: app/verifier/human_only_detector.py
Algorithm: YOLOv8 object detection
Input: Image bytes
Output: {status, objects}
Speed: ~600-800ms (YOLO inference)
Purpose: Ensure only 1 person, count verification
Model: yolov8n.pt (nano, CPU optimized)
Logic: Must detect exactly 1 "person" class
```

### **12. Hand Detector**
```
File: app/verifier/hand_detector.py
Algorithm: MediaPipe Hand Detection
Input: Image bytes
Output: {hands_detected, hand_position, is_ok}
Speed: ~100ms
Purpose: Check hands not covering face
Positions: "covering_face" | "near_face" | "visible" | "not_visible"
Logic: Reject if hands cover face region
```

---

## 📊 Data Flow

### **Request Flow**

```
CLIENT
  │
  ├─ POST /api/v1/get-token
  │  └─ body: {username, password}
  │  └─ response: {token}
  │
  └─ POST /api/v1/verify-face
     ├─ header: Authorization: Bearer <token>
     ├─ body: multipart/form-data {image}
     │
     ▼ (on server)
     
     1. Extract token from header
     2. Validate token (JWT)
     3. Read image bytes
     4. Validate image format
     5. Run 11 parallel checks
     6. Aggregate results
     7. Format response
     8. Return JSON
```

### **Response Flow**

```
{
  "responseTime": <unix_timestamp>,
  "responseType": "FACE_VERIFY",
  "status": 200 or 500,
  "response": "success" or "error",
  "msg": "Human readable message",
  "data": {
    "image_status": "passed" or "failed",
    "score": <0-11>,
    "max_score": 11,
    "details": {
      "face": {...},
      "eyes": {...},
      "quality": {...},
      "pose": {...},
      "lighting": {...},
      "background": {...},
      "geometry": {...},
      "text": {...},
      "background_uniform": {...},
      "object_detector": {...},
      "human_only": {...},
      "hands": {...}
    }
  }
}
```

---

## 🎯 Scoring System

### **Point Distribution**

| Check | Points | Condition |
|-------|--------|-----------|
| Face Detection | 1 | face_detected == true |
| Eye Detection | 1 | eyes_detected == true |
| Quality | 1 | is_blurry == false |
| Head Pose | 1 | head_pose in ["frontal", "slightly_turned", "turned"] |
| Lighting | 1 | lighting == "good" |
| Background | 1 | background_ok == true |
| Geometry | 1 | geometry_ok == true |
| Text | 1 | text_ok == true |
| Background Uniform | 1 | status == "PASS" |
| Object Detector | 1 | non_human_object_present == false |
| Hand Detection | 1 | is_ok == true |

### **Total: 11 Points Maximum**

### **Passing Logic**

```python
score = sum of all passed checks
passing_threshold = 8

if score >= 8:
    image_status = "PASSED"  ✅
else:
    image_status = "FAILED"  ❌
```

### **Example Scenarios**

| Score | Status | Reason |
|-------|--------|--------|
| 11/11 | ✅ PASS | Perfect image |
| 10/11 | ✅ PASS | Minor issue (e.g., slight blur) |
| 8/11  | ✅ PASS | Minimal requirements met |
| 7/11  | ❌ FAIL | Below threshold |
| 0/11  | ❌ FAIL | No face detected |

---

## ⚡ Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Total Response Time | 2-2.5s | With YOLO models |
| Fast Response (no YOLO) | 0.5-1s | Without object/human detection |
| Face Detection | ~50ms | Haar Cascade |
| MediaPipe Operations | ~100-150ms | Pose + Hands |
| YOLO Inference | ~800-1000ms | Segmentation model |
| Tesseract OCR | ~200-300ms | Text detection |
| Memory Usage | ~500MB-1GB | With all models loaded |
| Concurrency | Unlimited | AsyncIO support |

---

## 🔒 Security

- **Authentication**: JWT tokens with configurable expiration
- **Input Validation**: File type, size, and format checks
- **Error Handling**: No sensitive data in error messages
- **Rate Limiting**: Can be added via middleware
- **CORS**: Configurable cross-origin requests

---

## 📈 Optimization Tips

1. **For Speed**: Disable YOLO models if not needed
2. **For Accuracy**: Increase passing threshold to 9+
3. **For Flexibility**: Adjust individual thresholds in each checker
4. **For Scale**: Use load balancer with multiple instances

---

## 🚀 Deployment

### **Docker (Recommended)**
```bash
docker compose up --build
```

### **Manual (Local)**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Production (Gunicorn + Uvicorn)**
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

**Architecture Designed for Professional-Grade ID Photo Verification** ✅
