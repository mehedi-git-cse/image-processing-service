"""
Test Script for Background Uniform Color Checker

This script demonstrates the new background_uniform_checker module.
You can test it with sample images to see how it works.
"""

import cv2
import numpy as np
from app.verifier.background_uniform_checker import check_background_uniform_color


def test_with_sample_image(image_path: str):
    """
    Test the background uniform checker with a real image file.
    
    Args:
        image_path: Path to image file (JPG, PNG, etc.)
    """
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print('='*60)
    
    # Read image as bytes (simulating FastAPI upload)
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Run the check
    result = check_background_uniform_color(image_bytes)
    
    # Display results
    print(f"\n✅ Status: {'PASS' if result['background_uniform'] else 'FAIL'}")
    print(f"📊 Dominant Colors: {result['dominant_colors']}")
    print(f"📐 Edge Density: {result['edge_density']:.4f}")
    print(f"🎨 Color Variation (std): {result['color_std']:.2f}")
    print(f"💬 Reason: {result['reason']}")
    print()


def create_test_images():
    """
    Create synthetic test images to demonstrate different scenarios.
    """
    print("\n🎨 Creating synthetic test images...\n")
    
    # Test 1: Perfect uniform white background with face
    img1 = np.ones((400, 300, 3), dtype=np.uint8) * 255  # White background
    cv2.rectangle(img1, (100, 100), (200, 250), (180, 150, 120), -1)  # Face-like rectangle
    cv2.imwrite('test_uniform_white.jpg', img1)
    print("✓ Created: test_uniform_white.jpg (should PASS)")
    
    # Test 2: Uniform light blue background with face
    img2 = np.ones((400, 300, 3), dtype=np.uint8)
    img2[:, :] = [230, 200, 180]  # Light blue
    cv2.rectangle(img2, (100, 100), (200, 250), (180, 150, 120), -1)  # Face
    cv2.imwrite('test_uniform_blue.jpg', img2)
    print("✓ Created: test_uniform_blue.jpg (should PASS)")
    
    # Test 3: Background with gradient (should FAIL)
    img3 = np.ones((400, 300, 3), dtype=np.uint8)
    for i in range(400):
        color = int(255 * (i / 400))
        img3[i, :] = [color, color, color]
    cv2.rectangle(img3, (100, 100), (200, 250), (180, 150, 120), -1)  # Face
    cv2.imwrite('test_gradient_bg.jpg', img3)
    print("✓ Created: test_gradient_bg.jpg (should FAIL - gradient)")
    
    # Test 4: Background with objects (should FAIL)
    img4 = np.ones((400, 300, 3), dtype=np.uint8) * 255  # White background
    cv2.rectangle(img4, (100, 100), (200, 250), (180, 150, 120), -1)  # Face
    cv2.rectangle(img4, (10, 10), (50, 50), (0, 0, 0), -1)  # Object in background
    cv2.circle(img4, (270, 50), 20, (100, 100, 100), -1)  # Another object
    cv2.imwrite('test_objects_bg.jpg', img4)
    print("✓ Created: test_objects_bg.jpg (should FAIL - objects)")
    
    # Test 5: Multi-color background (should FAIL)
    img5 = np.ones((400, 300, 3), dtype=np.uint8)
    img5[:, :150] = [255, 200, 200]  # Pink left side
    img5[:, 150:] = [200, 255, 200]  # Green right side
    cv2.rectangle(img5, (100, 100), (200, 250), (180, 150, 120), -1)  # Face
    cv2.imwrite('test_multicolor_bg.jpg', img5)
    print("✓ Created: test_multicolor_bg.jpg (should FAIL - multiple colors)")


def run_tests():
    """
    Main test runner.
    """
    print("\n" + "="*60)
    print("BACKGROUND UNIFORM COLOR CHECKER - TEST SUITE")
    print("="*60)
    
    # Create test images
    create_test_images()
    
    # Test each image
    test_images = [
        'test_uniform_white.jpg',
        'test_uniform_blue.jpg',
        'test_gradient_bg.jpg',
        'test_objects_bg.jpg',
        'test_multicolor_bg.jpg'
    ]
    
    print("\n" + "="*60)
    print("RUNNING TESTS")
    print("="*60)
    
    for img_path in test_images:
        try:
            test_with_sample_image(img_path)
        except FileNotFoundError:
            print(f"❌ File not found: {img_path}")
        except Exception as e:
            print(f"❌ Error testing {img_path}: {str(e)}")
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("""
Expected Results:
  ✅ test_uniform_white.jpg  → PASS (uniform white)
  ✅ test_uniform_blue.jpg   → PASS (uniform light blue)
  ❌ test_gradient_bg.jpg    → FAIL (gradient detected)
  ❌ test_objects_bg.jpg     → FAIL (objects/edges detected)
  ❌ test_multicolor_bg.jpg  → FAIL (multiple colors)
    """)


if __name__ == "__main__":
    run_tests()
