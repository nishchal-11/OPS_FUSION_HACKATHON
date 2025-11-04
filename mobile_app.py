"""
❤️ Heart Sound Mobile Analyzer
Ultra-Fast Analysis - Streamlit Cloud Compatible
Python 3.13 compatible - TensorFlow Lite only (no TensorFlow dependency)
"""

import streamlit as st
import numpy as np
import librosa
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

# Import custom modules
from config import *
from utils import *

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
                        # Use lightweight TensorFlow Lite Runtime
                        interpreter = tflite.Interpreter(model_path=str(model_path))
                    else:
                        # Use full TensorFlow
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

def preprocess_audio_file(audio_file):
    """Preprocess uploaded audio."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name
        
        # Load audio
        audio, sr = load_audio(tmp_path, SAMPLE_RATE)
        
        if len(audio) == 0:
            st.error("Could not load audio file")
            return None, None, None
        
        # Preprocess (from utils)
        audio_proc = preprocess_audio(audio, sr, AUDIO_DURATION)
        
        # Get mel spectrogram
        mel_spec = audio_to_melspectrogram(audio_proc, sr, N_MELS, N_FFT, HOP_LENGTH)
        
        # Add batch and channel dimensions
        mel_spec = np.expand_dims(mel_spec, axis=[0, -1])
        
        os.unlink(tmp_path)
        return mel_spec, audio_proc, sr
        
    except Exception as e:
        st.error(f"Audio processing error: {e}")
        return None, None, None

def plot_spectrogram(mel_spec, sr):
    """Plot mel-spectrogram."""
    try:
        fig, ax = plt.subplots(figsize=(12, 4))
        img = librosa.display.specshow(
            mel_spec[0, :, :, 0],
            sr=sr,
            hop_length=HOP_LENGTH,
            x_axis='time',
            y_axis='mel',
            ax=ax,
            cmap='viridis'
        )
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.title('Mel-Spectrogram')
        plt.tight_layout()
        return fig
    except Exception as e:
        st.warning(f"Could not plot spectrogram: {e}")
        return None

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
        st.info("This is a demo interface. Please check requirements.txt")
        return
    
    # Load model
    model = load_tflite_model()
    
    if model is None:
        st.warning("⚠️ Model loading failed - app may not function correctly")
        st.stop()
    
    # File uploader section
    st.markdown("### 🎵 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose a heart sound audio file",
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
                result = preprocess_audio_file(uploaded_file)
                
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
                            fig_wave = plt.figure(figsize=(10, 3))
                            plt.plot(audio_proc, linewidth=1)
                            plt.title("Audio Waveform")
                            plt.xlabel("Sample")
                            plt.ylabel("Amplitude")
                            plt.grid(alpha=0.3)
                            st.pyplot(fig_wave, use_container_width=True)
                            plt.close(fig_wave)
                        
                        with col2:
                            st.subheader("🎵 Mel-Spectrogram")
                            fig_spec = plot_spectrogram(mel_spec, sr)
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
