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
            if not text or len(text.strip()) < 1:
                return {'emotion': 'neutral', 'confidence': 1.0, 'all_emotions': {e: (100 if e == 'neutral' else 0) for e in self.emotions}}

            # Normalize input
            text_stripped = text.strip().lower()
            normalized = re.sub(r"[^a-z]+", "", text_stripped)

            # 1) Hard match for single-word explicit emotions -> force 100%
            direct_map = {
                'happy': 'happy',
                'joy': 'happy',
                'sad': 'sad',
                'angry': 'angry',
                'mad': 'angry',
                'surprise': 'surprise',
                'surprised': 'surprise',
                'fear': 'fear',
                'scared': 'fear',
                'afraid': 'fear',
                'neutral': 'neutral'
            }
            if normalized in direct_map:
                emo = direct_map[normalized]
                return {
                    'emotion': emo,
                    'confidence': 1.0,
                    'all_emotions': {e: (100.0 if e == emo else 0.0) for e in self.emotions}
                }

            # 2) Keyword signals (multi-word text)
            emotion_keywords = {
                'happy': ['happy', 'joy', 'love', 'amazing', 'great', 'wonderful'],
                'sad': ['sad', 'terrible', 'disappointed', 'bad', 'unhappy'],
                'angry': ['angry', 'mad', 'hate', 'frustrated', 'annoyed'],
                'surprise': ['surprise', 'wow', 'unbelievable', 'shocked'],
                'fear': ['scared', 'fear', 'frightening', 'afraid']
            }

            text_lower = text_stripped
            emotion_scores = {emotion: 0 for emotion in self.emotions}

            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        emotion_scores[emotion] += 1

            # 3) Use ML model if available, else keyword fallback
            if self.model:
                predicted_emotion = self.model.predict([text])[0]
                probabilities = self.model.predict_proba([text])[0]
                confidence = float(np.max(probabilities))
                # Map probabilities to full emotion set (missing -> 0.0)
                class_probs = dict(zip(self.model.classes_, probabilities))
                full_probs = {e: float(class_probs.get(e, 0.0)) for e in self.emotions}
                return {
                    'emotion': predicted_emotion,
                    'confidence': confidence,
                    'all_emotions': full_probs
                }
            else:
                dominant_emotion, count = max(emotion_scores.items(), key=lambda x: x[1])
                if count == 0:
                    dominant_emotion = 'neutral'
                return {
                    'emotion': dominant_emotion,
                    'confidence': min(1.0, count / 3.0) if dominant_emotion != 'neutral' else 0.5,
                    'all_emotions': {e: (100.0 if e == dominant_emotion else 0.0) for e in self.emotions}
                }

        except Exception as e:
            logger.error(f"Error in text emotion analysis: {e}")
            return {'emotion': 'neutral', 'confidence': 0.0, 'all_emotions': {e: (100 if e == 'neutral' else 0) for e in self.emotions}}
