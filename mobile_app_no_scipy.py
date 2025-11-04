"""
❤️ Heart Sound Mobile Analyzer - FINAL VERSION
Ultra-Fast Analysis - Streamlit Cloud Compatible
Python 3.13 - NO scipy/librosa/TensorFlow dependencies
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile
import os
import json
from pathlib import Path
from PIL import Image
import io
import warnings
warnings.filterwarnings('ignore')
import wave

# Try lightweight TensorFlow Lite Runtime (Python 3.13 compatible)
try:
    import tflite_runtime.interpreter as tflite
    TF_AVAILABLE = True
    USE_TF_LITE_RUNTIME = True
except ImportError:
    # Fallback to full TensorFlow (if available)
    try:
        import tensorflow as tf
        TF_AVAILABLE = True
        USE_TF_LITE_RUNTIME = False
    except ImportError:
        TF_AVAILABLE = False
        tflite = None
        tf = None

# Import config
from config import *

# Page config
st.set_page_config(
    page_title="❤️ Heart Sound Mobile Analyzer",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS styling
st.markdown("""
<style>
    .main .block-container { padding: 1rem; }
    .mobile-header { 
        font-size: 2rem; 
        font-weight: bold; 
        text-align: center; 
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .mobile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .normal { color: #28a745; font-weight: bold; font-size: 1.3rem; }
    .abnormal { color: #dc3545; font-weight: bold; font-size: 1.3rem; }
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 25px;
    }
</style>
""", unsafe_allow_html=True)

# ===== AUDIO PROCESSING (NO LIBROSA) =====

def load_wav_audio(file_path, target_sr=8000):
    """Load WAV audio file without librosa."""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            
            # Read audio data
            audio_data = wav_file.readframes(n_frames)
            
            # Convert byte data to numpy array
            audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # Normalize to [-1, 1]
            if sample_width == 2:
                audio = audio / 32768.0
            elif sample_width == 1:
                audio = (audio - 128) / 128.0
            
            # Convert to mono if stereo
            if n_channels == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
            
            # Resample if needed (simple downsampling)
            if framerate != target_sr:
                ratio = target_sr / framerate
                new_length = int(len(audio) * ratio)
                audio = np.interp(
                    np.linspace(0, len(audio)-1, new_length),
                    np.arange(len(audio)),
                    audio
                )
            
            return audio, target_sr
    except Exception as e:
        st.error(f"Error loading audio: {e}")
        return np.array([]), 8000

def preprocess_audio_simple(audio, sr, duration=5.0):
    """Preprocess audio - NO librosa."""
    try:
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        # Fix duration
        target_length = int(duration * sr)
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
        else:
            audio = audio[:target_length]
        
        return audio
    except Exception as e:
        st.error(f"Error preprocessing: {e}")
        return audio

def simple_spectrogram(audio, sr, n_mels=128, n_fft=1024, hop_length=256):
    """Compute mel-spectrogram without librosa using numpy FFT."""
    try:
        # Compute STFT
        mel_spec_list = []
        for i in range(0, len(audio) - n_fft, hop_length):
            frame = audio[i:i + n_fft]
            # Apply Hann window
            window = np.hanning(n_fft)
            windowed = frame * window
            # FFT
            fft = np.fft.rfft(windowed)
            mag = np.abs(fft)
            mel_spec_list.append(mag)
        
        mel_spec = np.array(mel_spec_list).T
        
        # Simple log scale
        mel_spec = np.log(mel_spec + 1e-9)
        
        # Normalize to n_mels bins (simple binning)
        if mel_spec.shape[0] > n_mels:
            # Downsample frequency
            indices = np.linspace(0, mel_spec.shape[0]-1, n_mels).astype(int)
            mel_spec = mel_spec[indices, :]
        
        return mel_spec
    except Exception as e:
        st.error(f"Spectrogram error: {e}")
        return None

@st.cache_resource
def load_tflite_model():
    """Load TensorFlow Lite model - Python 3.13 compatible."""
    try:
        if not TF_AVAILABLE:
            st.error("❌ TensorFlow not available")
            return None
        
        # Try .tflite models first
        model_paths = [
            MODELS_DIR / "heart_sound_mobile_quantized.tflite",
            MODELS_DIR / "heart_sound_mobile.tflite",
            MODELS_DIR / "gpu_optimized_cnn_final.keras",
        ]
        
        for model_path in model_paths:
            if not model_path.exists():
                continue
            
            try:
                # Load TFLite model
                if str(model_path).endswith('.tflite'):
                    if USE_TF_LITE_RUNTIME:
                        interpreter = tflite.Interpreter(model_path=str(model_path))
                    else:
                        interpreter = tf.lite.Interpreter(model_path=str(model_path))
                    
                    interpreter.allocate_tensors()
                    st.success(f"✅ Model loaded: {model_path.name}")
                    return interpreter
                    
                else:
                    # Try Keras model
                    if not USE_TF_LITE_RUNTIME and tf is not None:
                        model = tf.keras.models.load_model(str(model_path), compile=False)
                        st.success(f"✅ Keras model loaded: {model_path.name}")
                        return model
                        
            except Exception as e:
                st.warning(f"⚠️ Could not load {model_path.name}: {e}")
                continue
        
        st.error("❌ No compatible model found")
        return None
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def make_prediction(model, mel_spec):
    """Make prediction - works with both TFLite and Keras."""
    try:
        if model is None:
            return None, None
        
        # Get input/output details
        if hasattr(model, 'get_input_details'):
            input_details = model.get_input_details()
            output_details = model.get_output_details()
            
            # Prepare input
            input_data = mel_spec.astype(np.float32)
            model.set_tensor(input_details[0]['index'], input_data)
            
            # Run inference
            model.invoke()
            
            # Get output
            output = model.get_tensor(output_details[0]['index'])
            confidence = float(output[0][0])
        else:
            # Keras model
            output = model.predict(mel_spec, verbose=0)
            confidence = float(output[0][0])
        
        # Classify
        prediction = "Abnormal" if confidence > CLASSIFICATION_THRESHOLD else "Normal"
        return prediction, confidence
        
    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")
        return None, None

def process_audio_file(audio_file):
    """Process uploaded audio file."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name
        
        # Load audio
        audio, sr = load_wav_audio(tmp_path, SAMPLE_RATE)
        
        if len(audio) == 0:
            st.error("Could not load audio file")
            return None, None, None
        
        # Preprocess
        audio_proc = preprocess_audio_simple(audio, sr, AUDIO_DURATION)
        
        # Get spectrogram
        mel_spec = simple_spectrogram(audio_proc, sr, N_MELS, N_FFT, HOP_LENGTH)
        
        if mel_spec is None:
            st.error("Failed to compute spectrogram")
            return None, None, None
        
        # Add batch and channel dimensions
        mel_spec = np.expand_dims(mel_spec, axis=[0, -1])
        
        os.unlink(tmp_path)
        return mel_spec, audio_proc, sr
        
    except Exception as e:
        st.error(f"Audio processing error: {e}")
        return None, None, None

def plot_waveform(audio):
    """Plot waveform."""
    try:
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.plot(audio, linewidth=0.5)
        ax.set_title("Audio Waveform")
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        return fig
    except Exception as e:
        st.warning(f"Could not plot waveform: {e}")
        return None

def plot_spectrogram_simple(mel_spec):
    """Plot spectrogram using matplotlib."""
    try:
        fig, ax = plt.subplots(figsize=(12, 4))
        im = ax.imshow(
            mel_spec[0, :, :, 0],
            aspect='auto',
            origin='lower',
            cmap='viridis',
            interpolation='nearest'
        )
        ax.set_title('Mel-Spectrogram')
        ax.set_xlabel('Time Frame')
        ax.set_ylabel('Mel Frequency Bin')
        plt.colorbar(im, ax=ax, label='dB')
        plt.tight_layout()
        return fig
    except Exception as e:
        st.warning(f"Could not plot spectrogram: {e}")
        return None

# ===== MAIN APP =====

def main():
    """Main application."""
    st.markdown('<div class="mobile-header">❤️ Heart Sound Mobile Analyzer</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-card">
        <h3>🚀 Ultra-Fast AI Analysis</h3>
        <p>Upload heart sound audio for instant AI-powered classification</p>
        <p><strong>⚡ Lightning Fast</strong> • <strong>🎯 Accurate</strong> • <strong>📱 Mobile Optimized</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if TensorFlow is available
    if not TF_AVAILABLE:
        st.error("❌ TensorFlow is not installed. Models cannot be loaded.")
        return
    
    # Load model
    model = load_tflite_model()
    
    if model is None:
        st.warning("⚠️ Model loading failed - app may not function correctly")
        st.stop()
    
    # File uploader section
    st.markdown("### 🎵 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose a heart sound audio file (WAV format recommended)",
        type=['wav', 'mp3', 'mp4', 'webm', 'ogg', 'm4a'],
        help="Supported formats: WAV, MP3, MP4, WebM, OGG, M4A"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.info(f"📁 File: {uploaded_file.name} ({file_size_mb:.2f} MB)")
        
        # Process button
        if st.button("🔍 Analyze Heart Sound", use_container_width=True):
            with st.spinner("🔄 Processing audio..."):
                result = process_audio_file(uploaded_file)
                
                if result[0] is not None:
                    mel_spec, audio_proc, sr = result
                    
                    # Make prediction
                    with st.spinner("🧠 Running AI analysis..."):
                        prediction, confidence = make_prediction(model, mel_spec)
                    
                    if prediction is not None:
                        # Display result
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        
                        if prediction == "Normal":
                            st.markdown(f'<div class="normal">✅ NORMAL HEART SOUND</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="abnormal">⚠️ ABNORMAL HEART SOUND</div>', unsafe_allow_html=True)
                        
                        st.markdown(f"**Confidence Score:** {confidence*100:.1f}%", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Visualizations
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🌊 Waveform")
                            fig_wave = plot_waveform(audio_proc)
                            if fig_wave:
                                st.pyplot(fig_wave, use_container_width=True)
                                plt.close(fig_wave)
                        
                        with col2:
                            st.subheader("🎵 Spectrogram")
                            fig_spec = plot_spectrogram_simple(mel_spec)
                            if fig_spec:
                                st.pyplot(fig_spec, use_container_width=True)
                                plt.close(fig_spec)
                        
                        st.success("✅ Analysis complete!")
                    else:
                        st.error("Failed to make prediction")
                else:
                    st.error("Failed to process audio")

if __name__ == "__main__":
    main()
