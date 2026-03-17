"""
CNN Model Architecture for Skin Disease Classification
=======================================================
Uses a custom Convolutional Neural Network (CNN) for classifying
skin disease images into 7 categories from the HAM10000 dataset.

Classes:
    0: Actinic Keratoses (akiec)
    1: Basal Cell Carcinoma (bcc)
    2: Benign Keratosis (bkl)
    3: Dermatofibroma (df)
    4: Melanoma (mel)
    5: Melanocytic Nevi (nv)
    6: Vascular Lesions (vasc)
"""

import tensorflow as tf
from tensorflow.keras import layers, models


# Image dimensions expected by the model
IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_CHANNELS = 3
NUM_CLASSES = 7

# Class labels mapping
CLASS_NAMES = [
    "Actinic Keratoses",
    "Basal Cell Carcinoma",
    "Benign Keratosis",
    "Dermatofibroma",
    "Melanoma",
    "Melanocytic Nevi",
    "Vascular Lesions"
]

# Short codes from HAM10000 dataset
CLASS_CODES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]


def build_cnn_model(input_shape=(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), num_classes=NUM_CLASSES):
    """
    Build a CNN model for skin disease classification.
    
    Architecture:
        - 4 Convolutional blocks (Conv2D + BatchNorm + ReLU + MaxPool)
        - Global Average Pooling
        - Fully Connected layers with Dropout
        - Softmax output layer
    
    Args:
        input_shape: Tuple of (height, width, channels)
        num_classes: Number of output classes
    
    Returns:
        Compiled Keras model
    """
    model = models.Sequential([
        # ---- Block 1 ----
        layers.Conv2D(32, (3, 3), padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(32, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),

        # ---- Block 2 ----
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),

        # ---- Block 3 ----
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.30),

        # ---- Block 4 ----
        layers.Conv2D(256, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(256, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.30),

        # ---- Classifier Head ----
        layers.GlobalAveragePooling2D(),
        layers.Dense(512),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])

    # Compile model with Adam optimizer
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


if __name__ == "__main__":
    # Build and display model summary
    model = build_cnn_model()
    model.summary()
    print(f"\nTotal parameters: {model.count_params():,}")
    print(f"Input shape: {(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS)}")
    print(f"Output classes: {NUM_CLASSES}")
    print(f"Classes: {CLASS_NAMES}")
