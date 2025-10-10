import numpy as np
import cv2
from deepface import DeepFace
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import logging

logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self, model_name='DeepFace'):
        self.model_name = model_name
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def detect_emotion_from_image(self, image_path):
        """Detect emotion from image file"""
        try:
            # Analyze image using DeepFace
            analysis = DeepFace.analyze(
                img_path=image_path,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            if isinstance(analysis, list):
                analysis = analysis[0]
                
            emotion = analysis['dominant_emotion']
            confidence = analysis['emotion'][emotion]
            
            return {
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': analysis['emotion']
            }
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            return None
    
    def detect_emotion_from_frame(self, frame):
        """Detect emotion from video frame"""
        try:
            # Convert frame to RGB (DeepFace expects RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Analyze frame
            analysis = DeepFace.analyze(
                img_path=rgb_frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',
                silent=True
            )
            
            if isinstance(analysis, list):
                analysis = analysis[0]
                
            emotion = analysis['dominant_emotion']
            confidence = analysis['emotion'][emotion]
            
            return {
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': analysis['emotion']
            }
            
        except Exception as e:
            logger.error(f"Error in frame emotion detection: {e}")
            return None
    
    def detect_faces(self, frame):
        """Detect faces in frame for real-time processing"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        return faces