#!/usr/bin/env python3
"""
Test script to isolate the image processing issue
"""

import sys
import os
import cv2
import numpy as np
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_opencv():
    """Test if OpenCV can read and process images"""
    print("🧪 Testing OpenCV image processing...")
    
    # Create a test image
    test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    
    # Save and read it back
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        temp_path = f.name
        cv2.imwrite(temp_path, test_image)
        print(f"✅ Created test image: {temp_path}")
    
    try:
        # Try to read the image
        img = cv2.imread(temp_path)
        if img is not None:
            print(f"✅ OpenCV can read image: {img.shape}")
        else:
            print("❌ OpenCV cannot read image")
            return False
        
        # Test face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            print("❌ Cannot load face cascade")
            return False
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        print(f"✅ Face detection working. Found {len(faces)} faces")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_deepface():
    """Test if DeepFace can process images"""
    print("\n🧪 Testing DeepFace...")
    
    try:
        from deepface import DeepFace
        print("✅ DeepFace imported successfully")
        
        # Create a test image with a simple pattern (no face)
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = f.name
            cv2.imwrite(temp_path, test_image)
        
        try:
            # Test DeepFace with enforce_detection=False
            result = DeepFace.analyze(
                img_path=temp_path,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            print(f"✅ DeepFace analysis completed: {type(result)}")
            
            if isinstance(result, list) and len(result) > 0:
                emotion = result[0]['dominant_emotion']
                print(f"✅ DeepFace emotion: {emotion}")
            else:
                print("⚠️ DeepFace returned empty result")
            
            return True
            
        except Exception as e:
            print(f"❌ DeepFace analysis failed: {e}")
            return False
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except ImportError as e:
        print(f"❌ Cannot import DeepFace: {e}")
        return False
    except Exception as e:
        print(f"❌ DeepFace test failed: {e}")
        return False

def test_actual_image(image_path):
    """Test with an actual image file"""
    print(f"\n🧪 Testing with actual image: {image_path}")
    
    if not os.path.exists(image_path):
        print("❌ Image file does not exist")
        return False
    
    try:
        # Test OpenCV
        img = cv2.imread(image_path)
        if img is None:
            print("❌ OpenCV cannot read the image")
            return False
        print(f"✅ OpenCV read image: {img.shape}")
        
        # Test face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        print(f"✅ Found {len(faces)} faces in image")
        
        # Test DeepFace
        from deepface import DeepFace
        result = DeepFace.analyze(
            img_path=image_path,
            actions=['emotion'],
            enforce_detection=False,
            silent=True
        )
        print(f"✅ DeepFace analysis successful")
        
        if isinstance(result, list) and len(result) > 0:
            emotion = result[0]['dominant_emotion']
            confidence = result[0]['emotion'][emotion]
            print(f"✅ Emotion: {emotion} (confidence: {confidence})")
        
        return True
        
    except Exception as e:
        print(f"❌ Actual image test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔍 Starting Image Processing Diagnostics...")
    print("=" * 50)
    
    # Test basic functionality
    test_opencv()
    test_deepface()
    
    # Test with an actual image if provided
    if len(sys.argv) > 1:
        test_actual_image(sys.argv[1])
    
    print("=" * 50)
    print("🎉 Diagnostics completed!")