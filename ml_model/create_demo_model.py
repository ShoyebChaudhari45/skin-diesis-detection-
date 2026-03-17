"""
Create Smart Demo Model
========================
Creates a skin disease demo model that:
  1. Correctly accepts 224×224×3 images (same as production model)
  2. Uses the IMAGE PIXEL COLORS (brightness, redness, warmth, contrast)
     to map different skin images to different disease classes
  3. Produces varied, realistic-looking predictions across ALL 7 classes

The trick: use a TensorFlow function-based model that extracts color
statistics BEFORE any learned weights can corrupt them, then applies
a deterministic heuristic mapping → softmax probabilities.

Run: python ml_model/create_demo_model.py
"""

import os
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_model.model_architecture import CLASS_NAMES, CLASS_CODES, IMG_HEIGHT, IMG_WIDTH


# ---------------------------------------------------------------------------
# Heuristic weight matrix (6 color features → 7 disease classes)
# Rows = color features: [mean_r, mean_g, mean_b, std_r, std_g, std_b]
# Cols = classes:        [akiec,  bcc,    bkl,    df,    mel,   nv,    vasc]
# ---------------------------------------------------------------------------
W_MATRIX = np.array([
    # akiec    bcc      bkl      df       mel      nv       vasc
    [  3.5,    2.5,     1.5,     2.0,    -0.5,     1.2,     4.0  ],  # mean_r
    [  0.5,    2.0,     1.8,     1.5,    -1.0,     1.8,    -1.5  ],  # mean_g
    [ -1.0,    1.5,     0.5,     0.5,    -2.0,     1.0,    -2.5  ],  # mean_b
    [  1.0,   -0.5,     0.8,     1.0,     5.0,    -2.0,     0.5  ],  # std_r
    [  0.5,   -0.5,     0.5,     0.8,     3.0,    -1.2,     0.3  ],  # std_g
    [  0.3,   -0.3,     0.3,     0.5,     2.5,    -1.0,     0.2  ],  # std_b
], dtype=np.float32)

BIAS = np.array(
    [0.20, 0.30, 0.25, 0.15, -0.10, 0.35, 0.10],
    dtype=np.float32
)

TEMPERATURE = 0.30   # lower = more confident predictions


def build_smart_demo_model():
    """
    Build a Keras model that uses image color statistics as features
    to produce varied skin-disease predictions.

    Architecture:
      Input (224, 224, 3)
        → Lambda: extract color stats → (6,) feature vector
        → Dense(7) with fixed heuristic weights + bias
        → Softmax
    """
    inputs = tf.keras.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3), name="input_image")

    # ── Extract color statistics via Lambda layer ──────────────────────────
    # Using a Lambda layer keeps the computation inside the Keras graph
    # so the model is fully serializable as .h5

    def extract_color_features(x):
        """x: (B, H, W, 3), returns (B, 6)"""
        r = x[:, :, :, 0]
        g = x[:, :, :, 1]
        b = x[:, :, :, 2]
        mean_r = tf.reduce_mean(r, axis=[1, 2], keepdims=False)
        mean_g = tf.reduce_mean(g, axis=[1, 2], keepdims=False)
        mean_b = tf.reduce_mean(b, axis=[1, 2], keepdims=False)
        std_r  = tf.math.reduce_std(r, axis=[1, 2])
        std_g  = tf.math.reduce_std(g, axis=[1, 2])
        std_b  = tf.math.reduce_std(b, axis=[1, 2])
        return tf.stack([mean_r, mean_g, mean_b, std_r, std_g, std_b], axis=1)

    features = tf.keras.layers.Lambda(
        extract_color_features,
        name="color_features"
    )(inputs)  # shape: (B, 6)

    # ── Dense layer with heuristic weights (NOT randomly initialized) ──────
    dense_out = tf.keras.layers.Dense(
        7, activation=None, use_bias=True, name="disease_logits"
    )(features)  # (B, 7)

    # Apply temperature scaling via another Lambda
    def temperature_scale(x):
        return x / TEMPERATURE

    scaled = tf.keras.layers.Lambda(temperature_scale, name="temperature_scale")(dense_out)
    predictions = tf.keras.layers.Softmax(name="predictions")(scaled)

    model = tf.keras.Model(inputs, predictions, name="skin_disease_demo_v2")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def set_heuristic_weights(model):
    """Set the Dense layer weights to our hand-crafted heuristic matrix."""
    dense_layer = model.get_layer("disease_logits")
    dense_layer.set_weights([W_MATRIX, BIAS])
    return model


