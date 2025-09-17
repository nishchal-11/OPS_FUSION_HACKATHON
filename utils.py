"""
Utility functions for heart sound analysis.
Common functions used across notebooks and the Streamlit app.
"""

import librosa
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

def load_audio(file_path: str, target_sr: int = 8000) -> Tuple[np.ndarray, int]:
    """
    Load audio file and convert to target sample rate.
    
    Args:
        file_path: Path to audio file
        target_sr: Target sample rate in Hz
        
    Returns:
        Tuple of (audio_data, sample_rate)
    """
    try:
        audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
        return audio, sr
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return np.array([]), 0

def preprocess_audio(audio: np.ndarray, sr: int, 
                    duration: float = 5.0) -> np.ndarray:
    """
    Preprocess audio: trim silence, normalize, and fix duration.
    
    Args:
        audio: Audio time series
        sr: Sample rate
        duration: Target duration in seconds
        
    Returns:
        Preprocessed audio array
    """
    # Trim leading/trailing silence
    audio = librosa.effects.trim(audio, top_db=20)[0]
    
    # Normalize amplitude
    if len(audio) > 0:
        audio = librosa.util.normalize(audio)
    
    # Fix duration: pad or crop to target length
    target_length = int(duration * sr)
    
    if len(audio) < target_length:
        # Pad with zeros
        padding = target_length - len(audio)
        audio = np.pad(audio, (0, padding), mode='constant')
    elif len(audio) > target_length:
        # Center crop
        start = (len(audio) - target_length) // 2
        audio = audio[start:start + target_length]
    
    return audio

def audio_to_melspectrogram(audio: np.ndarray, sr: int,
                           n_mels: int = 128, n_fft: int = 1024,
                           hop_length: int = 256) -> np.ndarray:
    """
    Convert audio to mel-spectrogram.
    
    Args:
        audio: Audio time series
        sr: Sample rate
        n_mels: Number of mel frequency bins
        n_fft: FFT window size
        hop_length: Hop length for STFT
        
    Returns:
        Log mel-spectrogram array (n_mels, time_frames)
    """
    # Compute mel-spectrogram
    mel_spec = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length
    )
    
    # Convert to log scale
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    
    return log_mel_spec

def create_preprocessing_config(sr: int = 8000, duration: float = 5.0,
                               n_mels: int = 128, n_fft: int = 1024,
                               hop_length: int = 256) -> Dict[str, Any]:
    """Create preprocessing configuration dictionary."""
    return {
        'sample_rate': sr,
        'duration': duration,
        'n_mels': n_mels,
        'n_fft': n_fft,
        'hop_length': hop_length,
        'expected_shape': (n_mels, int(duration * sr // hop_length) + 1)
    }

def save_preprocessing_config(config: Dict[str, Any], save_path: str):
    """Save preprocessing config to JSON file."""
    with open(save_path, 'w') as f:
        json.dump(config, f, indent=2)

def load_preprocessing_config(config_path: str) -> Dict[str, Any]:
    """Load preprocessing config from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def get_physionet_labels(physionet_dir: str) -> pd.DataFrame:
    """
    Extract labels from PhysioNet 2016 dataset structure.
    
    Args:
        physionet_dir: Path to physionet2016 directory
        
    Returns:
        DataFrame with columns: file_id, label, subset, file_path
    """
    physionet_path = Path(physionet_dir)
    all_records = []
    
    # Process each training subset (training-a through training-f)
    for subset_dir in physionet_path.glob("training-*"):
        subset_name = subset_dir.name
        
        # Look for REFERENCE.csv in this subset
        ref_file = subset_dir / "REFERENCE.csv"
        if ref_file.exists():
            # Read labels
            labels_df = pd.read_csv(ref_file, header=None, names=['file_id', 'label'])
            
            # Add subset and file path information
            labels_df['subset'] = subset_name
            labels_df['file_path'] = labels_df['file_id'].apply(
                lambda x: str(subset_dir / f"{x}.wav")
            )
            
            all_records.append(labels_df)
    
    # Combine all subsets
    if all_records:
        combined_df = pd.concat(all_records, ignore_index=True)
        
        # Map labels to binary (assuming -1=normal, 1=abnormal or similar)
        # This may need adjustment based on actual label format
        combined_df['binary_label'] = combined_df['label'].apply(
            lambda x: 'abnormal' if x == 1 else 'normal'
        )
        
        return combined_df
    else:
        print("Warning: No REFERENCE.csv files found in training subsets")
        return pd.DataFrame()

def print_dataset_summary(labels_df: pd.DataFrame):
    """Print summary statistics of the dataset."""
    print("📊 Dataset Summary")
    print("=" * 50)
    print(f"Total samples: {len(labels_df)}")
    print(f"Subsets: {labels_df['subset'].unique()}")
    print("\nLabel distribution:")
    print(labels_df['binary_label'].value_counts())
    print(f"\nClass balance: {labels_df['binary_label'].value_counts(normalize=True)}")
    print("=" * 50)