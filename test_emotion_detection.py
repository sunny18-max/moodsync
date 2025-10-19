"""
Test script to verify emotion detection is working correctly
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.emotion.facial_analyzer import FacialEmotionAnalyzer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_emotion_detection(image_path):
    """Test emotion detection on a single image"""
    print("\n" + "="*60)
    print("TESTING EMOTION DETECTION")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return
    
    print(f"\n📸 Testing image: {image_path}")
    print(f"📏 File size: {os.path.getsize(image_path) / 1024:.2f} KB")
    
    # Initialize analyzer
    print("\n🔧 Initializing FacialEmotionAnalyzer...")
    analyzer = FacialEmotionAnalyzer()
    
    print(f"✓ DeepFace available: {analyzer.deepface_available}")
    print(f"✓ Detector backend: {analyzer.detector_backend}")
    
    # Analyze emotion
    print("\n🎭 Analyzing emotion...")
    result = analyzer.detect_emotion_from_image(image_path)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    if result:
        print(f"\n🎯 Detected Emotion: {result['emotion'].upper()}")
        print(f"📊 Confidence: {result['confidence']*100:.1f}%")
        print(f"🔍 Method: {result.get('method', 'unknown')}")
        
        if 'all_emotions' in result:
            print("\n📈 All Emotion Scores:")
            sorted_emotions = sorted(
                result['all_emotions'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            for emotion, score in sorted_emotions:
                bar_length = int(score / 5)  # Scale to max 20 chars
                bar = "█" * bar_length
                print(f"  {emotion:10s}: {score:6.2f}% {bar}")
        
        if result.get('method') == 'fallback':
            print("\n⚠️  WARNING: Using fallback detection (DeepFace failed)")
            print("   This means the emotion might not be accurate.")
            print("   Reasons:")
            print("   - No clear face detected")
            print("   - Poor image quality")
            print("   - Bad lighting")
        elif result.get('method') == 'deepface':
            print("\n✅ SUCCESS: DeepFace detection working properly!")
        
        # Image info
        if 'image_info' in result:
            info = result['image_info']
            print(f"\n📐 Image Info:")
            print(f"  Size: {info['width']}x{info['height']} pixels")
            print(f"  Format: {info['format']}")
            print(f"  Channels: {info['channels']}")
    else:
        print("❌ No result returned from emotion detection")
    
    print("\n" + "="*60)

def main():
    """Main test function"""
    print("\n🚀 MoodSync Emotion Detection Test")
    print("="*60)
    
    # Check if image path provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_emotion_detection(image_path)
    else:
        print("\n📝 Usage: python test_emotion_detection.py <image_path>")
        print("\nExample:")
        print("  python test_emotion_detection.py path/to/sad_face.jpg")
        print("\n💡 Tips for best results:")
        print("  - Use clear, well-lit photos")
        print("  - Face should be front-facing")
        print("  - Image size: 300x300 pixels or larger")
        print("  - Supported formats: JPG, PNG, BMP, WEBP")
        print("\n🔍 Test with different emotions:")
        print("  - Happy: Smiling face")
        print("  - Sad: Crying or frowning face")
        print("  - Angry: Aggressive expression")
        print("  - Surprise: Shocked expression")
        print("  - Fear: Scared expression")
        print("  - Neutral: Calm, expressionless face")

if __name__ == "__main__":
    main()
