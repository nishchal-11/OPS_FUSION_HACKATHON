"""
Heart Sound Mobile Analyzer - Ultra-Fast Analysis
Streamlit Cloud compatible version with robust error handling
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

# Safe TensorFlow import
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except:
    TF_AVAILABLE = False

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
    """Load TensorFlow Lite model safely."""
    try:
        if not TF_AVAILABLE:
            return None
            
        model_path = MODELS_DIR / "heart_sound_mobile_quantized.tflite"
        
        if not model_path.exists():
            # Try fallback models
            alternatives = [
                MODELS_DIR / "heart_sound_mobile.tflite",
                MODELS_DIR / "gpu_optimized_cnn_final.keras"
            ]
            for alt_path in alternatives:
                if alt_path.exists():
                    model_path = alt_path
                    break
        
        if not model_path.exists():
            st.error(f"❌ Model file not found: {model_path}")
            return None
        
        # Load based on file type
        if str(model_path).endswith('.tflite'):
            interpreter = tf.lite.Interpreter(model_path=str(model_path))
            interpreter.allocate_tensors()
            st.success(f"✅ TFLite Model loaded: {model_path.name}")
            return interpreter
        else:
            # Keras model
            model = tf.keras.models.load_model(str(model_path), compile=False)
            st.success(f"✅ Keras Model loaded: {model_path.name}")
            return model
            
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None

def make_prediction(model, mel_spec):
    """Make prediction with the loaded model."""
    try:
        if model is None:
            return None, None
        
        # Handle TFLite interpreter
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
        st.error(f"❌ Prediction error: {e}")
        return None, None

def preprocess_audio(audio_file):
    """Preprocess uploaded audio."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name
        
        # Load audio
        audio, sr = load_audio(tmp_path, SAMPLE_RATE)
        
        if len(audio) == 0:
            st.error("Could not load audio file")
            return None
        
        # Preprocess (trim silence, normalize, fix duration)
        from utils import preprocess_audio as preprocess_audio_utils
        audio = preprocess_audio_utils(audio, sr, AUDIO_DURATION)
        
        # Get mel spectrogram
        mel_spec = audio_to_melspectrogram(audio, sr, N_MELS, N_FFT, HOP_LENGTH)
        
        # Add batch and channel dimensions
        mel_spec = np.expand_dims(mel_spec, axis=[0, -1])
        
        os.unlink(tmp_path)
        return mel_spec, audio, sr
        
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
            ax=ax
        )
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.title('Mel-Spectrogram')
        return fig
    except:
        return None

# Main app
def main():
    st.markdown('<div class="mobile-header">❤️ Heart Sound Mobile Analyzer</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-card">
        <h3>🚀 Ultra-Fast AI Analysis</h3>
        <p>Upload heart sound audio for instant AI-powered classification</p>
        <p><strong>⚡ Lightning Fast</strong> • <strong>🎯 Accurate</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load model
    model = load_tflite_model()
    
    if model is None:
        st.warning("⚠️ Model loading failed. Please check configuration.")
        return
    
    # File uploader
    st.markdown("### 🎵 Upload Audio")
    uploaded_file = st.file_uploader(
        "Choose audio file",
        type=['wav', 'mp3', 'mp4', 'webm', 'ogg', 'm4a']
    )
    
    if uploaded_file:
        st.info(f"📁 File: {uploaded_file.name}")
        
        # Process
        with st.spinner("🔄 Processing audio..."):
            result = preprocess_audio(uploaded_file)
            
            if result[0] is not None:
                mel_spec, audio, sr = result
                
                # Make prediction
                with st.spinner("🧠 Analyzing..."):
                    prediction, confidence = make_prediction(model, mel_spec)
                
                if prediction:
                    # Display result
                    st.markdown("""<div class="result-card">""", unsafe_allow_html=True)
                    
                    if prediction == "Normal":
                        st.markdown(f'<div class="normal">✅ Normal Heart Sound</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="abnormal">⚠️ Abnormal Heart Sound</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Confidence:** {confidence*100:.1f}%", unsafe_allow_html=True)
                    st.markdown("""</div>""", unsafe_allow_html=True)
                    
                    # Visualization
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Waveform**")
                        fig_wave = plt.figure(figsize=(10, 3))
                        plt.plot(audio)
                        plt.title("Audio Waveform")
                        st.pyplot(fig_wave)
                        plt.close(fig_wave)
                    
                    with col2:
                        st.markdown("**Mel-Spectrogram**")
                        fig_spec = plot_spectrogram(mel_spec, sr)
                        if fig_spec:
                            st.pyplot(fig_spec)
                            plt.close(fig_spec)
            else:
                st.error("Failed to process audio")

if __name__ == "__main__":
    main()