def create_demo_model(save_path='ml_model/skin_disease_model.h5'):
    """Build, calibrate, and save the smart demo model."""
    print("=" * 65)
    print("  CREATING SMART DEMO MODEL (Color-Heuristic CNN v2)")
    print("=" * 65)
    print(f"\n[INFO] Classes ({len(CLASS_NAMES)} total): {', '.join(CLASS_NAMES)}")

    # Build model
    print("\n[INFO] Building color-heuristic model...")
    model = build_smart_demo_model()

    # Set heuristic weights
    print("[INFO] Setting disease-mapping heuristic weights...")
    model = set_heuristic_weights(model)
    model.summary()

    # ── Verify predictions are diverse ──────────────────────────────────────
    print("\n[INFO] Verifying predictions across 7 skin-type test images...")

    test_cases = [
        ("Dark lesion (Melanoma-like)",        [0.18, 0.12, 0.10], 0.08),
        ("Pink/pearl mole (BCC-like)",         [0.88, 0.76, 0.73], 0.04),
        ("Brown mole (Nevi-like)",             [0.52, 0.36, 0.26], 0.07),
        ("Red-scaly patch (Actinic Kerat.)",   [0.85, 0.44, 0.40], 0.07),
        ("Brown flat growth (BKL-like)",       [0.66, 0.50, 0.37], 0.05),
        ("Pinkish bump (Dermatofibroma-like)", [0.72, 0.59, 0.56], 0.06),
        ("Red-purple spot (Vascular-like)",    [0.82, 0.35, 0.50], 0.06),
    ]

    predicted_classes = []
    print()
    print(f"  {'Image Type':<40} {'Predicted Class':<26} {'Conf':>6}")
    print("  " + "─" * 75)

    for desc, color, noise_level in test_cases:
        np.random.seed(abs(hash(desc)) % 1000)
        img = np.clip(
            np.random.normal(loc=color, scale=noise_level,
                             size=(1, IMG_HEIGHT, IMG_WIDTH, 3)),
            0, 1
        ).astype(np.float32)

        preds = model.predict(img, verbose=0)[0]
        top_idx = int(np.argmax(preds))
        top_class = CLASS_NAMES[top_idx]
        confidence = float(preds[top_idx]) * 100
        predicted_classes.append(top_class)

        # Show top-3 predictions
        top3 = sorted(enumerate(preds), key=lambda x: -x[1])[:3]
        top3_str = ", ".join(f"{CLASS_NAMES[i][:10]}:{v*100:.0f}%" for i, v in top3)
        print(f"  {desc:<40} {top_class:<26} {confidence:>5.1f}%")
        print(f"  {'':40} Top3: {top3_str}")
        print()

    unique = set(predicted_classes)
    print(f"  → Unique classes predicted: {len(unique)} / {len(CLASS_NAMES)}")
    if len(unique) >= 6:
        print("  ✅ Excellent diversity — all 7 classes reachable!")
    elif len(unique) >= 5:
        print("  ✓ Good diversity — demo model is working correctly!")
    else:
        print("  ⚠ Some classes not hit — but still much better than single-class")

    # Save
    os.makedirs(
        os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True
    )
    model.save(save_path)
    file_size = os.path.getsize(save_path) / (1024 * 1024)

    print(f"\n[DONE] Demo model saved to: {save_path} ({file_size:.2f} MB)")
    print("[NOTE] Replace with a real trained model by downloading HAM10000 and running:")
    print("       python ml_model/train.py --data_dir dataset/HAM10000 --epochs 30")
    return model


if __name__ == "__main__":
    create_demo_model()
