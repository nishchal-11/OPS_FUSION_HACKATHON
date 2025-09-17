# Configuration for Heart Sound Analyzer
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PHYSIONET_DIR = DATA_DIR / "physionet2016"
SPECTROGRAMS_DIR = DATA_DIR / "spectrograms"
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Audio processing settings
SAMPLE_RATE = 8000  # Target sample rate (Hz)
AUDIO_DURATION = 5.0  # Fixed duration in seconds for training
N_MELS = 128  # Number of mel frequency bins
N_FFT = 1024  # FFT window size
HOP_LENGTH = 256  # Hop length for STFT

# Model settings
BATCH_SIZE = 32  # Training batch size
LEARNING_RATE = 1e-3  # Initial learning rate
EPOCHS = 50  # Maximum training epochs
EARLY_STOPPING_PATIENCE = 8  # Early stopping patience
VALIDATION_SPLIT = 0.2  # Validation split ratio

# Classification settings
CLASSIFICATION_THRESHOLD = 0.5  # Binary classification threshold
CLASS_NAMES = ["Normal", "Abnormal"]

# Streamlit app settings
APP_PORT = 8501
QR_UPDATE_INTERVAL = 30  # Seconds to refresh QR code

# File patterns
AUDIO_EXTENSIONS = ['.wav', '.flac', '.mp3', '.webm', '.ogg', '.m4a']
MODEL_FILENAME = "heart_classifier.keras"
PREPROCESSING_CONFIG_FILENAME = "preprocess_config.json"

# Create directories if they don't exist
for directory in [DATA_DIR, SPECTROGRAMS_DIR, MODELS_DIR, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)