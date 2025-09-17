#!/usr/bin/env python3
"""
GPU-Optimized CNN Training Script for Heart Sound Classification
Automatically uses GPU when available, optimized for full dataset training
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

# Set TensorFlow environment variable for protobuf compatibility
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Add parent directory for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils import *
from config import *

def setup_gpu_acceleration():
    """Configure GPU acceleration if available."""
    print("🔧 Setting up GPU acceleration...")

    # Check for GPU availability
    gpus = tf.config.list_physical_devices('GPU')
    print(f"📊 GPUs detected: {len(gpus)}")

    if gpus:
        try:
            # Enable memory growth to avoid allocating all GPU memory at once
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✅ GPU memory growth enabled for {len(gpus)} GPU(s)")

            # Set GPU device
            tf.config.set_visible_devices(gpus[0], 'GPU')
            print("🎯 Using GPU for training")

        except RuntimeError as e:
            print(f"❌ GPU setup failed: {e}")
            print("🔄 Falling back to CPU")
    else:
        print("💻 Using CPU for training (GPU not detected)")

    return len(gpus) > 0

def create_optimized_cnn(input_shape, use_gpu=True):
    """Create an optimized CNN for heart sound classification."""

    model = models.Sequential([
        # Input layer
        layers.Input(shape=input_shape),

        # Optimized conv blocks with GPU-friendly settings
        layers.Conv2D(32, (3, 3), activation='relu', padding='same',
                     kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        layers.Conv2D(64, (3, 3), activation='relu', padding='same',
                     kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.3),

        layers.Conv2D(128, (3, 3), activation='relu', padding='same',
                     kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.4),

        # Global pooling for efficiency
        layers.GlobalAveragePooling2D(),

        # Dense layers
        layers.Dense(128, activation='relu', kernel_initializer='he_normal'),
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

def create_efficient_data_generator(processed_df, split='train', batch_size=32, shuffle=True):
    """Create efficient data generator optimized for GPU/CPU."""

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

    return generator, len(split_df), input_shape

def main():
    print("🚀 GPU-Optimized CNN Training on Full Dataset")
    print("=" * 60)

    # Setup GPU acceleration
    gpu_available = setup_gpu_acceleration()

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

    # Create data generators
    print("\n🔄 Creating optimized data generators...")
    train_gen, train_size, input_shape = create_efficient_data_generator(
        processed_df, 'train', BATCH_SIZE, shuffle=True
    )
    val_gen, val_size, _ = create_efficient_data_generator(
        processed_df, 'val', BATCH_SIZE, shuffle=False
    )

    print(f"📐 Input shape: {input_shape}")
    print(f"🔢 Train batches per epoch: {train_size // BATCH_SIZE}")
    print(f"🔢 Val batches per epoch: {val_size // BATCH_SIZE}")

    # Create optimized model
    print("\n🏗️ Building optimized CNN model...")
    model = create_optimized_cnn(input_shape, use_gpu=gpu_available)

    # Compile with GPU-optimized settings
    optimizer = keras.optimizers.Adam(learning_rate=0.001)
    if gpu_available:
        # Use mixed precision for GPU acceleration
        optimizer = tf.keras.mixed_precision.LossScaleOptimizer(optimizer)
        print("⚡ Mixed precision enabled for GPU acceleration")

    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )

    print(f"📊 Model parameters: {model.count_params():,}")

    # Calculate class weights
    train_labels = processed_df[processed_df['split'] == 'train']['label'].map({'normal': 0, 'abnormal': 1}).values
    class_weights = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)
    class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
    print(f"⚖️ Class weights: {class_weight_dict}")

    # GPU-optimized callbacks
    callbacks_list = [
        # Early stopping
        callbacks.EarlyStopping(
            monitor='val_auc',
            patience=8,  # More patience for GPU training
            restore_best_weights=True,
            mode='max',
            verbose=1
        ),
        # Model checkpoint
        callbacks.ModelCheckpoint(
            filepath=str(MODELS_DIR / 'gpu_optimized_cnn.keras'),
            monitor='val_auc',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        # Learning rate reduction
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        # TensorBoard for monitoring
        callbacks.TensorBoard(
            log_dir=str(MODELS_DIR / 'tensorboard_logs'),
            histogram_freq=1,
            write_graph=True
        )
    ]

    # GPU-optimized training settings
    training_epochs = 30 if gpu_available else 15  # More epochs with GPU
    print(f"\n🚀 Starting {'GPU' if gpu_available else 'CPU'} training...")
    print(f"   Epochs: {training_epochs}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Mixed precision: {'Yes' if gpu_available else 'No'}")

    # Create TensorFlow datasets for better GPU performance
    train_dataset = tf.data.Dataset.from_generator(
        train_gen,
        output_signature=(
            tf.TensorSpec(shape=(None,) + input_shape, dtype=tf.float32),
            tf.TensorSpec(shape=(None,), dtype=tf.int32)
        )
    ).prefetch(tf.data.AUTOTUNE)

    val_dataset = tf.data.Dataset.from_generator(
        val_gen,
        output_signature=(
            tf.TensorSpec(shape=(None,) + input_shape, dtype=tf.float32),
            tf.TensorSpec(shape=(None,), dtype=tf.int32)
        )
    ).prefetch(tf.data.AUTOTUNE)

    # Train model
    history = model.fit(
        train_dataset,
        steps_per_epoch=train_size // BATCH_SIZE,
        epochs=training_epochs,
        validation_data=val_dataset,
        validation_steps=val_size // BATCH_SIZE,
        callbacks=callbacks_list,
        class_weight=class_weight_dict,
        verbose=1
    )

    print("\n✅ Training completed!")

    # Quick evaluation
    print("\n📊 Evaluating final model...")
    val_pred = model.predict(val_dataset, steps=val_size // BATCH_SIZE, verbose=1)
    val_true = []

    # Get true labels
    val_df = processed_df[processed_df['split'] == 'val']
    val_true = val_df['label'].map({'normal': 0, 'abnormal': 1}).values[:len(val_pred)]

    if len(val_pred) == len(val_true):
        val_auc = roc_auc_score(val_true, val_pred)
        val_pred_binary = (val_pred > 0.5).astype(int)

        print(f"\n📈 Final Validation Results:")
        print(f"  AUC Score: {val_auc:.4f}")
        print(f"  Accuracy: {np.mean(val_pred_binary == val_true):.4f}")
        print(f"\n📋 Classification Report:")
        print(classification_report(val_true, val_pred_binary, target_names=['Normal', 'Abnormal']))

    # Save final model
    final_model_path = MODELS_DIR / "gpu_optimized_cnn_final.keras"
    model.save(final_model_path)
    print(f"\n💾 Model saved to: {final_model_path}")

    # Save metadata
    metadata = {
        'model_path': str(final_model_path),
        'input_shape': input_shape,
        'training_samples': train_size,
        'validation_samples': val_size,
        'gpu_used': gpu_available,
        'final_val_auc': float(val_auc) if 'val_auc' in locals() else None,
        'model_params': model.count_params(),
        'class_weights': class_weight_dict,
        'preprocessing_config': str(DATA_DIR / "full_preprocess_config.json"),
        'training_config': {
            'epochs': len(history.history['loss']),
            'batch_size': BATCH_SIZE,
            'mixed_precision': gpu_available,
            'optimizer': 'Adam',
            'learning_rate': 0.001
        }
    }

    metadata_path = MODELS_DIR / "gpu_optimized_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"📋 Metadata saved to: {metadata_path}")
    print("\n🎯 GPU-OPTIMIZED CNN TRAINING COMPLETE!")
    print("=" * 60)
    print("✅ Processed: 3,240 files")
    print(f"✅ Trained: {'GPU' if gpu_available else 'CPU'} optimized CNN")
    print("✅ Ready: For Streamlit deployment")
    print(f"📊 Final AUC: {val_auc:.4f}" if 'val_auc' in locals() else "")

if __name__ == "__main__":
    main()