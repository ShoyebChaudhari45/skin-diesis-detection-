"""
Training Pipeline for Skin Disease Classification CNN
=====================================================
This script handles the complete training workflow:
1. Dataset loading (HAM10000)
2. Image preprocessing & augmentation
3. Class-weight balanced training (handles severe class imbalance)
4. Evaluation (accuracy, loss, confusion matrix)
5. Model saving

Usage (full dataset):
    python ml_model/train.py --data_dir dataset/HAM10000 --epochs 30 --batch_size 16

Usage (quick test with subset):
    python ml_model/train.py --data_dir dataset/HAM10000 --epochs 5 --batch_size 16 --image_limit 1000

Usage (faster with smaller images):
    python ml_model/train.py --data_dir dataset/HAM10000 --epochs 30 --batch_size 32 --img_size 128
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_model.model_architecture import build_cnn_model, IMG_HEIGHT, IMG_WIDTH, CLASS_NAMES, CLASS_CODES


def load_ham10000_metadata(data_dir):
    """
    Load HAM10000 metadata CSV and map image paths.
    
    Args:
        data_dir: Root directory containing HAM10000 images and CSV
    
    Returns:
        DataFrame with columns: image_id, dx (diagnosis), image_path
    """
    # Try to find the metadata CSV
    csv_candidates = [
        os.path.join(data_dir, 'HAM10000_metadata.csv'),
        os.path.join(data_dir, 'metadata.csv'),
        os.path.join(data_dir, 'hmnist_28_28_RGB.csv'),
    ]
    
    csv_path = None
    for candidate in csv_candidates:
        if os.path.exists(candidate):
            csv_path = candidate
            break
    
    if csv_path is None:
        raise FileNotFoundError(
            f"No metadata CSV found in {data_dir}. "
            "Please download HAM10000 dataset and place metadata CSV in the data directory."
        )
    
    print(f"[INFO] Loading metadata from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Find image directories
    image_dirs = []
    for subdir in ['HAM10000_images_part_1', 'HAM10000_images_part_2', 'images', '']:
        full_path = os.path.join(data_dir, subdir)
        if os.path.isdir(full_path):
            image_dirs.append(full_path)
    
    # Map image IDs to file paths
    def find_image(image_id):
        for img_dir in image_dirs:
            for ext in ['.jpg', '.png', '.jpeg']:
                path = os.path.join(img_dir, f"{image_id}{ext}")
                if os.path.exists(path):
                    return path
        return None
    
    df['image_path'] = df['image_id'].apply(find_image)
    df = df.dropna(subset=['image_path'])
    
    print(f"[INFO] Found {len(df)} images")
    print(f"[INFO] Class distribution:\n{df['dx'].value_counts()}")
    
    return df


def preprocess_image(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH)):
    """
    Load and preprocess a single image.
    
    Args:
        image_path: Path to image file
        target_size: Tuple of (height, width)
    
    Returns:
        Preprocessed numpy array normalized to [0, 1]
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize((target_size[1], target_size[0]), Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32) / 255.0
    return img_array


def compute_class_weights(labels_int):
    """
    Compute class weights to handle severe class imbalance in HAM10000.
    HAM10000 imbalance: nv=6705, mel=1113, bkl=1099, bcc=514, akiec=327, vasc=142, df=115

    Returns:
        Dict mapping class index -> weight (higher weight = rarer class)
    """
    classes = np.arange(len(CLASS_NAMES))
    weights = compute_class_weight(
        class_weight='balanced',
        classes=classes,
        y=labels_int
    )
    class_weight_dict = {i: float(w) for i, w in enumerate(weights)}
    print("[INFO] Class weights (higher = rarer class):")
    for i, name in enumerate(CLASS_NAMES):
        print(f"  {name:<25} weight = {class_weight_dict[i]:.3f}")
    return class_weight_dict


def create_data_generators(X_train, y_train, X_val, y_val, batch_size=32):
    """
    Create training and validation data generators with augmentation.
    
    Training augmentation includes:
        - Random rotation (±20°)
        - Width/height shift (±20%)
        - Horizontal/vertical flip
        - Zoom (±20%)
        - Shear (±15°)
    
    Args:
        X_train, y_train: Training data and labels
        X_val, y_val: Validation data and labels
        batch_size: Batch size for generators
    
    Returns:
        Tuple of (train_generator, val_generator)
    """
    # Training data augmentation
    train_datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        zoom_range=0.2,
        shear_range=0.15,
        fill_mode='nearest'
    )
    
    # Validation — no augmentation
    val_datagen = ImageDataGenerator()
    
    train_generator = train_datagen.flow(X_train, y_train, batch_size=batch_size)
    val_generator = val_datagen.flow(X_val, y_val, batch_size=batch_size)
    
    return train_generator, val_generator


