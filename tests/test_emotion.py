#!/usr/bin/env python3
"""
Test script for Emotion Detection functionality
"""

import sys
import os
import numpy as np

# Add the parent directory to Python path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.emotion.facial_analyzer import FacialEmotionAnalyzer
    from app.emotion.text_analyzer import TextEmotionAnalyzer
    print("✓ Successfully imported emotion modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_text_emotion_detection():
    """Test text emotion detection with sample texts"""
    print("\nTesting Text Emotion Detection...")
    
    try:
        analyzer = TextEmotionAnalyzer()
        print("✓ TextEmotionAnalyzer initialized successfully")
        
        # Test cases with expected emotions
        test_cases = [
            ("I'm so happy today! This is amazing!", "happy"),
            ("I feel very sad and disappointed", "sad"), 
            ("This makes me angry and frustrated", "angry"),
            ("Wow! I can't believe this surprise!", "surprise"),
            ("I'm scared and frightened", "fear"),
            ("It's just a normal day", "neutral")
        ]
        
        for text, expected_emotion in test_cases:
            result = analyzer.analyze_text_emotion(text)
            if result:
                detected_emotion = result['emotion']
                confidence = result['confidence']
                print(f"✓ Text: '{text[:30]}...'")
                print(f"  Detected: {detected_emotion} (confidence: {confidence:.2f})")
                
                if detected_emotion == expected_emotion:
                    print(f"  ✅ Emotion matched expected: {expected_emotion}")
                else:
                    print(f"  ⚠️  Expected {expected_emotion}, got {detected_emotion}")
            else:
                print(f"❌ No result for text: '{text[:30]}...'")
        
        print("🎉 Text emotion detection tests completed!")
        
    except Exception as e:
        print(f"❌ Text emotion detection test failed: {e}")

def test_facial_emotion_detection():
    """Test facial emotion detection"""
    print("\nTesting Facial Emotion Detection...")
    
    try:
        analyzer = FacialEmotionAnalyzer()
        print("✓ FacialEmotionAnalyzer initialized successfully")
        print(f"  DeepFace available: {analyzer.deepface_available}")
        
        # Test with a simple frame (no actual face)
        test_frame = generate_test_frame()
        
        # Test face detection
        faces = analyzer.detect_faces(test_frame)
        print(f"✓ Face detection working: {len(faces)} faces detected")
        
        # Test emotion detection
        emotion_result = analyzer.detect_emotion_from_frame(test_frame)
        if emotion_result:
            method = emotion_result.get('method', 'unknown')
            print(f"✓ Emotion detection working: {emotion_result['emotion']} (method: {method})")
            print(f"  Confidence: {emotion_result['confidence']:.2f}")
        else:
            print("⚠️ Emotion detection failed")
            
        print("🎉 Facial emotion detection tests completed!")
        
    except Exception as e:
        print(f"❌ Facial emotion detection test failed: {e}")

def generate_test_frame(width=640, height=480):
    """Generate a test frame for emotion detection"""
    # Create a simple random frame
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return frame

def test_emotion_integration():
    """Test integration between components"""
    print("\nTesting Emotion Integration...")
    
    try:
        facial_analyzer = FacialEmotionAnalyzer()
        text_analyzer = TextEmotionAnalyzer()
        
        # Test that both analyzers work together
        text_result = text_analyzer.analyze_text_emotion("I'm feeling great!")
        frame_result = facial_analyzer.detect_emotion_from_frame(generate_test_frame())
        
        if text_result and frame_result:
            print("✓ Both text and facial emotion detection working together")
            print(f"  Text emotion: {text_result['emotion']}")
            print(f"  Facial emotion: {frame_result['emotion']}")
        else:
            print("⚠️ Integration test had some issues")
            
        print("🎉 Emotion integration tests completed!")
        
    except Exception as e:
        print(f"❌ Emotion integration test failed: {e}")

def run_all_emotion_tests():
    """Run all emotion detection tests"""
    print("=" * 60)
    print("EMOTION DETECTION TEST SUITE")
    print("=" * 60)
    
    test_text_emotion_detection()
    test_facial_emotion_detection()
    test_emotion_integration()
    
    print("\n" + "=" * 60)
    print("EMOTION TEST SUMMARY: Check for any ❌ or ⚠️  above")
    print("=" * 60)

if __name__ == '__main__':
    run_all_emotion_tests()