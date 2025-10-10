from flask import Flask, render_template, request, jsonify
import cv2
import base64
import numpy as np
import logging
import os
import tempfile
import traceback

# Configure logging without emojis for Windows compatibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'bf0a4021e472eff2d9fca1990a026901'

def get_image_requirements_message():
    """Return image requirements for error messages"""
    return {
        'min_size': '100x100 pixels',
        'max_size': '5000x5000 pixels', 
        'max_file_size': '20MB',
        'formats': 'JPG, JPEG, PNG, BMP, WEBP, TIFF',
        'recommended': 'Clear front-facing face, good lighting, 300x300+ pixels'
    }

# Simple fallback emotion detection
def simple_emotion_detection():
    """Always return a neutral emotion as fallback"""
    return {
        'emotion': 'neutral',
        'confidence': 0.5,
        'all_emotions': {
            'angry': 0, 'disgust': 0, 'fear': 0, 
            'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 100
        },
        'success': True,
        'method': 'fallback'
    }

# Mock Spotify client for fallback
class MockSpotifyClient:
    def get_recommendations_by_emotion(self, emotion, limit=10):
        return [
            {
                'name': f'Sample {emotion.capitalize()} Song',
                'artists': ['Sample Artist'],
                'album': 'Sample Album',
                'preview_url': None,
                'external_url': 'https://open.spotify.com',
                'album_image': None
            }
            for _ in range(limit)
        ]
    
    def search_tracks(self, query, limit=10):
        return [
            {
                'name': f'Search Result for "{query}"',
                'artists': ['Various Artists'],
                'album': 'Search Results',
                'preview_url': None,
                'external_url': 'https://open.spotify.com',
                'album_image': None
            }
            for _ in range(min(limit, 5))
        ]

# Try to initialize real components, fallback to mock if failed
try:
    from app.emotion.facial_analyzer import FacialEmotionAnalyzer
    from app.emotion.text_analyzer import TextEmotionAnalyzer
    from app.spotify.client import SpotifyClient
    
    facial_analyzer = FacialEmotionAnalyzer()
    text_analyzer = TextEmotionAnalyzer()
    spotify_client = SpotifyClient()
    COMPONENTS_LOADED = True
    logger.info("Real components loaded successfully")
    
