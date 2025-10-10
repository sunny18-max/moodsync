import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Spotify API Configuration
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')
    
    # Model Configuration
    EMOTION_MODEL_PATH = os.getenv('EMOTION_MODEL_PATH', 'data/models/emotion_model.h5')
    FACE_DETECTION_MODEL = 'opencv'  # or 'mtcnn', 'retinaface'
    
    # App Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    PORT = int(os.getenv('PORT', 5000))
    
    # Emotion mappings
    EMOTION_TO_GENRE = {
        'happy': ['pop', 'dance', 'electronic', 'disco'],
        'sad': ['acoustic', 'blues', 'sad', 'piano'],
        'angry': ['rock', 'metal', 'punk', 'hard-rock'],
        'surprise': ['indie', 'alternative', 'experimental'],
        'fear': ['ambient', 'classical', 'soundtrack'],
        'disgust': ['industrial', 'noise', 'experimental'],
        'neutral': ['chill', 'indie', 'lo-fi']
    }

settings = Settings()