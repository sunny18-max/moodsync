import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import logging

logger = logging.getLogger(__name__)

class TextEmotionAnalyzer:
    def __init__(self):
        self.model = None
        self.emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'neutral']
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load pre-trained text emotion model"""
        try:
            # In a real project, you would load a pre-trained model
            # For demo purposes, we'll create a simple pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )),
                ('classifier', LogisticRegression(
                    multi_class='multinomial',
                    max_iter=1000
                ))
            ])
            
            # Sample training data (in practice, use a proper dataset)
            sample_texts = [
                "I'm so happy today!", "This is amazing!", "I love this!",
                "I feel so sad", "This is terrible", "I'm disappointed",
                "I'm angry about this", "This makes me mad", "I hate this",
                "Wow that's surprising!", "I can't believe it!",
                "I'm scared", "This is frightening",
                "It's okay", "Nothing special", "Regular day"
            ]
            
            sample_labels = [
                'happy', 'happy', 'happy',
                'sad', 'sad', 'sad',
                'angry', 'angry', 'angry',
                'surprise', 'surprise',
                'fear', 'fear',
                'neutral', 'neutral', 'neutral'
            ]
            
            self.model.fit(sample_texts, sample_labels)
            
        except Exception as e:
            logger.error(f"Error initializing text model: {e}")
    
    def analyze_text_emotion(self, text):
        """Analyze emotion from text input"""
        try:
            if not text or len(text.strip()) < 3:
                return {'emotion': 'neutral', 'confidence': 1.0}
            
            # Simple rule-based fallback
            emotion_keywords = {
                'happy': ['happy', 'joy', 'love', 'amazing', 'great', 'wonderful'],
                'sad': ['sad', 'terrible', 'disappointed', 'bad', 'unhappy'],
                'angry': ['angry', 'mad', 'hate', 'frustrated', 'annoyed'],
                'surprise': ['surprise', 'wow', 'unbelievable', 'shocked'],
                'fear': ['scared', 'fear', 'frightening', 'afraid']
            }
            
            text_lower = text.lower()
            emotion_scores = {emotion: 0 for emotion in self.emotions}
            
            # Keyword matching
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        emotion_scores[emotion] += 1
            
            # Use ML model if available
            if self.model:
                predicted_emotion = self.model.predict([text])[0]
                probabilities = self.model.predict_proba([text])[0]
                confidence = max(probabilities)
                
                return {
                    'emotion': predicted_emotion,
                    'confidence': float(confidence),
                    'all_emotions': dict(zip(self.model.classes_, probabilities))
                }
            else:
                # Fallback to keyword-based approach
                dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
                return {
                    'emotion': dominant_emotion[0] if dominant_emotion[1] > 0 else 'neutral',
                    'confidence': dominant_emotion[1] / 10.0,
                    'all_emotions': emotion_scores
                }
                
        except Exception as e:
            logger.error(f"Error in text emotion analysis: {e}")
            return {'emotion': 'neutral', 'confidence': 0.0}