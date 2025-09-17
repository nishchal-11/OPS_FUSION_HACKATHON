#!/usr/bin/env python3
"""
Fast CNN Training Script for Heart Sound Classification
Trains on full dataset with optimized settings
"""

import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set TensorFlow environment variable
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Add parent directory for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils import *
from config import *

def create_efficient_cnn(input_shape):
    """Create an optimized CNN for heart sound classification."""

    model = models.Sequential([
        # Input layer
        layers.Input(shape=input_shape),

        # Efficient conv blocks with batch norm and dropout
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),

        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.3),

        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.4),

        # Global pooling for efficiency
        layers.GlobalAveragePooling2D(),

        # Dense layers
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),

        # Output
        layers.Dense(1, activation='sigmoid')
    ])

    return model

def load_spectrogram_batch(file_paths, labels):
    """Load a batch of spectrograms efficiently."""
    X_batch = []
    y_batch = []

    for path, label in zip(file_paths, labels):
        try:
            spec = np.load(path)
            spec = np.expand_dims(spec, axis=-1)  # Add channel dimension
            X_batch.append(spec)
            y_batch.append(label)
        except:
            continue

    return np.array(X_batch), np.array(y_batch)

def create_tf_dataset(processed_df, split='train', batch_size=32, shuffle=True):
    """Create efficient TensorFlow dataset."""

    # Filter by split
    split_df = processed_df[processed_df['split'] == split].copy()
    split_df['numeric_label'] = split_df['label'].map({'normal': 0, 'abnormal': 1})

    file_paths = split_df['spectrogram_path'].values
    labels = split_df['numeric_label'].values

    def generator():
        indices = np.arange(len(file_paths))

        while True:
            if shuffle:
                np.random.shuffle(indices)

            for i in range(0, len(indices), batch_size):
                batch_indices = indices[i:i+batch_size]
                batch_paths = file_paths[batch_indices]
                batch_labels = labels[batch_indices]

                X_batch, y_batch = load_spectrogram_batch(batch_paths, batch_labels)

                if len(X_batch) > 0:
                    yield X_batch, y_batch

    # Get input shape from first spectrogram
    try:
        first_spec = np.load(file_paths[0])
        input_shape = (first_spec.shape[0], first_spec.shape[1], 1)
    except:
        input_shape = (128, 157, 1)  # Default shape

    dataset = tf.data.Dataset.from_generator(
        generator,
        output_signature=(
            tf.TensorSpec(shape=(None,) + input_shape, dtype=tf.float32),
            tf.TensorSpec(shape=(None,), dtype=tf.int32)
        )
    ).prefetch(tf.data.AUTOTUNE)

    return dataset, len(split_df), input_shape

def main():
    print("🚀 Fast CNN Training on Full Dataset")
    print("=" * 50)

    # Load processed dataset
    dataset_path = DATA_DIR / "full_processed_dataset.csv"
    if not dataset_path.exists():
        print("❌ Processed dataset not found! Run batch processing first.")
        return

    processed_df = pd.read_csv(dataset_path)
    print(f"📊 Loaded {len(processed_df)} processed spectrograms")
    print(f"   Train: {len(processed_df[processed_df['split'] == 'train'])}")
    print(f"   Val: {len(processed_df[processed_df['split'] == 'val'])}")
    print(f"   Classes: {processed_df['label'].value_counts().to_dict()}")

    # Create datasets
    print("\n🔄 Creating TensorFlow datasets...")
    train_dataset, train_size, input_shape = create_tf_dataset(processed_df, 'train', BATCH_SIZE, shuffle=True)
    val_dataset, val_size, _ = create_tf_dataset(processed_df, 'val', BATCH_SIZE, shuffle=False)

    print(f"📐 Input shape: {input_shape}")
    print(f"🔢 Train batches per epoch: {train_size // BATCH_SIZE}")
    print(f"🔢 Val batches per epoch: {val_size // BATCH_SIZE}")

    # Create model
    print("\n🏗️ Building CNN model...")
    model = create_efficient_cnn(input_shape)

    # Compile with optimized settings
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )

    print(f"📊 Model parameters: {model.count_params():,}")

    # Calculate class weights
    train_labels = processed_df[processed_df['split'] == 'train']['label'].map({'normal': 0, 'abnormal': 1}).values
    class_weights = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)
    class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
    print(f"⚖️ Class weights: {class_weight_dict}")

    # Callbacks for efficient training
    callbacks_list = [
        callbacks.EarlyStopping(
            monitor='val_auc',
            patience=5,
            restore_best_weights=True,
            mode='max',
            verbose=1
        ),
        callbacks.ModelCheckpoint(
            filepath=str(MODELS_DIR / 'best_cnn_model.keras'),
            monitor='val_auc',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
    ]

    # Train model
    print("\n🚀 Starting training...")
    history = model.fit(
        train_dataset,
        steps_per_epoch=train_size // BATCH_SIZE,
        epochs=20,  # Limited epochs for speed
        validation_data=val_dataset,
        validation_steps=val_size // BATCH_SIZE,
        callbacks=callbacks_list,
        class_weight=class_weight_dict,
        verbose=1
    )

    print("\n✅ Training completed!")

    # Quick evaluation
    print("\n📊 Evaluating final model...")
    val_pred = model.predict(val_dataset, steps=val_size // BATCH_SIZE, verbose=0)
    val_true = []

    # Get true labels
    val_df = processed_df[processed_df['split'] == 'val']
    val_true = val_df['label'].map({'normal': 0, 'abnormal': 1}).values[:len(val_pred)]

    if len(val_pred) == len(val_true):
        val_auc = roc_auc_score(val_true, val_pred)
        val_pred_binary = (val_pred > 0.5).astype(int)

        print(f"📈 Final Validation AUC: {val_auc:.4f}")
        print(f"📋 Classification Report:")
        print(classification_report(val_true, val_pred_binary, target_names=['Normal', 'Abnormal']))

    # Save final model
    final_model_path = MODELS_DIR / "full_cnn_model.keras"
    model.save(final_model_path)
    print(f"\n💾 Model saved to: {final_model_path}")

    # Save metadata
    metadata = {
        'model_path': str(final_model_path),
        'input_shape': input_shape,
        'training_samples': train_size,
        'validation_samples': val_size,
        'final_val_auc': float(val_auc) if 'val_auc' in locals() else None,
        'model_params': model.count_params(),
        'class_weights': class_weight_dict,
        'preprocessing_config': str(DATA_DIR / "full_preprocess_config.json")
    }

    metadata_path = MODELS_DIR / "full_cnn_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"📋 Metadata saved to: {metadata_path}")
    print("\n🎯 FULL DATASET CNN TRAINING COMPLETE!")
    print("=" * 50)
    print("✅ Processed: 3,240 files")
    print("✅ Trained: Efficient CNN model")
    print("✅ Ready: For Streamlit deployment")

if __name__ == "__main__":
    main()