"""
ML Predictor Utility
====================
Handles loading the trained CNN model and performing predictions
on uploaded skin disease images.
"""

import os
import numpy as np
from PIL import Image
import io

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

# Import model constants
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_model.model_architecture import IMG_HEIGHT, IMG_WIDTH, CLASS_NAMES


class SkinDiseasePredictor:
    """
    Skin disease prediction engine.
    
    Loads a trained Keras model and provides prediction functionality
    for skin disease images.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the predictor.
        
        Args:
            model_path: Path to the saved .h5 model file
        """
        self.model = None
        self.model_path = model_path
        self.is_loaded = False
    
    def load_model(self, model_path: str = None):
        """
        Load the trained model from disk.
        
        Args:
            model_path: Optional path override to model file
        """
        path = model_path or self.model_path
        
        if not path or not os.path.exists(path):
            print(f"[WARNING] Model file not found at: {path}")
            print("[WARNING] Run 'python ml_model/create_demo_model.py' to create a demo model.")
            self.is_loaded = False
            return
        
        try:
            print(f"[INFO] Loading ML model from: {path}")
            self.model = tf.keras.models.load_model(path)
            self.is_loaded = True
            print(f"[INFO] Model loaded successfully! ({self.model.count_params():,} parameters)")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.is_loaded = False
    
    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocess an image for model prediction.
        
        Steps:
            1. Open image from bytes
            2. Convert to RGB
            3. Resize to model input dimensions
            4. Normalize pixel values to [0, 1]
            5. Add batch dimension
        
        Args:
            image_bytes: Raw image file bytes
        
        Returns:
            Preprocessed numpy array of shape (1, 224, 224, 3)
        """
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Resize to model's expected input
        img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.LANCZOS)
        
        # Convert to numpy array and normalize
        img_array = np.array(img, dtype=np.float32) / 255.0
        
        # Add batch dimension: (224, 224, 3) -> (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, image_bytes: bytes) -> dict:
        """
        Perform skin disease prediction on an image.
        
        Args:
            image_bytes: Raw image file bytes
        
        Returns:
            Dictionary containing:
                - predicted_class: Name of predicted disease
                - confidence: Confidence percentage
                - all_predictions: Dict of all class probabilities
        """
        if not self.is_loaded:
            raise RuntimeError(
                "Model not loaded. Run 'python ml_model/create_demo_model.py' first."
            )
        
        # Preprocess the image
        processed_img = self.preprocess_image(image_bytes)
        
        # Get model predictions
        predictions = self.model.predict(processed_img, verbose=0)[0]
        
        # Sort predictions by confidence
        top_indices = np.argsort(predictions)[::-1]
        
        # Build results dictionary
        results = {
            "predicted_class": CLASS_NAMES[top_indices[0]],
            "confidence": round(float(predictions[top_indices[0]]) * 100, 2),
            "all_predictions": {
                CLASS_NAMES[i]: round(float(predictions[i]) * 100, 2)
                for i in top_indices
            }
        }
        
        return results


# Global predictor instance
predictor = SkinDiseasePredictor()
