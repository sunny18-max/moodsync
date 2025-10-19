import cv2
import logging
import numpy as np
import os
import time
from datetime import datetime
import tempfile

# Configure logging without emojis for Windows compatibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import DeepFace with comprehensive error handling
DEEPFACE_AVAILABLE = False
DEEPFACE_ERROR = None

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logger.info("DeepFace imported successfully")
except ImportError as e:
    DEEPFACE_ERROR = f"Import failed: {e}"
    logger.error(f"DeepFace import failed: {e}")
except Exception as e:
    DEEPFACE_ERROR = f"Initialization failed: {e}"
    logger.error(f"Error importing DeepFace: {e}")

def convert_numpy_types(obj):
    """
    Convert numpy data types to Python native types for JSON serialization
    """
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

class FacialEmotionAnalyzer:
    def __init__(self, detector_backend='retinaface'):
        """
        Initialize Facial Emotion Analyzer with robust error handling
        Using retinaface for better face detection accuracy
        """
        self.detector_backend = detector_backend
        
        # Initialize face cascade with error handling
        self.face_cascade = None
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                logger.error(f"OpenCV face cascade could not be loaded from {cascade_path}")
                self.face_cascade = None
            else:
                logger.info("OpenCV face cascade loaded successfully")
        except Exception as e:
            logger.error(f"Error loading face cascade: {e}")
            self.face_cascade = None
        
        # Available emotions
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        # Check if DeepFace is available
        self.deepface_available = DEEPFACE_AVAILABLE
        self.deepface_error = DEEPFACE_ERROR
        
        if not self.deepface_available:
            logger.warning(f"DeepFace not available: {self.deepface_error}")
        else:
            logger.info("DeepFace is available for emotion detection")
        
        logger.info(f"FacialEmotionAnalyzer initialized - DeepFace: {self.deepface_available}, OpenCV: {self.face_cascade is not None}")

    def detect_emotion_from_image(self, image_path, enforce_detection=False):
        """
        Detect emotion from image file with comprehensive error handling
        """
        logger.info(f"Starting emotion analysis for image: {image_path}")
        
        try:
            # First, validate the image with enhanced checks
            is_valid, error_msg, image_info = self.validate_image_enhanced(image_path)
            if not is_valid:
                logger.error(f"Image validation failed: {error_msg}")
                return self._get_fallback_emotion(f"Image validation failed: {error_msg}")
            
            logger.info(f"Image validation passed: {image_path}")
            logger.info(f"Image info: {image_info['width']}x{image_info['height']}, {image_info['file_size_mb']:.2f}MB, format: {image_info['format']}")
            
            # Check if image needs resizing
            processed_image_path = self._preprocess_image_if_needed(image_path, image_info)
            use_processed = processed_image_path != image_path
            
            try:
                # Try DeepFace first if available
                if self.deepface_available:
                    try:
                        logger.info(f"Using DeepFace for analysis (backend: {self.detector_backend})")
                        
                        # Try with primary detector first
                        try:
                            analysis = DeepFace.analyze(
                                img_path=processed_image_path if use_processed else image_path,
                                actions=['emotion'],
                                enforce_detection=True,
                                detector_backend='retinaface',  # Best for accuracy
                                silent=True
                            )
                        except:
                            # Fallback to opencv if retinaface fails
                            logger.info("Retinaface failed, trying opencv")
                            analysis = DeepFace.analyze(
                                img_path=processed_image_path if use_processed else image_path,
                                actions=['emotion'],
                                enforce_detection=False,  # More lenient
                                detector_backend='opencv',
                                silent=True
                            )
                        
                        logger.info(f"DeepFace analysis completed, result type: {type(analysis)}")
                        
                        # Handle multiple faces or no faces
                        if isinstance(analysis, list):
                            if len(analysis) > 0:
                                analysis = analysis[0]  # Use first face
                                logger.info(f"Detected {len(analysis)} faces, using first face")
                            else:
                                logger.warning("No faces detected in the image")
                                return self._get_fallback_emotion("No faces detected. Please ensure the image contains a clear, front-facing face.")
                        
                        emotion_scores = analysis['emotion']
                        dominant_emotion = analysis['dominant_emotion']
                        confidence = emotion_scores[dominant_emotion]
                        
                        result = {
                            'emotion': dominant_emotion,
                            'confidence': float(confidence / 100.0),  # Convert to Python float
                            'all_emotions': convert_numpy_types(emotion_scores),  # Convert numpy types
                            'face_region': analysis.get('region', {}),
                            'success': True,
                            'method': 'deepface',
                            'image_info': image_info,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        logger.info(f"Emotion detected: {dominant_emotion} (confidence: {confidence/100:.2f})")
                        return result
                        
                    except Exception as e:
                        logger.error(f"DeepFace analysis failed: {str(e)}")
                        # Fall back to OpenCV-based detection
                        return self._detect_with_opencv_fallback(processed_image_path if use_processed else image_path, image_info)
                else:
                    # DeepFace not available, use OpenCV fallback
                    logger.info("Using OpenCV fallback for emotion detection")
                    return self._detect_with_opencv_fallback(processed_image_path if use_processed else image_path, image_info)
                    
            finally:
                # Clean up processed image if created
                if use_processed and os.path.exists(processed_image_path):
                    try:
                        os.unlink(processed_image_path)
                        logger.info("Cleaned up processed image")
                    except Exception as cleanup_error:
                        logger.warning(f"Could not delete processed image: {cleanup_error}")
                
        except Exception as e:
            logger.error(f"Unexpected error in image emotion detection: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_fallback_emotion(f"Unexpected error: {str(e)}")

    def validate_image_enhanced(self, image_path):
        """
        Enhanced image validation with detailed checks
        """
        try:
            # Basic file checks
            if not os.path.exists(image_path):
                return False, "Image file does not exist", {}
            
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                return False, "Image file is empty", {}
            
            # File size limits
            MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
            if file_size > MAX_FILE_SIZE:
                return False, f"Image file too large ({file_size/1024/1024:.1f}MB). Maximum size is 20MB.", {}
            
            # Try to read the image with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                return False, "Cannot read image file (unsupported format or corrupt file)", {}
            
            height, width = img.shape[:2]
            
            # Image dimension checks
            MIN_DIMENSION = 100  # pixels
            MAX_DIMENSION = 5000  # pixels
            
            if width < MIN_DIMENSION or height < MIN_DIMENSION:
                return False, f"Image too small ({width}x{height}). Minimum size is {MIN_DIMENSION}x{MIN_DIMENSION} pixels.", {}
            
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                return False, f"Image too large ({width}x{height}). Maximum size is {MAX_DIMENSION}x{MAX_DIMENSION} pixels.", {}
            
            # Check image format
            file_extension = os.path.splitext(image_path)[1].lower()
            supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif']
            
            image_info = {
                'width': width,
                'height': height,
                'file_size_bytes': file_size,
                'file_size_mb': file_size / 1024 / 1024,
                'format': file_extension,
                'channels': img.shape[2] if len(img.shape) > 2 else 1,
                'aspect_ratio': round(width / height, 2) if height > 0 else 0
            }
            
            logger.info(f"Image validated: {width}x{height}, {file_size/1024/1024:.2f}MB, format: {file_extension}")
            return True, "Image is valid", image_info
            
        except Exception as e:
            return False, f"Error validating image: {str(e)}", {}

    def _preprocess_image_if_needed(self, image_path, image_info):
        """
        Preprocess image if it's too large or needs optimization
        """
        try:
            width = image_info['width']
            height = image_info['height']
            file_size_mb = image_info['file_size_mb']
            
            # Define optimal size for face detection
            OPTIMAL_MAX_DIMENSION = 1000  # pixels
            COMPRESSION_THRESHOLD = 5.0  # MB
            
            needs_resize = width > OPTIMAL_MAX_DIMENSION or height > OPTIMAL_MAX_DIMENSION
            needs_compression = file_size_mb > COMPRESSION_THRESHOLD
            
            if not needs_resize and not needs_compression:
                return image_path  # No processing needed
            
            logger.info(f"Preprocessing image: resize={needs_resize}, compress={needs_compression}")
            
            # Read original image
            img = cv2.imread(image_path)
            if img is None:
                return image_path
            
            processed_img = img.copy()
            
            # Resize if needed
            if needs_resize:
                scale_factor = OPTIMAL_MAX_DIMENSION / max(width, height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                processed_img = cv2.resize(processed_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # Save processed image with optimal compression
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"processed_{os.path.basename(image_path)}")
            
            # Use JPEG compression for large files
            if needs_compression:
                compression_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # 85% quality
                cv2.imwrite(temp_path, processed_img, compression_params)
            else:
                cv2.imwrite(temp_path, processed_img)
            
            new_size = os.path.getsize(temp_path) / 1024 / 1024
            logger.info(f"Saved processed image: {new_size:.2f}MB (original: {file_size_mb:.2f}MB)")
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image_path  # Return original if processing fails

    def detect_emotion_from_frame(self, frame, enforce_detection=False):
        """
        Detect emotion from video frame with comprehensive error handling
        """
        try:
            if frame is None:
                logger.error("Invalid frame provided (None)")
                return self._get_fallback_emotion("Invalid frame")
            
            if frame.size == 0:
                logger.error("Empty frame provided")
                return self._get_fallback_emotion("Empty frame")
            
            logger.info(f"Analyzing emotion from frame (shape: {frame.shape})")
            
            # Preprocess frame if needed
            processed_frame = self._preprocess_frame(frame)
            
            # Try DeepFace first if available
            if self.deepface_available:
                try:
                    # Convert BGR to RGB for DeepFace
                    rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    
                    # Try with primary detector first
                    try:
                        analysis = DeepFace.analyze(
                            img_path=rgb_frame,
                            actions=['emotion'],
                            enforce_detection=True,
                            detector_backend='retinaface',
                            silent=True
                        )
                    except:
                        # Fallback to opencv
                        logger.info("Retinaface failed for webcam, trying opencv")
                        analysis = DeepFace.analyze(
                            img_path=rgb_frame,
                            actions=['emotion'],
                            enforce_detection=False,
                            detector_backend='opencv',
                            silent=True
                        )
                    
                    if isinstance(analysis, list):
                        if len(analysis) > 0:
                            analysis = analysis[0]  # Use first face
                            logger.info(f"Detected {len(analysis)} faces in frame")
                        else:
                            logger.warning("No faces detected in frame")
                            return self._get_fallback_emotion("No faces detected")
                    
                    emotion_scores = analysis['emotion']
                    dominant_emotion = analysis['dominant_emotion']
                    confidence = emotion_scores[dominant_emotion]
                    
                    result = {
                        'emotion': dominant_emotion,
                        'confidence': float(confidence / 100.0),  # Convert to Python float
                        'all_emotions': convert_numpy_types(emotion_scores),  # Convert numpy types
                        'face_region': analysis.get('region', {}),
                        'success': True,
                        'method': 'deepface',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    logger.info(f"Frame emotion: {dominant_emotion} (confidence: {confidence/100:.2f})")
                    return result
                    
                except Exception as e:
                    logger.warning(f"DeepFace frame analysis failed: {str(e)}")
                    # Fall back to OpenCV-based detection
                    return self._detect_faces_simple(processed_frame)
            else:
                # DeepFace not available, use OpenCV fallback
                logger.info("Using OpenCV fallback for frame analysis")
                return self._detect_faces_simple(processed_frame)
                
        except Exception as e:
            logger.error(f"Unexpected error in frame emotion detection: {str(e)}")
            return self._get_fallback_emotion(f"Frame processing error: {str(e)}")

    def _preprocess_frame(self, frame):
        """
        Preprocess frame for better face detection
        """
        try:
            height, width = frame.shape[:2]
            
            # Resize if frame is too large
            MAX_FRAME_DIMENSION = 800
            if max(width, height) > MAX_FRAME_DIMENSION:
                scale_factor = MAX_FRAME_DIMENSION / max(width, height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized frame to {new_width}x{new_height}")
            
            return frame
            
        except Exception as e:
            logger.error(f"Frame preprocessing failed: {e}")
            return frame

    def _detect_with_opencv_fallback(self, image_path, image_info=None):
        """
        Fallback emotion detection using OpenCV for image files
        """
        try:
            logger.info(f"Using OpenCV fallback for image: {image_path}")
            img = cv2.imread(image_path)
            if img is None:
                logger.error("Could not read image file with OpenCV")
                return self._get_fallback_emotion("Could not read image file")
            
            logger.info(f"OpenCV read image successfully: {img.shape}")
            return self._detect_faces_simple(img, image_info)
            
        except Exception as e:
            logger.error(f"OpenCV fallback failed: {str(e)}")
            return self._get_fallback_emotion("Fallback detection failed")

    def _detect_faces_simple(self, frame, image_info=None):
        """
        Simple face detection and basic emotion estimation using OpenCV
        """
        try:
            if self.face_cascade is None:
                logger.warning("Face detector not available for fallback")
                return self._get_fallback_emotion("Face detector not available")
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                logger.info(f"OpenCV detected {len(faces)} faces")
                # If faces are detected, return neutral emotion
                result = self._get_fallback_emotion("Faces detected but using fallback emotion")
                result['face_count'] = len(faces)
                result['faces'] = faces.tolist()
                if image_info:
                    result['image_info'] = image_info
                return result
            else:
                logger.warning("OpenCV detected no faces")
                suggestion = self._get_face_detection_suggestion(frame.shape)
                return self._get_fallback_emotion(f"No faces detected. {suggestion}")
                
        except Exception as e:
            logger.error(f"Simple face detection failed: {str(e)}")
            return self._get_fallback_emotion("Face detection error")

    def _get_face_detection_suggestion(self, image_shape):
        """
        Provide suggestions for better face detection based on image characteristics
        """
        height, width = image_shape[:2]
        
        suggestions = []
        
        if width < 300 or height < 300:
            suggestions.append("Try using a higher resolution image")
        
        if width > 2000 or height > 2000:
            suggestions.append("Very large image, consider resizing")
        
        if len(suggestions) > 0:
            return " ".join(suggestions)
        else:
            return "Ensure the face is clearly visible, well-lit, and facing forward."

    def _get_fallback_emotion(self, reason="Fallback method"):
        """
        Provide consistent fallback emotion detection
        """
        fallback_emotion = 'neutral'
        fallback_confidence = 0.5
        
        result = {
            'emotion': fallback_emotion,
            'confidence': fallback_confidence,
            'all_emotions': {emotion: (100.0 if emotion == fallback_emotion else 0.0) for emotion in self.emotions},
            'success': True,
            'method': 'fallback',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Using fallback emotion: {fallback_emotion} ({reason})")
        return result