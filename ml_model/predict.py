"""
Standalone Prediction Script
=============================
Load a trained model and predict on a single image.

Usage:
    python ml_model/predict.py --image path/to/image.jpg
    python ml_model/predict.py --image path/to/image.jpg --model ml_model/skin_disease_model.h5
"""

import os
import sys
import argparse
import numpy as np
from PIL import Image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_model.model_architecture import IMG_HEIGHT, IMG_WIDTH, CLASS_NAMES


def predict_image(image_path, model_path='ml_model/skin_disease_model.h5'):
    """
    Predict skin disease from an image.
    
    Args:
        image_path: Path to input image
        model_path: Path to saved .h5 model
    
    Returns:
        Dictionary with prediction results
    """
    # Load model
    print(f"[INFO] Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    
    # Load and preprocess image
    print(f"[INFO] Processing image: {image_path}")
    img = Image.open(image_path).convert('RGB')
    img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    # Predict
    predictions = model.predict(img_array, verbose=0)[0]
    
    # Get top predictions
    top_indices = np.argsort(predictions)[::-1]
    
    results = {
        'predicted_class': CLASS_NAMES[top_indices[0]],
        'confidence': float(predictions[top_indices[0]]) * 100,
        'all_predictions': {
            CLASS_NAMES[i]: float(predictions[i]) * 100 
            for i in top_indices
        }
    }
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict skin disease from image')
    parser.add_argument('--image', type=str, required=True, help='Path to image file')
    parser.add_argument('--model', type=str, default='ml_model/skin_disease_model.h5',
                        help='Path to trained model')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"[ERROR] Image not found: {args.image}")
        sys.exit(1)
    
    results = predict_image(args.image, args.model)
    
    print("\n" + "=" * 50)
    print("  PREDICTION RESULTS")
    print("=" * 50)
    print(f"  Disease: {results['predicted_class']}")
    print(f"  Confidence: {results['confidence']:.2f}%")
    print("\n  All Probabilities:")
    for name, prob in results['all_predictions'].items():
        bar = '█' * int(prob / 2)
        print(f"    {name:25s} {prob:6.2f}% {bar}")
