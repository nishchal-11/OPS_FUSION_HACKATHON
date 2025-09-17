#!/usr/bin/env python3
"""
Phase 1 Validation Test Script
Tests all implemented components to ensure they work correctly.
"""

import sys
import os
sys.path.append('.')

from config import *
from utils import *
import tensorflow as tf
import numpy as np
import json
import pandas as pd
from pathlib import Path

def test_model_loading():
    """Test 1: Model Loading"""
    print('1. Testing Model Loading...')
    try:
        model_path = MODELS_DIR / 'gpu_optimized_cnn_final.keras'
        if not model_path.exists():
            print(f'❌ Model file not found: {model_path}')
            return False

        model = tf.keras.models.load_model(model_path)
        print('✅ Model loaded successfully')
        print(f'   Model input shape: {model.input_shape}')
        print(f'   Model output shape: {model.output_shape}')
        print(f'   Model summary:')
        model.summary(print_fn=lambda x: print(f'     {x}'))
        return True
    except Exception as e:
        print(f'❌ Model loading failed: {e}')
        return False

def test_metadata_loading():
    """Test 2: Configuration Loading"""
    print('\n2. Testing Configuration...')
    try:
        metadata_path = MODELS_DIR / 'gpu_optimized_metadata.json'
        if not metadata_path.exists():
            print(f'❌ Metadata file not found: {metadata_path}')
            return False

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print('✅ Model metadata loaded')
        print(f'   Training date: {metadata.get("training_date", "N/A")}')
        print(f'   Best validation AUC: {metadata.get("best_val_auc", "N/A")}')
        print(f'   Training epochs: {metadata.get("epochs", "N/A")}')
        return True
    except Exception as e:
        print(f'❌ Metadata loading failed: {e}')
        return False

def test_preprocessing_config():
    """Test 3: Preprocessing Config"""
    print('\n3. Testing Preprocessing Configuration...')
    try:
        config_path = MODELS_DIR / 'preprocess_config.json'
        if not config_path.exists():
            print(f'❌ Preprocessing config file not found: {config_path}')
            return False

        preprocess_config = load_preprocessing_config(config_path)
        print('✅ Preprocessing config loaded')
        print(f'   Sample rate: {preprocess_config.get("sample_rate", "N/A")}')
        print(f'   Duration: {preprocess_config.get("duration", "N/A")}')
        print(f'   Mel bins: {preprocess_config.get("n_mels", "N/A")}')
        print(f'   Expected shape: {preprocess_config.get("expected_shape", "N/A")}')
        return True
    except Exception as e:
        print(f'❌ Preprocessing config failed: {e}')
        return False

def test_dataset_loading():
    """Test 4: Dataset Loading"""
    print('\n4. Testing Dataset Loading...')
    try:
        dataset_path = DATA_DIR / 'full_processed_dataset.csv'
        if not dataset_path.exists():
            print(f'❌ Dataset file not found: {dataset_path}')
            return False

        df = pd.read_csv(dataset_path)
        print('✅ Dataset loaded successfully')
        print(f'   Total samples: {len(df)}')
        print(f'   Columns: {list(df.columns)}')
        print(f'   Label distribution:')
        print(f'     {df["label"].value_counts().to_dict()}')
        print(f'   Split distribution:')
        print(f'     {df["split"].value_counts().to_dict()}')
        return True
    except Exception as e:
        print(f'❌ Dataset loading failed: {e}')
        return False

def test_spectrogram_loading():
    """Test 5: Spectrogram Loading"""
    print('\n5. Testing Spectrogram Loading...')
    try:
        # Test normal spectrograms
        normal_dir = SPECTROGRAMS_DIR / 'normal'
        if normal_dir.exists():
            normal_files = list(normal_dir.glob('*.npy'))
            if normal_files:
                sample_spec = np.load(normal_files[0])
                print(f'✅ Normal spectrograms found: {len(normal_files)} files')
                print(f'   Sample spectrogram shape: {sample_spec.shape}')
            else:
                print('❌ No normal spectrogram files found')
                return False
        else:
            print(f'❌ Normal spectrograms directory not found: {normal_dir}')
            return False

        # Test abnormal spectrograms
        abnormal_dir = SPECTROGRAMS_DIR / 'abnormal'
        if abnormal_dir.exists():
            abnormal_files = list(abnormal_dir.glob('*.npy'))
            if abnormal_files:
                print(f'✅ Abnormal spectrograms found: {len(abnormal_files)} files')
            else:
                print('❌ No abnormal spectrogram files found')
                return False
        else:
            print(f'❌ Abnormal spectrograms directory not found: {abnormal_dir}')
            return False

        return True
    except Exception as e:
        print(f'❌ Spectrogram loading failed: {e}')
        return False