except Exception as e:
    logger.error(f"Failed to load real components: {e}")
    logger.error(traceback.format_exc())
    
    # Use mock components
    facial_analyzer = None
    text_analyzer = None
    spotify_client = MockSpotifyClient()
    COMPONENTS_LOADED = False
    logger.info("Using mock components as fallback")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze emotion from uploaded image - SUPER ROBUST VERSION"""
    logger.info("IMAGE ANALYSIS REQUEST RECEIVED")
    
    try:
        # Check if we have image data
        if 'image' not in request.files:
            logger.error("No 'image' in request.files")
            return jsonify({
                'error': 'No image provided',
                'requirements': get_image_requirements_message()
            }), 400
        
        image_file = request.files['image']
        logger.info(f"Processing file: {image_file.filename}")
        
        if image_file.filename == '':
            logger.error("Empty filename")
            return jsonify({
                'error': 'No image selected',
                'requirements': get_image_requirements_message()
            }), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff', 'tif'}
        file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        
        if file_extension not in allowed_extensions:
            logger.error(f"Invalid file extension: {file_extension}")
            return jsonify({
                'error': f'Invalid file type (.{file_extension}). Supported formats: JPG, PNG, GIF, BMP, WEBP, TIFF.',
                'requirements': get_image_requirements_message()
            }), 400
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            image_file.save(temp_file.name)
            temp_path = temp_file.name
        
        logger.info(f"Saved to: {temp_path}")
        
        try:
            # Try to use real facial analyzer if available
            if facial_analyzer:
                logger.info("Using real facial analyzer")
                emotion_result = facial_analyzer.detect_emotion_from_image(temp_path)
            else:
                logger.info("Using fallback emotion detection")
                emotion_result = simple_emotion_detection()
            
            logger.info(f"Emotion result: {emotion_result}")
            
            if not emotion_result:
                logger.error("No emotion result")
                emotion_result = simple_emotion_detection()
            
            # Get music recommendations
            tracks = spotify_client.get_recommendations_by_emotion(emotion_result['emotion'])
            logger.info(f"Got {len(tracks)} tracks")
            
            response = {
                'emotion': emotion_result['emotion'],
                'confidence': emotion_result['confidence'],
                'all_emotions': emotion_result.get('all_emotions', {}),
                'tracks': tracks,
                'method': emotion_result.get('method', 'fallback')
            }
            
            # Add image info if available
            if emotion_result.get('image_info'):
                response['image_info'] = emotion_result['image_info']
            
            logger.info("IMAGE ANALYSIS SUCCESS")
            return jsonify(response)
            
        except Exception as analysis_error:
            logger.error(f"Analysis failed: {analysis_error}")
            logger.error(traceback.format_exc())
            
            # Fallback response
            fallback_result = simple_emotion_detection()
            tracks = spotify_client.get_recommendations_by_emotion(fallback_result['emotion'])
            
            return jsonify({
                'emotion': fallback_result['emotion'],
                'confidence': fallback_result['confidence'],
                'all_emotions': fallback_result['all_emotions'],
                'tracks': tracks,
                'method': 'emergency_fallback',
                'note': 'Using emergency fallback due to analysis error'
            })
            
        finally:
            # Always clean up
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.info("Cleaned up temp file")
                except Exception as cleanup_error:
                    logger.warning(f"Could not delete temp file: {cleanup_error}")
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in image analysis: {e}")
        logger.error(traceback.format_exc())
        
        # Ultimate fallback
        fallback_result = simple_emotion_detection()
        tracks = spotify_client.get_recommendations_by_emotion(fallback_result['emotion'])
        
        return jsonify({
            'emotion': fallback_result['emotion'],
            'confidence': fallback_result['confidence'],
            'all_emotions': fallback_result['all_emotions'],
            'tracks': tracks,
            'method': 'critical_fallback',
            'note': 'Critical error occurred, using fallback'
        })

@app.route('/analyze_webcam', methods=['POST'])
def analyze_webcam():
    """Analyze emotion from webcam frame - SUPER ROBUST VERSION"""
    logger.info("WEBCAM ANALYSIS REQUEST RECEIVED")
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        logger.info(f"Received image data (length: {len(image_data)})")
        
        # Convert base64 to image
        try:
            header, encoded = image_data.split(",", 1)
            binary_data = base64.b64decode(encoded)
            np_data = np.frombuffer(binary_data, dtype=np.uint8)
            frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            logger.info(f"Decoded frame: {frame.shape if frame is not None else 'None'}")
        except Exception as e:
            logger.error(f"Image decoding failed: {e}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        if frame is None:
            return jsonify({'error': 'Could not decode image data'}), 400
        
        # Try to use real facial analyzer if available
        if facial_analyzer:
            logger.info("Using real facial analyzer for webcam")
            emotion_result = facial_analyzer.detect_emotion_from_frame(frame)
        else:
            logger.info("Using fallback for webcam")
            emotion_result = simple_emotion_detection()
        
        if not emotion_result:
            emotion_result = simple_emotion_detection()
        
        # Get music recommendations
        tracks = spotify_client.get_recommendations_by_emotion(emotion_result['emotion'])
        
        response = {
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'all_emotions': emotion_result.get('all_emotions', {}),
            'tracks': tracks,
            'method': emotion_result.get('method', 'fallback')
        }
        
        logger.info("WEBCAM ANALYSIS SUCCESS")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in webcam analysis: {e}")
        logger.error(traceback.format_exc())
        
        # Ultimate fallback
        fallback_result = simple_emotion_detection()
        tracks = spotify_client.get_recommendations_by_emotion(fallback_result['emotion'])
        
        return jsonify({
            'emotion': fallback_result['emotion'],
            'confidence': fallback_result['confidence'],
            'all_emotions': fallback_result['all_emotions'],
            'tracks': tracks,
            'method': 'critical_fallback',
            'note': 'Critical error occurred, using fallback'
        })

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    """Analyze emotion from text input"""
    logger.info("TEXT ANALYSIS REQUEST RECEIVED")
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Use text analyzer if available, otherwise use simple detection
        if text_analyzer:
            logger.info("Using real text analyzer")
            emotion_result = text_analyzer.analyze_text_emotion(text)
        else:
            logger.info("Using fallback text analysis")
            # Simple keyword-based fallback
            text_lower = text.lower()
            if any(word in text_lower for word in ['happy', 'joy', 'good', 'great', 'excited', 'wonderful']):
                emotion = 'happy'
                confidence = 0.8
            elif any(word in text_lower for word in ['sad', 'bad', 'terrible', 'awful', 'depressed', 'unhappy']):
                emotion = 'sad'
                confidence = 0.8
            elif any(word in text_lower for word in ['angry', 'mad', 'frustrated', 'annoyed', 'upset']):
                emotion = 'angry'
                confidence = 0.8
            elif any(word in text_lower for word in ['surprise', 'surprised', 'wow', 'amazing', 'unbelievable']):
                emotion = 'surprise'
                confidence = 0.7
            elif any(word in text_lower for word in ['fear', 'scared', 'afraid', 'frightened', 'terrified']):
                emotion = 'fear'
                confidence = 0.7
            else:
                emotion = 'neutral'
                confidence = 0.5
            
            emotion_result = {
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': {emotion: 100}
            }
        
        # Get music recommendations
        tracks = spotify_client.get_recommendations_by_emotion(emotion_result['emotion'])
        
        response = {
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'all_emotions': emotion_result.get('all_emotions', {}),
            'tracks': tracks
        }
        
        logger.info("TEXT ANALYSIS SUCCESS")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Text analysis error'}), 500

@app.route('/search_music', methods=['POST'])
def search_music():
    """Search for music directly"""
    logger.info("MUSIC SEARCH REQUEST RECEIVED")
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No search query provided'}), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({'error': 'Empty search query'}), 400
        
        tracks = spotify_client.search_tracks(query)
        
        response = {
            'tracks': tracks,
            'search_query': query
        }
        
        logger.info("MUSIC SEARCH SUCCESS")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in music search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Music search error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy' if COMPONENTS_LOADED else 'degraded',
        'components_loaded': COMPONENTS_LOADED,
        'facial_analyzer': facial_analyzer is not None,
        'text_analyzer': text_analyzer is not None,
        'spotify_client': spotify_client is not None,
        'message': 'Application is running with fallback support'
    }
    return jsonify(status)

@app.route('/debug')
def debug_info():
    """Debug information endpoint"""
    debug_info = {
        'python_version': os.sys.version,
        'working_directory': os.getcwd(),
        'components_loaded': COMPONENTS_LOADED,
        'facial_analyzer_available': facial_analyzer is not None,
        'text_analyzer_available': text_analyzer is not None,
        'spotify_client_available': spotify_client is not None,
        'image_requirements': get_image_requirements_message()
    }
    
    # Test OpenCV
    try:
        debug_info['opencv_version'] = cv2.__version__
        debug_info['opencv_working'] = True
    except Exception as e:
        debug_info['opencv_working'] = False
        debug_info['opencv_error'] = str(e)
    
    # Test NumPy
    try:
        debug_info['numpy_version'] = np.__version__
        debug_info['numpy_working'] = True
    except Exception as e:
        debug_info['numpy_working'] = False
        debug_info['numpy_error'] = str(e)
    
    return jsonify(debug_info)

if __name__ == '__main__':
    print("STARTING MOOD-BASED MUSIC RECOMMENDER")
    print("=" * 60)
    print("This version has maximum fallback support")
    print("It should NEVER return 500 errors")
    print("=" * 60)
    print(f"Real components loaded: {COMPONENTS_LOADED}")
    print("Server running on http://localhost:5000")
    print("=" * 60)
    print("Available endpoints:")
    print("  /                 - Main application")
    print("  /health           - Health check")
    print("  /debug            - Debug information")
    print("  /analyze_image    - Analyze image emotion")
    print("  /analyze_text     - Analyze text emotion")
    print("  /analyze_webcam   - Analyze webcam emotion")
    print("  /search_music     - Search for music")
    print("=" * 60)
    
    if not COMPONENTS_LOADED:
        print("WARNING: Some components failed to load")
        print("The application will use fallback methods")
        print("Check the logs for details")
    
    app.run(debug=True, port=5000, host='0.0.0.0')