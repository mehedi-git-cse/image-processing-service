import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands

def check_hands(image_bytes):
    """
    Check if hands are visible or holding objects.
    
    FAIL if:
    - Hands visible and covering face/ID
    - Hand position indicates holding object
    
    Args:
        image_bytes: Image in bytes format
        
    Returns:
        dict: {
            "hands_detected": bool,
            "hand_position": str,  # "covering_face", "near_face", "holding_object", "visible", "not_visible"
            "is_ok": bool,
            "reason": str
        }
    """
    
    try:
        # Decode image
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return _fail("Image decode failed")
        
        h, w = img.shape[:2]
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect hands
        with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as hands:
            results = hands.process(rgb)
        
        if not results.multi_hand_landmarks:
            return _pass("No hands detected")
        
        # Check hand positions
        hand_positions = []
        for hand_landmarks in results.multi_hand_landmarks:
            # Get hand bounding box
            x_coords = [lm.x for lm in hand_landmarks.landmark]
            y_coords = [lm.y for lm in hand_landmarks.landmark]
            
            hand_x_min, hand_x_max = min(x_coords), max(x_coords)
            hand_y_min, hand_y_max = min(y_coords), max(y_coords)
            
            # Face region typically in center-upper area
            face_region_x = (0.25, 0.75)
            face_region_y = (0.15, 0.65)
            
            # Check if hand is in face region
            hand_center_x = (hand_x_min + hand_x_max) / 2
            hand_center_y = (hand_y_min + hand_y_max) / 2
            
            # Check hand visibility and position
            if (face_region_x[0] <= hand_center_x <= face_region_x[1] and 
                face_region_y[0] <= hand_center_y <= face_region_y[1]):
                
                # Hand is near/covering face
                hand_positions.append("covering_face")
                
            elif hand_y_min < face_region_y[1] and hand_y_max > face_region_y[0]:
                # Hand partially in face region
                hand_positions.append("near_face")
                
            else:
                # Hand visible but not covering face
                hand_positions.append("visible")
        
        # Decision logic
        if "covering_face" in hand_positions:
            return {
                "hands_detected": True,
                "hand_position": "covering_face",
                "is_ok": False,
                "reason": "Hand is covering face/ID - not acceptable"
            }
        
        if "near_face" in hand_positions:
            return {
                "hands_detected": True,
                "hand_position": "near_face",
                "is_ok": False,
                "reason": "Hand near face - partially obscuring"
            }
        
        if "visible" in hand_positions:
            return {
                "hands_detected": True,
                "hand_position": "visible",
                "is_ok": True,
                "reason": "Hands visible but not covering face"
            }
        
        return _pass("No problematic hand positions detected")
        
    except Exception as e:
        return _fail(str(e))


def _pass(msg):
    return {
        "hands_detected": False,
        "hand_position": "not_visible",
        "is_ok": True,
        "reason": msg
    }


def _fail(msg):
    return {
        "hands_detected": True,
        "hand_position": "unknown",
        "is_ok": False,
        "reason": msg
    }