def test_audio_processing():
    """Test 6: Audio Processing Pipeline"""
    print('\n6. Testing Audio Processing Pipeline...')
    try:
        # Create synthetic test audio
        sr = SAMPLE_RATE
        duration = AUDIO_DURATION
        t = np.linspace(0, duration, int(duration * sr))

        # Generate test signal (simple sine wave)
        test_audio = 0.5 * np.sin(2 * np.pi * 100 * t)  # 100 Hz sine wave

        print('✅ Test audio generated')
        print(f'   Audio length: {len(test_audio)} samples')
        print(f'   Duration: {len(test_audio)/sr:.2f} seconds')

        # Test preprocessing
        processed_audio = preprocess_audio(test_audio, sr, duration)
        print('✅ Audio preprocessing successful')
        print(f'   Processed length: {len(processed_audio)} samples')

        # Test spectrogram conversion
        mel_spec = audio_to_melspectrogram(processed_audio, sr, N_MELS, N_FFT, HOP_LENGTH)
        print('✅ Mel-spectrogram conversion successful')
        print(f'   Spectrogram shape: {mel_spec.shape}')

        # Test model input preparation
        mel_spec_expanded = np.expand_dims(mel_spec, axis=[0, -1])
        print('✅ Model input preparation successful')
        print(f'   Model input shape: {mel_spec_expanded.shape}')

        return True
    except Exception as e:
        print(f'❌ Audio processing failed: {e}')
        return False

def test_model_prediction():
    """Test 7: Model Prediction"""
    print('\n7. Testing Model Prediction...')
    try:
        # Load model
        model = tf.keras.models.load_model(MODELS_DIR / 'gpu_optimized_cnn_final.keras')

        # Create test input
        sr = SAMPLE_RATE
        duration = AUDIO_DURATION
        t = np.linspace(0, duration, int(duration * sr))
        test_audio = 0.5 * np.sin(2 * np.pi * 100 * t)

        # Process audio
        processed_audio = preprocess_audio(test_audio, sr, duration)
        mel_spec = audio_to_melspectrogram(processed_audio, sr, N_MELS, N_FFT, HOP_LENGTH)
        model_input = np.expand_dims(mel_spec, axis=[0, -1])

        # Make prediction
        prediction = model.predict(model_input, verbose=0)
        confidence = float(prediction[0][0])
        predicted_class = "Abnormal" if confidence > CLASSIFICATION_THRESHOLD else "Normal"

        print('✅ Model prediction successful')
        print(f'   Raw prediction: {prediction[0][0]:.4f}')
        print(f'   Predicted class: {predicted_class}')
        print(f'   Confidence: {confidence:.1%}')

        return True
    except Exception as e:
        print(f'❌ Model prediction failed: {e}')
        return False

def main():
    """Run all validation tests"""
    print('=' * 60)
    print('PHASE 1 VALIDATION: Complete System Check')
    print('=' * 60)
    print()

    tests = [
        test_model_loading,
        test_metadata_loading,
        test_preprocessing_config,
        test_dataset_loading,
        test_spectrogram_loading,
        test_audio_processing,
        test_model_prediction
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    print('=' * 60)
    print('VALIDATION RESULTS SUMMARY')
    print('=' * 60)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f'{i}. {test.__name__.replace("_", " ").title()}: {status}')

    print()
    print(f'Overall: {passed}/{total} tests passed')

    if passed == total:
        print('🎉 ALL TESTS PASSED! System is ready for deployment.')
    else:
        print('⚠️  Some tests failed. Please check the errors above.')

    print('=' * 60)

if __name__ == "__main__":
    main()