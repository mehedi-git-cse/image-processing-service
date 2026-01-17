import cv2
import numpy as np
from sklearn.cluster import KMeans


def check_background_uniform_color(image_bytes, 
                                   max_colors: int = 2, 
                                   edge_density_threshold: float = 0.03,
                                   color_std_threshold: float = 30.0):
    """
    Verify that the image background (excluding face) is a single uniform color.
    
    This check ensures the background meets official ID photo standards:
    - Single solid color (white, light blue, light gray, etc.)
    - No objects, patterns, gradients, shadows, or textures
    - Face region is excluded from analysis
    
    Args:
        image_bytes: Image in bytes format
        max_colors: Maximum number of dominant colors allowed (default=2, allows slight variation)
        edge_density_threshold: Maximum allowed edge density for clean background (default=0.03)
        color_std_threshold: Maximum standard deviation for color uniformity (default=30.0)
        
    Returns:
        dict: {
            "background_uniform": bool,
            "dominant_colors": int,
            "edge_density": float,
            "color_std": float,
            "reason": str
        }
    """
    try:
        # Decode image
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return {
                "background_uniform": False,
                "dominant_colors": 0,
                "edge_density": 0.0,
                "color_std": 0.0,
                "reason": "Failed to decode image"
            }
        
        h, w = img.shape[:2]
        
        # Step 1: Detect face and create mask
        face_mask = _get_face_mask(img)
        
        # Step 2: Extract background pixels (non-face region)
        background_pixels = _extract_background_pixels(img, face_mask)
        
        if background_pixels.size == 0:
            return {
                "background_uniform": False,
                "dominant_colors": 0,
                "edge_density": 0.0,
                "color_std": 0.0,
                "reason": "No background pixels found (face occupies entire image)"
            }
        
        # Step 3: Analyze color uniformity using KMeans clustering
        dominant_color_count, color_std = _analyze_color_uniformity(
            background_pixels, max_colors
        )
        
        # Step 4: Detect objects/patterns using edge detection on background only
        edge_density = _detect_background_objects(img, face_mask)
        
        # Step 5: Determine pass/fail status
        is_uniform = (
            dominant_color_count <= max_colors and 
            edge_density < edge_density_threshold and
            color_std < color_std_threshold
        )
        
        # Step 6: Generate detailed reason
        reason = _generate_reason(
            is_uniform, dominant_color_count, edge_density, 
            color_std, max_colors, edge_density_threshold, color_std_threshold
        )
        
        return {
            "background_uniform": bool(is_uniform),
            "dominant_colors": int(dominant_color_count),
            "edge_density": float(round(edge_density, 4)),
            "color_std": float(round(color_std, 2)),
            "reason": reason
        }
        
    except Exception as e:
        return {
            "background_uniform": False,
            "dominant_colors": 0,
            "edge_density": 0.0,
            "color_std": 0.0,
            "reason": f"Error during background check: {str(e)}"
        }


def _get_face_mask(img):
    """
    Detect face and create a binary mask where face region is white (255).
    
    Args:
        img: OpenCV image (BGR format)
        
    Returns:
        numpy.ndarray: Binary mask (0 for background, 255 for face)
    """
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    # Mark face regions in mask with expanded boundary (to include hair, ears, etc.)
    for (x, y, fw, fh) in faces:
        # Expand face bounding box by 20% on each side to capture hair/ears
        expand_ratio = 0.2
        x_exp = max(0, int(x - fw * expand_ratio))
        y_exp = max(0, int(y - fh * expand_ratio))
        w_exp = min(w, int(x + fw * (1 + expand_ratio)))
        h_exp = min(h, int(y + fh * (1 + expand_ratio)))
        
        # Fill face region with white (255)
        mask[y_exp:h_exp, x_exp:w_exp] = 255
    
    return mask


def _extract_background_pixels(img, face_mask):
    """
    Extract background pixels (where mask is 0) as a flat array of BGR values.
    
    Args:
        img: OpenCV image (BGR format)
        face_mask: Binary mask (0 for background, 255 for face)
        
    Returns:
        numpy.ndarray: Background pixels as Nx3 array (N pixels, 3 channels)
    """
    # Get pixels where mask is 0 (background)
    background_pixels = img[face_mask == 0]
    return background_pixels


def _analyze_color_uniformity(pixels, max_colors):
    """
    Analyze color uniformity using KMeans clustering and standard deviation.
    
    Args:
        pixels: Nx3 array of BGR pixel values
        max_colors: Maximum number of clusters to check
        
    Returns:
        tuple: (dominant_color_count, color_std)
            - dominant_color_count: Number of significant color clusters
            - color_std: Standard deviation of pixel values (uniformity measure)
    """
    if pixels.shape[0] < 100:  # Need at least 100 pixels
        return 0, 0.0
    
    # Calculate standard deviation across all channels (measure of color variation)
    color_std = np.std(pixels)
    
    # Use KMeans to find dominant colors
    # Sample pixels if too many (for performance)
    sample_size = min(5000, pixels.shape[0])
    sampled_pixels = pixels[np.random.choice(pixels.shape[0], sample_size, replace=False)]
    
    # Perform KMeans clustering
    n_clusters = min(max_colors + 2, 5)  # Check a bit more than threshold
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(sampled_pixels)
    
    # Count significant clusters (those with >5% of pixels)
    labels = kmeans.labels_
    unique, counts = np.unique(labels, return_counts=True)
    percentages = counts / counts.sum()
    
    # Count clusters that represent >5% of the image
    significant_clusters = np.sum(percentages > 0.05)
    
    return significant_clusters, color_std


def _detect_background_objects(img, face_mask):
    """
    Detect objects, patterns, or textures in background using edge detection.
    
    Args:
        img: OpenCV image (BGR format)
        face_mask: Binary mask (0 for background, 255 for face)
        
    Returns:
        float: Edge density ratio (0 to 1, where 0 = clean background)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect edges using Canny
    edges = cv2.Canny(blurred, 50, 150)
    
    # Mask out face region from edges
    edges_background = cv2.bitwise_and(edges, edges, mask=cv2.bitwise_not(face_mask))
    
    # Calculate edge density in background
    background_area = np.sum(face_mask == 0)
    if background_area == 0:
        return 1.0  # No background, fail the check
    
    edge_pixels = np.sum(edges_background > 0)
    edge_density = edge_pixels / background_area
    
    return edge_density


def _generate_reason(is_uniform, color_count, edge_density, color_std, 
                     max_colors, edge_threshold, std_threshold):
    """
    Generate human-readable reason for pass/fail status.
    
    Args:
        is_uniform: Whether background passed the check
        color_count: Number of dominant colors detected
        edge_density: Edge density ratio
        color_std: Color standard deviation
        max_colors: Threshold for max colors
        edge_threshold: Threshold for edge density
        std_threshold: Threshold for color std
        
    Returns:
        str: Human-readable explanation
    """
    if is_uniform:
        return "Background is uniform single color (PASS)"
    
    # Identify specific failure reasons
    reasons = []
    
    if color_count > max_colors:
        reasons.append(f"Multiple colors detected ({color_count} dominant colors)")
    
    if edge_density >= edge_threshold:
        reasons.append(f"Objects/patterns detected (edge density: {edge_density:.3f})")
    
    if color_std >= std_threshold:
        reasons.append(f"Non-uniform color (variation: {color_std:.1f})")
    
    if reasons:
        return "Background not uniform: " + "; ".join(reasons)
    
    return "Background uniformity check failed"