def plot_training_history(history, save_dir):
    """
    Plot and save training accuracy and loss graphs.
    
    Args:
        history: Keras training history object
        save_dir: Directory to save plots
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # ---- Accuracy Plot ----
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
    ax.plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
    ax.set_title('Model Accuracy Over Epochs', fontsize=16, fontweight='bold')
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'accuracy_plot.png'), dpi=150)
    plt.close()
    print(f"[INFO] Accuracy plot saved to {save_dir}/accuracy_plot.png")
    
    # ---- Loss Plot ----
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(history.history['loss'], label='Train Loss', linewidth=2)
    ax.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
    ax.set_title('Model Loss Over Epochs', fontsize=16, fontweight='bold')
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'loss_plot.png'), dpi=150)
    plt.close()
    print(f"[INFO] Loss plot saved to {save_dir}/loss_plot.png")


def plot_confusion_matrix(y_true, y_pred, class_names, save_dir):
    """
    Generate and save confusion matrix heatmap.
    
    Args:
        y_true: True labels (integer-encoded)
        y_pred: Predicted labels (integer-encoded)
        class_names: List of class name strings
        save_dir: Directory to save plot
    """
    os.makedirs(save_dir, exist_ok=True)
    
    cm = confusion_matrix(y_true, y_pred)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=class_names, yticklabels=class_names, ax=ax
    )
    ax.set_title('Confusion Matrix', fontsize=16, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=12)
    ax.set_ylabel('True Label', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'confusion_matrix.png'), dpi=150)
    plt.close()
    print(f"[INFO] Confusion matrix saved to {save_dir}/confusion_matrix.png")


def train_model(data_dir, epochs=30, batch_size=16, model_save_path='ml_model/skin_disease_model.h5',
                image_limit=None, img_size=None):
    """
    Complete training pipeline with class-weight balancing.
    
    Steps:
        1. Load and preprocess HAM10000 data
        2. Compute class weights to handle imbalance
        3. Split into train/val/test sets (70/15/15)
        4. Create augmented data generators
        5. Build and train CNN model with class weighting
        6. Evaluate on test set
        7. Generate plots and save model
    
    Args:
        data_dir: Path to HAM10000 dataset
        epochs: Number of training epochs
        batch_size: Training batch size
        model_save_path: Path to save trained model
        image_limit: Optional int — limit total images for quick testing
        img_size: Optional int — resize images to img_size x img_size (default 224)
    """
    print("=" * 60)
    print("  SKIN DISEASE CLASSIFICATION - TRAINING PIPELINE")
    print("=" * 60)

    # Determine image size
    target_h = img_size if img_size else IMG_HEIGHT
    target_w = img_size if img_size else IMG_WIDTH
    print(f"[INFO] Image size: {target_h} × {target_w}")
    
    # Step 1: Load metadata
    print("\n[STEP 1] Loading dataset metadata...")
    df = load_ham10000_metadata(data_dir)

    # Apply image limit for quick testing
    if image_limit:
        print(f"[INFO] Limiting to {image_limit} images (--image_limit flag)")
        df = df.groupby('dx', group_keys=False).apply(
            lambda x: x.sample(min(len(x), max(1, int(image_limit * len(x) / len(df)))), random_state=42)
        ).reset_index(drop=True)
        print(f"[INFO] Reduced dataset: {len(df)} images")
        print(df['dx'].value_counts().to_string())
    
    # Step 2: Load and preprocess images
    print("\n[STEP 2] Loading and preprocessing images...")
    images = []
    labels = []
    
    for idx, row in df.iterrows():
        try:
            img = preprocess_image(row['image_path'], target_size=(target_h, target_w))
            images.append(img)
            label_idx = CLASS_CODES.index(row['dx'])
            labels.append(label_idx)
        except Exception as e:
            print(f"  [WARN] Skipping {row['image_id']}: {e}")
        
        if (idx + 1) % 500 == 0:
            print(f"  Processed {idx + 1}/{len(df)} images...")
    
    X = np.array(images)
    labels_array = np.array(labels)
    y = tf.keras.utils.to_categorical(labels_array, num_classes=len(CLASS_NAMES))
    
    print(f"  Dataset shape: X={X.shape}, y={y.shape}")
    print("  Class distribution in loaded data:")
    for code, name in zip(CLASS_CODES, CLASS_NAMES):
        count = np.sum(labels_array == CLASS_CODES.index(code))
        print(f"    {name:<25} {count:>5} images")

    # Step 3: Compute class weights (BEFORE splitting)
    print("\n[STEP 3] Computing class weights for imbalanced training...")
    class_weight_dict = compute_class_weights(labels_array)
    
    # Step 4: Split data (70% train, 15% val, 15% test)
    print("\n[STEP 4] Splitting dataset...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=labels_array
    )
    labels_temp = np.argmax(y_temp, axis=1)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=labels_temp
    )
    
    print(f"  Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
    
    # Step 5: Create data generators
    print("\n[STEP 5] Creating data generators with augmentation...")
    train_gen, val_gen = create_data_generators(X_train, y_train, X_val, y_val, batch_size)
    
    # Step 6: Build model
    print("\n[STEP 6] Building CNN model...")
    model = build_cnn_model(input_shape=(target_h, target_w, 3))
    model.summary()
    
    # Step 7: Set up callbacks
    callbacks = [
        ModelCheckpoint(
            model_save_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=8,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Step 8: Train WITH class weights
    print("\n[STEP 7] Training model with class weights...")
    print("[INFO] Class weights ensure minority classes (df=115, vasc=142) get equal emphasis")
    history = model.fit(
        train_gen,
        steps_per_epoch=max(1, len(X_train) // batch_size),
        epochs=epochs,
        validation_data=val_gen,
        validation_steps=max(1, len(X_val) // batch_size),
        callbacks=callbacks,
        class_weight=class_weight_dict,
        verbose=1
    )
    
    # Step 9: Evaluate on test set
    print("\n[STEP 8] Evaluating on test set...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"  Test Accuracy: {test_accuracy:.4f}")
    print(f"  Test Loss: {test_loss:.4f}")
    
    # Generate predictions
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
    
    # Classification report — verify all 7 classes appear
    print("\n[STEP 9] Classification Report (all 7 classes):")
    print(classification_report(y_true_classes, y_pred_classes, target_names=CLASS_NAMES))
    
    # Per-class accuracy summary
    print("\n  Per-class prediction counts:")
    for i, name in enumerate(CLASS_NAMES):
        true_count = np.sum(y_true_classes == i)
        pred_count = np.sum(y_pred_classes == i)
        print(f"    {name:<25} true={true_count:>4}  predicted={pred_count:>4}")

    # Step 10: Generate plots
    results_dir = os.path.join(os.path.dirname(model_save_path), 'results')
    print(f"\n[STEP 10] Generating plots in {results_dir}...")
    plot_training_history(history, results_dir)
    plot_confusion_matrix(y_true_classes, y_pred_classes, CLASS_NAMES, results_dir)
    
    # Save model
    model.save(model_save_path)
    print(f"\n[DONE] Model saved to {model_save_path}")
    print(f"[DONE] Final Test Accuracy: {test_accuracy:.4f}")
    
    return model, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train Skin Disease Classification CNN')
    parser.add_argument('--data_dir', type=str, default='dataset/HAM10000',
                        help='Path to HAM10000 dataset directory')
    parser.add_argument('--epochs', type=int, default=30,
                        help='Number of training epochs (default: 30)')
    parser.add_argument('--batch_size', type=int, default=16,
                        help='Training batch size (default: 16)')
    parser.add_argument('--model_path', type=str, default='ml_model/skin_disease_model.h5',
                        help='Path to save trained model')
    parser.add_argument('--image_limit', type=int, default=None,
                        help='Limit total images for quick test runs (e.g. 1000)')
    parser.add_argument('--img_size', type=int, default=None,
                        help='Image size for faster training (e.g. 128 instead of 224)')
    
    args = parser.parse_args()
    train_model(
        args.data_dir,
        args.epochs,
        args.batch_size,
        args.model_path,
        image_limit=args.image_limit,
        img_size=args.img_size
    )
