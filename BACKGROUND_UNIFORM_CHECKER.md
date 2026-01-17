# Background Uniform Color Checker - Documentation

## Overview

The **background_uniform_checker** module adds a new verification check to ensure that ID/passport photos have a clean, uniform background without objects, patterns, or multiple colors.

---

## Purpose

Official ID photos (passport, KYC, driver's license) must have:
- ✅ Single solid color background (white, light blue, light gray, etc.)
- ✅ No objects, furniture, or people in background
- ✅ No patterns, textures, or wallpaper
- ✅ No shadows or gradients
- ✅ Professional studio-quality background

---

## How It Works

### Algorithm Steps

1. **Face Detection**
   - Detects face using Haar Cascade
   - Creates a mask with expanded boundary (±20%) to include hair/ears
   - Excludes face region from background analysis

2. **Background Pixel Extraction**
   - Extracts all non-face pixels
   - Converts to flat array for analysis

3. **Color Uniformity Analysis**
   - Uses **KMeans clustering** to find dominant colors
   - Calculates **standard deviation** of pixel values
   - Checks if only 1-2 colors dominate (allows slight variation)

4. **Object Detection**
   - Applies **Canny edge detection** on background
   - Masks out face region
   - Calculates **edge density ratio**
   - High edge density = objects/patterns present

5. **Pass/Fail Decision**
   - **PASS** if:
     - ≤ 2 dominant colors
     - Edge density < 3%
     - Color std < 30.0
   - **FAIL** if any criterion fails

---

## Function Signature

```python
def check_background_uniform_color(
    image_bytes: bytes,
    max_colors: int = 2,
    edge_density_threshold: float = 0.03,
    color_std_threshold: float = 30.0
) -> dict
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_bytes` | bytes | Required | Image data in bytes format |
| `max_colors` | int | 2 | Maximum allowed dominant colors |
| `edge_density_threshold` | float | 0.03 | Max edge density (3%) |
| `color_std_threshold` | float | 30.0 | Max color standard deviation |

### Return Value

```python
{
    "background_uniform": bool,      # True if passed, False if failed
    "dominant_colors": int,           # Number of dominant color clusters
    "edge_density": float,            # Edge density ratio (0.0 to 1.0)
    "color_std": float,               # Standard deviation of pixel values
    "reason": str                     # Human-readable explanation
}
```

---

## Example Responses

### ✅ Pass Example (Clean White Background)

```json
{
  "background_uniform": true,
  "dominant_colors": 1,
  "edge_density": 0.0087,
  "color_std": 12.34,
  "reason": "Background is uniform single color (PASS)"
}
```

### ❌ Fail Example (Multiple Colors)

```json
{
  "background_uniform": false,
  "dominant_colors": 4,
  "edge_density": 0.0156,
  "color_std": 45.67,
  "reason": "Background not uniform: Multiple colors detected (4 dominant colors); Non-uniform color (variation: 45.7)"
}
```

### ❌ Fail Example (Objects Detected)

```json
{
  "background_uniform": false,
  "dominant_colors": 2,
  "edge_density": 0.0823,
  "color_std": 28.91,
  "reason": "Background not uniform: Objects/patterns detected (edge density: 0.082)"
}
```

---

## Integration

### 1. Import the Module

```python
from app.verifier.background_uniform_checker import check_background_uniform_color
```

### 2. Call in Verification Pipeline

```python
# In face_verification_controller.py
result = build_response(
    detect_face(img),
    check_eyes(img),
    check_quality(img),
    check_head_pose(img),
    check_lighting(img),
    check_background(img),
    check_face_geometry(img),
    check_text_presence(img),
    check_background_uniform_color(img)  # NEW CHECK
)
```

### 3. Update Scoring System

The `build_response()` function now scores out of **9 points** (previously 8):
- Minimum passing score: **7/9**
- Each check contributes 1 point if passed

---

## Technical Details

### Libraries Used

- **OpenCV (cv2)**: Image processing, face detection, edge detection
- **NumPy**: Array operations, statistical analysis
- **scikit-learn**: KMeans clustering for color analysis

### Face Detection Method

- **Haar Cascade Classifier**: `haarcascade_frontalface_default.xml`
- **Expansion**: Face bounding box expanded by 20% to include hair/ears
- **Purpose**: Ensures background analysis doesn't include person's features

### Color Clustering

- **Algorithm**: KMeans with 5 clusters
- **Sampling**: Max 5000 pixels (for performance)
- **Threshold**: Only clusters representing >5% of image are counted

### Edge Detection

- **Preprocessing**: Gaussian blur (5x5) to reduce noise
- **Algorithm**: Canny edge detection (thresholds: 50, 150)
- **Masking**: Face region excluded from edge calculation

---

## Tuning Parameters

You can adjust thresholds for stricter/looser checks:

### Strict Mode (Professional Studio Quality)

```python
check_background_uniform_color(
    image_bytes,
    max_colors=1,              # Only 1 color allowed
    edge_density_threshold=0.02,  # 2% max edges
    color_std_threshold=20.0   # Very low variation
)
```

### Lenient Mode (Consumer Photos)

```python
check_background_uniform_color(
    image_bytes,
    max_colors=3,              # Up to 3 colors
    edge_density_threshold=0.05,  # 5% max edges
    color_std_threshold=40.0   # Higher variation allowed
)
```

---

## Testing

Run the test suite to verify functionality:

```bash
python test_background_uniform.py
```

This creates 5 synthetic test images:
1. ✅ Uniform white background (PASS)
2. ✅ Uniform light blue background (PASS)
3. ❌ Gradient background (FAIL)
4. ❌ Background with objects (FAIL)
5. ❌ Multi-color background (FAIL)

---

## Common Failure Scenarios

| Scenario | Detection Method | Example |
|----------|------------------|---------|
| Multiple colors | KMeans clustering | Pink + green background |
| Gradient | Color std deviation | White → gray fade |
| Objects/furniture | Edge density | Chair, plants, picture frames |
| Patterns/wallpaper | Edge density | Striped walls, textured surfaces |
| Shadows | Color std + edges | Person's shadow on wall |
| Clutter | Edge density + colors | Messy room background |

---

## Performance Considerations

- **Image Sampling**: KMeans uses max 5000 pixels for speed
- **Face Mask**: Reduces pixels analyzed (focuses on background)
- **Typical Runtime**: < 100ms per image on modern hardware
- **No External Dependencies**: Works offline (no API calls)

---

## Error Handling

The function handles common errors gracefully:

```python
# Invalid image
{
  "background_uniform": False,
  "reason": "Failed to decode image"
}

# No background (face fills entire image)
{
  "background_uniform": False,
  "reason": "No background pixels found (face occupies entire image)"
}

# Unexpected errors
{
  "background_uniform": False,
  "reason": "Error during background check: [error message]"
}
```

---

## Best Practices

1. **Use with other checks**: This check complements (not replaces) existing background_checker
2. **Adjust thresholds**: Tune parameters based on your use case
3. **Test with real photos**: Validate with actual ID photos from your domain
4. **Monitor false positives**: Some legitimate photos may fail (e.g., very light skin + white background)
5. **Provide feedback**: Return detailed `reason` to help users fix issues

---

## API Response Example

Full API response including the new check:

```json
{
  "responseTime": 1737158400,
  "responseType": "FACE_VERIFY",
  "status": 200,
  "response": "success",
  "msg": "Face verification completed",
  "data": {
    "image_status": "passed",
    "score": 8,
    "max_score": 9,
    "details": {
      "face": {"face_detected": true, "face_count": 1},
      "eyes": {"eyes_detected": true},
      "quality": {"blur_score": 234.56, "is_blurry": false},
      "pose": {"head_pose": "frontal"},
      "lighting": {"brightness": 145.2, "lighting": "good"},
      "background": {"edge_ratio": 0.0234, "background_ok": true},
      "geometry": {"geometry_ok": true},
      "text": {"text_detected": false, "word_count": 0, "text_area_ratio": 0.0, "text_ok": true},
      "background_uniform": {
        "background_uniform": true,
        "dominant_colors": 1,
        "edge_density": 0.0087,
        "color_std": 12.34,
        "reason": "Background is uniform single color (PASS)"
      }
    }
  }
}
```

---

## Troubleshooting

### Issue: Legitimate photos failing

**Solution**: Lower thresholds or increase max_colors to 3

### Issue: Missing scikit-learn error

**Solution**: Install requirements: `pip install -r requirements.txt`

### Issue: Face not detected, whole image analyzed

**Solution**: This is intentional fallback behavior. Check face_detector module.

### Issue: Very light skin + white background detected as "multiple colors"

**Solution**: This is expected. Advise users to use contrasting background.

---

## Future Enhancements

Potential improvements:
1. ✨ Detect specific background colors (e.g., require white/blue only)
2. ✨ Use ML model for better background segmentation
3. ✨ Detect shadows specifically (separate from objects)
4. ✨ Support custom color tolerance per region
5. ✨ Provide visualization of detected issues

---

## Summary

The `check_background_uniform_color` module ensures professional ID photo standards by:
- ✅ Detecting single uniform background colors
- ✅ Rejecting backgrounds with objects, patterns, or gradients
- ✅ Excluding face region from analysis
- ✅ Providing detailed diagnostic information
- ✅ Integrating seamlessly with existing verification pipeline

**Key Metrics**:
- **Score Impact**: +1 point (9 total possible)
- **Default Threshold**: 7/9 to pass
- **Runtime**: < 100ms per image
- **Dependencies**: opencv-python, numpy, scikit-learn
