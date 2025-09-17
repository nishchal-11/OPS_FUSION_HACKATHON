#!/usr/bin/env python
"""
Quick validation script to test if everything is working before training.
"""

import warnings
warnings.filterwarnings('ignore')

from utils import *
from config import *

def test_pipeline():
    print("🧪 Running preprocessing pipeline validation...")
    
    # Test 1: Dataset loading
    print("\n1. Testing dataset loading...")
    labels_df = get_physionet_labels(str(PHYSIONET_DIR))
    print(f"   ✅ Found {len(labels_df)} labeled files")
    print(f"   📊 Label distribution: {labels_df['binary_label'].value_counts().to_dict()}")
    
    if len(labels_df) == 0:
        print("   ❌ No labels found!")
        return False
    
    # Test 2: Audio loading
    print("\n2. Testing audio loading...")
    sample_file = labels_df.iloc[0]
    print(f"   🔍 Testing file: {sample_file['file_id']} ({sample_file['binary_label']})")
    
    audio, sr = load_audio(sample_file['file_path'], target_sr=SAMPLE_RATE)
    if len(audio) == 0:
        print("   ❌ Failed to load audio!")
        return False
    
    print(f"   ✅ Loaded: {len(audio)} samples at {sr}Hz ({len(audio)/sr:.1f}s)")
    
    # Test 3: Audio preprocessing
    print("\n3. Testing audio preprocessing...")
    processed = preprocess_audio(audio, sr, duration=AUDIO_DURATION)
    print(f"   ✅ Processed: {len(processed)} samples ({len(processed)/sr:.1f}s)")
    
    # Test 4: Spectrogram conversion
    print("\n4. Testing spectrogram conversion...")
    mel_spec = audio_to_melspectrogram(
        processed, sr, 
        n_mels=N_MELS, n_fft=N_FFT, hop_length=HOP_LENGTH
    )
    expected_shape = (N_MELS, int(AUDIO_DURATION * sr // HOP_LENGTH) + 1)
    print(f"   ✅ Spectrogram: {mel_spec.shape} (expected ~{expected_shape})")
    
    # Test 5: Configuration
    print("\n5. Testing configuration...")
    config = create_preprocessing_config()
    print(f"   ✅ Config created with {len(config)} parameters")
    
    print(f"\n🎉 All tests PASSED! Ready for training.")
    print(f"   📁 Dataset: {len(labels_df)} files")
    print(f"   🎵 Audio: {SAMPLE_RATE}Hz, {AUDIO_DURATION}s")
    print(f"   📊 Spectrograms: {N_MELS} mel bins")
    
    return True

if __name__ == "__main__":
    success = test_pipeline()
    if not success:
        print("\n❌ Validation failed! Please check the errors above.")
        exit(1)
    else:
        print("\n✅ Environment is ready for training!")
        exit(0)