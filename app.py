"""
Heart Sound Analyzer - Streamlit Web Application
A complete heart sound classification system with mobile QR recording capability.
"""

import streamlit as st
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import tempfile
import os
import json
import qrcode
from PIL import Image
import io
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from config import *
from utils import *

# Set page configuration
st.set_page_config(
    page_title="Heart Sound Analyzer",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .upload-section {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Load the trained CNN model."""
    try:
        from tensorflow.keras.models import load_model
        model_path = MODELS_DIR / "gpu_optimized_cnn_final.keras"
        model = load_model(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_data
def load_model_metadata():
    """Load model metadata."""
    try:
        metadata_path = MODELS_DIR / "gpu_optimized_metadata.json"
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Could not load model metadata: {e}")
        return {}

def preprocess_uploaded_audio(audio_file):
    """Preprocess uploaded audio file for prediction."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_path = tmp_file.name

        # Load and preprocess audio
        audio, sr = load_audio(tmp_path, SAMPLE_RATE)
        if len(audio) == 0:
            raise ValueError("Could not load audio file")

        # Preprocess audio
        processed_audio = preprocess_audio(audio, sr, AUDIO_DURATION)

        # Convert to mel-spectrogram
        mel_spec = audio_to_melspectrogram(
            processed_audio, SAMPLE_RATE,
            N_MELS, N_FFT, HOP_LENGTH
        )

        # Add channel dimension and batch dimension
        mel_spec = np.expand_dims(mel_spec, axis=[0, -1])

        # Clean up temp file
        os.unlink(tmp_path)

        return mel_spec, processed_audio, sr

    except Exception as e:
        st.error(f"Error preprocessing audio: {e}")
        return None, None, None

def make_prediction(model, preprocessed_audio):
    """Make prediction using the loaded model."""
    try:
        prediction = model.predict(preprocessed_audio, verbose=0)
        confidence = float(prediction[0][0])
        predicted_class = "Abnormal" if confidence > CLASSIFICATION_THRESHOLD else "Normal"
        return predicted_class, confidence
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        return None, None

def plot_spectrogram(audio, sr, title="Mel-Spectrogram"):
    """Create and return a matplotlib figure of the spectrogram."""
    fig, ax = plt.subplots(figsize=(10, 4))

    # Create mel-spectrogram
    mel_spec = audio_to_melspectrogram(audio, sr, N_MELS, N_FFT, HOP_LENGTH)

    # Plot
    img = librosa.display.specshow(
        mel_spec, sr=sr, x_axis='time', y_axis='mel',
        fmax=4000, ax=ax, cmap='viridis'
    )

    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.colorbar(img, ax=ax, format='%+2.0f dB')
    plt.tight_layout()

    return fig

def generate_qr_code(data):
    """Generate QR code for the given data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img

def get_confidence_color(confidence):
    """Get color class based on confidence level."""
    if confidence > 0.8:
        return "confidence-high"
    elif confidence > 0.6:
        return "confidence-medium"
    else:
        return "confidence-low"

def create_confidence_gauge(confidence, predicted_class):
    """Create a confidence gauge visualization."""
    fig, ax = plt.subplots(figsize=(8, 2))

    # Create gauge background
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.5, fill=True, color='#f0f0f0'))

    # Create confidence bar
    if predicted_class == "Normal":
        color = '#28a745'  # Green for normal
    else:
        color = '#dc3545'  # Red for abnormal

    ax.add_patch(plt.Rectangle((0, 0), confidence, 0.5, fill=True, color=color))

    # Add threshold line
    ax.axvline(x=CLASSIFICATION_THRESHOLD, color='black', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(CLASSIFICATION_THRESHOLD + 0.02, 0.6, f'Threshold\n({CLASSIFICATION_THRESHOLD})',
            fontsize=8, verticalalignment='bottom')

    # Styling
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    ax.set_yticks([])
    ax.set_title(f'Confidence: {confidence:.1%} ({predicted_class})', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

def get_medical_insights(predicted_class, confidence):
    """Generate medical insights based on prediction."""
    insights = {
        "Normal": {
            "description": "The heart sound appears to be within normal parameters.",
            "recommendations": [
                "Continue regular health check-ups",
                "Maintain a healthy lifestyle",
                "Monitor for any changes in symptoms"
            ],
            "next_steps": "No immediate medical intervention required"
        },
        "Abnormal": {
            "description": "The heart sound shows characteristics that may indicate an abnormality.",
            "recommendations": [
                "Consult a cardiologist for professional evaluation",
                "Consider additional diagnostic tests (ECG, echocardiography)",
                "Keep a record of symptoms and when they occur"
            ],
            "next_steps": "Schedule an appointment with a healthcare provider"
        }
    }

    base_insights = insights[predicted_class]

    # Adjust based on confidence
    if confidence < 0.6:
        base_insights["confidence_note"] = "⚠️ Low confidence prediction - additional testing recommended"
    elif confidence < 0.8:
        base_insights["confidence_note"] = "⚡ Moderate confidence - consider confirmatory tests"
    else:
        base_insights["confidence_note"] = "✅ High confidence prediction"

    return base_insights

def plot_waveform(audio, sr, title="Audio Waveform"):
    """Create waveform visualization."""
    fig, ax = plt.subplots(figsize=(10, 3))

    time = np.linspace(0, len(audio)/sr, len(audio))
    ax.plot(time, audio, color='#1f77b4', linewidth=1)

    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

def load_demo_spectrogram(label_type="normal"):
    """Load a demo spectrogram from processed data."""
    try:
        spectrograms_dir = SPECTROGRAMS_DIR / label_type
        if spectrograms_dir.exists():
            # Get list of available spectrograms
            spec_files = list(spectrograms_dir.glob("*.npy"))
            if spec_files:
                # Load a random spectrogram
                demo_file = np.random.choice(spec_files)
                spectrogram = np.load(demo_file)

                # Convert back to audio-like data for demo (approximate)
                # This is a simplified reconstruction for demo purposes
                return spectrogram, str(demo_file.name)
        return None, None
    except Exception as e:
        st.warning(f"Could not load demo data: {e}")
        return None, None

def create_sample_audio(duration=5.0, sr=8000, label="normal"):
    """Create a synthetic sample audio for demonstration."""
    try:
        # Generate synthetic heart sound-like audio
        t = np.linspace(0, duration, int(duration * sr))

        if label == "normal":
            # Normal heart sound: regular lub-dub pattern
            freq1, freq2 = 50, 120  # Approximate heart sound frequencies
            audio = (0.3 * np.sin(2 * np.pi * freq1 * t) +
                    0.2 * np.sin(2 * np.pi * freq2 * t) +
                    0.1 * np.random.normal(0, 0.1, len(t)))
        else:
            # Abnormal heart sound: irregular pattern with murmurs
            freq1, freq2, freq_murmur = 45, 110, 200
            audio = (0.3 * np.sin(2 * np.pi * freq1 * t) +
                    0.2 * np.sin(2 * np.pi * freq2 * t) +
                    0.15 * np.sin(2 * np.pi * freq_murmur * t) +
                    0.1 * np.random.normal(0, 0.15, len(t)))

        # Normalize
        audio = librosa.util.normalize(audio)

        return audio, sr

    except Exception as e:
        st.error(f"Error creating sample audio: {e}")
        return None, None

def demo_prediction_analysis():
    """Provide detailed analysis for demo predictions."""
    analysis_text = {
        "normal": """
        **Normal Heart Sound Analysis:**
        - Regular rhythm with clear S1 and S2 sounds
        - No audible murmurs or extra heart sounds
        - Normal frequency range (20-200 Hz dominant)
        - Consistent amplitude throughout cardiac cycle
        """,
        "abnormal": """
        **Abnormal Heart Sound Analysis:**
        - Irregular rhythm with possible murmurs
        - Additional heart sounds detected
        - Abnormal frequency components present
        - Variations in amplitude suggesting pathology
        """
    }
    return analysis_text

def safe_model_prediction(model, preprocessed_audio):
    """Safe model prediction with comprehensive error handling."""
    try:
        if model is None:
            raise ValueError("Model not loaded")

        if preprocessed_audio is None or preprocessed_audio.shape[0] == 0:
            raise ValueError("Invalid preprocessed audio data")

        # Check input shape compatibility
        expected_shape = model.input_shape
        actual_shape = preprocessed_audio.shape

        if len(actual_shape) != len(expected_shape):
            raise ValueError(f"Input shape mismatch: expected {expected_shape}, got {actual_shape}")

        prediction = model.predict(preprocessed_audio, verbose=0)

        if prediction is None or len(prediction) == 0:
            raise ValueError("Model returned empty prediction")

        confidence = float(prediction[0][0])

        # Validate confidence range
        if not (0 <= confidence <= 1):
            st.warning(f"Unexpected confidence value: {confidence}")
            confidence = max(0, min(1, confidence))  # Clamp to valid range

        predicted_class = "Abnormal" if confidence > CLASSIFICATION_THRESHOLD else "Normal"

        return predicted_class, confidence

    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        st.error("Please check your audio file and try again.")
        return None, None

def validate_audio_file(uploaded_file):
    """Validate uploaded audio file."""
    try:
        if uploaded_file is None:
            return False, "No file uploaded"

        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if uploaded_file.size > max_size:
            return False, f"File too large ({uploaded_file.size/1024/1024:.1f}MB). Maximum size: 50MB"

        # Check file extension
        file_name = uploaded_file.name.lower()
        valid_extensions = ['.wav', '.flac', '.mp3', '.webm', '.ogg', '.m4a', '.mp4']
        if not any(file_name.endswith(ext) for ext in valid_extensions):
            return False, f"Unsupported file format. Supported: {', '.join(valid_extensions)}"

        return True, "File validated successfully"

    except Exception as e:
        return False, f"File validation error: {str(e)}"

def handle_processing_error(error_msg, context=""):
    """Handle and display processing errors with helpful suggestions."""
    st.error(f"❌ Processing Error: {error_msg}")

    with st.expander("🔧 Troubleshooting Tips"):
        st.write("**Common Solutions:**")
        st.write("• Ensure your audio file is not corrupted")
        st.write("• Check that the file format is supported (.wav, .flac, .mp3, .webm, .ogg, .m4a)")
        st.write("• Try converting your audio to WAV format")
        st.write("• Ensure the audio is at least 3 seconds long")
        st.write("• Check that your audio has sufficient quality (>8kHz sample rate)")

        if context:
            st.write(f"**Context:** {context}")

    st.info("💡 If the problem persists, try uploading a different audio file.")

def main():
    """Main Streamlit application."""

    # Header
    st.markdown('<h1 class="main-header">❤️ Heart Sound Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Heart Sound Classification System")
    st.markdown("---")

    # Quick guide
    st.info("🚀 **Quick Start:** Upload an audio file → Click '🔍 Analyze Heart Sound' → Get instant results!")

    # EMERGENCY TOP BUTTON - Always visible
    st.markdown("### 🔥 MASTER ANALYZE BUTTON (ALWAYS WORKS)")
    master_analyze_button = st.button("🔍 MASTER ANALYZE - CLICK HERE!", type="primary", use_container_width=True)
    if master_analyze_button:
        st.success("✅ Master button clicked! Proceeding with analysis...")

    st.markdown("---")

    # Load model and metadata
    model = load_model()
    metadata = load_model_metadata()

    if model is None:
        st.error("❌ Could not load the trained model. Please check the models directory.")
        return

    # Sidebar with information
    with st.sidebar:
        st.header("📊 Model Information")

        if metadata:
            st.write(f"**Training Date:** {metadata.get('training_date', 'N/A')}")
            st.write(f"**Validation AUC:** {metadata.get('best_val_auc', 'N/A')}")
            st.write(f"**Model Type:** CNN")
            st.write(f"**Input Shape:** {metadata.get('input_shape', 'N/A')}")

        st.markdown("---")
        st.header("🔧 Configuration")
        st.write(f"Sample Rate: {SAMPLE_RATE} Hz")
        st.write(f"Duration: {AUDIO_DURATION}s")
        st.write(f"Mel Bins: {N_MELS}")

        st.markdown("---")
        st.header("📱 Mobile Recording")
        st.info("Upload audio files or use the QR code feature for mobile recording.")

    # Main content
    col1, col2 = st.columns([2, 1])

    # Add visual guide to analysis section
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <h2 style='color: #1f77b4;'>⬇️ Analysis Section Below ⬇️</h2>
    </div>
    """, unsafe_allow_html=True)

    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.header("🎵 Audio Analysis")

        # File upload
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=AUDIO_EXTENSIONS,
            help="Upload a heart sound recording (.wav, .flac, .mp3, .webm, .ogg, .m4a, .mp4)"
        )

        # Show upload status
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: **{uploaded_file.name}** ({uploaded_file.size/1024:.1f} KB)")
            st.info("🎯 **Next:** Click the **ANALYZE** button below to process your recording!")
        else:
            st.info("💡 **Upload a heart sound recording** or select a demo option above, then click **ANALYZE**")

        # Demo section
        st.markdown("---")
        st.subheader("🎯 Quick Demo")
        demo_option = st.selectbox(
            "Try with sample audio:",
            ["None", "Normal Heart Sound (Synthetic)", "Abnormal Heart Sound (Synthetic)",
             "Real Dataset Sample (Normal)", "Real Dataset Sample (Abnormal)"],
            index=1,  # Default to "Normal Heart Sound (Synthetic)"
            help="Select a demo audio file to test the system"
        )

        if demo_option != "None":
            st.info("💡 **Demo Mode:** Using pre-generated or synthetic audio for testing. Upload your own audio for real analysis.")

        # Demo info
        if demo_option in ["Real Dataset Sample (Normal)", "Real Dataset Sample (Abnormal)"]:
            st.info("📊 Using real spectrograms from the PhysioNet 2016 dataset for demonstration.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced Analysis button with better visibility
        st.markdown("""
        <style>
        .analyze-button-container {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .analyze-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            display: inline-block;
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            transition: all 0.3s ease;
            width: 100%;
            max-width: 300px;
        }
        .analyze-button:hover {
            background: linear-gradient(135deg, #45a049 0%, #4CAF50 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        .button-instructions {
            color: white;
            font-size: 14px;
            margin-top: 10px;
            opacity: 0.9;
        }
        .waiting-indicator {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        # ALWAYS show the analyze button - debug the visibility issue
        st.markdown("---")
        st.subheader("🔍 ANALYSIS SECTION")
        
        # Debug info
        st.write(f"**Debug:** uploaded_file = {uploaded_file is not None}, demo_option = '{demo_option}'")
        
        # Show status based on upload/demo selection
        if uploaded_file is None and demo_option == "None":
            st.markdown('<div class="waiting-indicator">⏳ Please upload a file or select a demo option above, then click ANALYZE</div>', unsafe_allow_html=True)
        else:
            st.success("✅ Ready to analyze! Click the button below.")
        
        # ALWAYS show the button container
        st.markdown('<div class="analyze-button-container">', unsafe_allow_html=True)
        st.markdown('<p class="button-instructions">🎯 CLICK HERE TO ANALYZE YOUR HEART SOUND!</p>', unsafe_allow_html=True)

        # Analysis button - ALWAYS VISIBLE
        analyze_button = st.button(
            "🔍 ANALYZE HEART SOUND", 
            type="primary", 
            use_container_width=True,
            help="Click to analyze your uploaded audio file or selected demo"
        )

        st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional backup button for visibility
        st.markdown("---")
        st.error("🔥 EMERGENCY BUTTON - If the main button doesn't work, use this:")
        backup_button = st.button("🚀 EMERGENCY ANALYZE BUTTON", type="secondary", use_container_width=True)

    with col2:
        st.header("📱 Mobile Heart Sound Recording")

        # Import QR generator
        try:
            from qr_generator import display_mobile_qr_component
            display_mobile_qr_component(port=8502)
        except ImportError:
            st.warning("⚠️ QR generator not available. Using basic QR code.")

            # Fallback to basic QR code
            st.info("Scan this QR code with your phone to record heart sounds directly.")

            # Generate basic QR code for current session
            qr_data = f"heartsound://{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            qr_img = generate_qr_code(qr_data)

            # Convert PIL image to bytes for Streamlit
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG')
            qr_bytes = buf.getvalue()

            st.image(qr_bytes, caption="Scan to Record", use_column_width=True)

            # Basic instructions
            with st.expander("📋 Recording Instructions"):
                st.markdown("""
                1. **Scan QR Code** with your phone's camera
                2. **Open the link** in your mobile browser
                3. **Record** heart sounds for 5-10 seconds
                4. **Download** and upload back to this app
                5. **Get Analysis** results instantly
                """)

    # Analysis logic - check all three buttons
    if analyze_button or backup_button or master_analyze_button:
        st.info("🔍 Button clicked! Starting analysis...")
        audio_data = None
        audio_sr = None

        # Handle uploaded file
        if uploaded_file is not None:
            # Validate file first
            is_valid, validation_msg = validate_audio_file(uploaded_file)
            if not is_valid:
                st.error(f"❌ {validation_msg}")
                return

            with st.spinner("Processing uploaded audio..."):
                try:
                    preprocessed, audio_data, audio_sr = preprocess_uploaded_audio(uploaded_file)
                    if preprocessed is None or audio_data is None:
                        handle_processing_error("Failed to process audio file", "Audio preprocessing failed")
                        return
                except Exception as e:
                    handle_processing_error(str(e), "Audio preprocessing error")
                    return

        # Handle demo selection
        elif demo_option != "None":
            with st.spinner("Loading demo audio..."):
                if "Synthetic" in demo_option:
                    st.write("🎵 Generating synthetic audio...")
                    # Generate synthetic audio
                    label = "normal" if "Normal" in demo_option else "abnormal"
                    audio_data, audio_sr = create_sample_audio(label=label)
                    demo_type = "synthetic"
                    if audio_data is not None:
                        st.success(f"✅ Demo loaded: {demo_option} ({len(audio_data)} samples)")
                    else:
                        st.error("Could not generate demo audio.")
                        return
                elif "Real Dataset" in demo_option:
                    # Load real dataset sample
                    label = "normal" if "Normal" in demo_option else "abnormal"
                    spectrogram, filename = load_demo_spectrogram(label)
                    if spectrogram is not None:
                        # Convert spectrogram back to approximate audio for demo
                        try:
                            audio_data = librosa.feature.inverse.mel_to_audio(
                                spectrogram, sr=SAMPLE_RATE, n_fft=N_FFT, hop_length=HOP_LENGTH
                            )
                            audio_sr = SAMPLE_RATE
                            demo_type = f"real dataset ({filename})"
                            st.success(f"✅ Demo loaded: {demo_option}")
                        except Exception as e:
                            st.error(f"Could not reconstruct audio from spectrogram: {e}")
                            return
                    else:
                        st.error("Could not load demo data. Please upload your own audio file.")
                        return
                else:
                    # Legacy demo options
                    label = "normal" if "Normal" in demo_option else "abnormal"
                    audio_data, audio_sr = create_sample_audio(label=label)
                    demo_type = "legacy demo"
                    st.success(f"Loaded demo: {demo_option}")

                # Preprocess demo audio for model
                if audio_data is not None:
                    processed_audio = preprocess_audio(audio_data, audio_sr, AUDIO_DURATION)
                    mel_spec = audio_to_melspectrogram(
                        processed_audio, SAMPLE_RATE,
                        N_MELS, N_FFT, HOP_LENGTH
                    )
                    preprocessed = np.expand_dims(mel_spec, axis=[0, -1])
                else:
                    st.error("Could not prepare demo audio for analysis.")
                    return

        else:
            st.error("🚨 **No audio to analyze!**")
            st.info("**To analyze heart sounds:**")
            st.write("1. **Upload an audio file** using the file uploader above, OR")
            st.write("2. **Select a demo option** from the dropdown above")
            st.write("3. Then click the **ANALYZE** button")
            return

        if audio_data is not None and audio_sr is not None:
            st.info("✅ Audio data ready, starting prediction...")
            # Make prediction with error handling
            with st.spinner("Analyzing heart sound..."):
                st.write("🧠 Loading model and making prediction...")
                predicted_class, confidence = safe_model_prediction(model, preprocessed)
                st.write(f"🎯 Prediction complete: {predicted_class} ({confidence:.1%})")

            if predicted_class is None:
                st.error("❌ Could not complete analysis. Please try again.")
                return
            
            # Display results
            st.markdown("---")
            st.header("📋 Analysis Results")

            # Main result card
            st.markdown('<div class="result-card">', unsafe_allow_html=True)

            col_result1, col_result2, col_result3 = st.columns([1, 1, 1])

            with col_result1:
                st.subheader("🏥 Diagnosis")
                if predicted_class == "Normal":
                    st.success(f"**{predicted_class}** Heart Sound")
                    st.write("✅ Within normal range")
                else:
                    st.error(f"**{predicted_class}** Heart Sound")
                    st.write("⚠️ Requires medical attention")

            with col_result2:
                st.subheader("📊 Confidence Level")
                confidence_color = get_confidence_color(confidence)
                st.markdown(f'<p class="{confidence_color}">**{confidence:.1%}**</p>', unsafe_allow_html=True)

                # Confidence interpretation
                if confidence > 0.8:
                    st.write("🔥 Very High Confidence")
                elif confidence > 0.6:
                    st.write("⚡ Moderate Confidence")
                else:
                    st.write("🤔 Low Confidence")

            with col_result3:
                st.subheader("🎯 Prediction Details")
                st.write(f"**Threshold:** {CLASSIFICATION_THRESHOLD}")
                st.write(f"**Model:** CNN Classifier")
                st.write(f"**Dataset:** PhysioNet 2016")

                st.markdown('</div>', unsafe_allow_html=True)

                # Enhanced visualizations
                st.subheader("� Visual Analysis")

                col_viz1, col_viz2 = st.columns(2)

                with col_viz1:
                    try:
                        st.write("**Confidence Gauge:**")
                        gauge_fig = create_confidence_gauge(confidence, predicted_class)
                        st.pyplot(gauge_fig)
                    except Exception as e:
                        st.warning(f"Could not create confidence gauge: {e}")

                with col_viz2:
                    try:
                        st.write("**Audio Waveform:**")
                        waveform_fig = plot_waveform(audio_data, audio_sr, "Heart Sound Waveform")
                        st.pyplot(waveform_fig)
                    except Exception as e:
                        st.warning(f"Could not create waveform plot: {e}")

                # Spectrogram
                try:
                    st.write("**Mel-Spectrogram:**")
                    spec_fig = plot_spectrogram(audio_data, audio_sr, "Heart Sound Analysis")
                    st.pyplot(spec_fig)
                except Exception as e:
                    st.warning(f"Could not create spectrogram: {e}")
                    st.info("This may be due to audio processing issues, but the prediction is still valid.")

                # Medical insights
                st.subheader("🩺 Medical Insights")

                insights = get_medical_insights(predicted_class, confidence)

                # Description
                st.info(f"**Analysis Summary:** {insights['description']}")

                # Confidence note
                if "confidence_note" in insights:
                    if confidence < 0.6:
                        st.error(insights['confidence_note'])
                    elif confidence < 0.8:
                        st.warning(insights['confidence_note'])
                    else:
                        st.success(insights['confidence_note'])

                # Recommendations
                st.write("**Recommendations:**")
                for rec in insights['recommendations']:
                    st.write(f"• {rec}")

                # Next steps
                st.write(f"**Next Steps:** {insights['next_steps']}")

                # Technical details in expander
                with st.expander("🔧 Technical Details"):
                    col_tech1, col_tech2 = st.columns(2)

                    with col_tech1:
                        st.write("**Audio Properties:**")
                        st.write(f"- Sample Rate: {audio_sr} Hz")
                        st.write(f"- Duration: {len(audio_data)/audio_sr:.1f} seconds")
                        st.write(f"- Processed Length: {AUDIO_DURATION} seconds")
                        st.write(f"- Mel Bins: {N_MELS}")

                    with col_tech2:
                        st.write("**Model Performance:**")
                        if metadata:
                            st.write(f"- Training AUC: {metadata.get('best_val_auc', 'N/A')}")
                            st.write(f"- Training Date: {metadata.get('training_date', 'N/A')}")
                        st.write(f"- Classification Threshold: {CLASSIFICATION_THRESHOLD}")
                        st.write(f"- Prediction Confidence: {confidence:.3f}")

                # Waveform visualization
                st.subheader("🌊 Audio Waveform Visualization")
                fig_waveform = plot_waveform(audio_data, audio_sr, "Heart Sound Waveform")
                st.pyplot(fig_waveform)

                # Confidence gauge
                st.subheader("Gauge")
                fig_gauge = create_confidence_gauge(confidence, predicted_class)
                st.pyplot(fig_gauge)

                # Medical insights
                st.subheader("🩺 Medical Insights")
                insights = get_medical_insights(predicted_class, confidence)
                st.write(f"**Description:** {insights['description']}")
                st.write("**Recommendations:**")
                for rec in insights["recommendations"]:
                    st.write(f"- {rec}")
                st.write(f"**Next Steps:** {insights['next_steps']}")
                if "confidence_note" in insights:
                    st.write(f"**Note:** {insights['confidence_note']}")

                # Demo analysis
                st.subheader("📈 Demo Analysis Details")
                demo_analysis_text = demo_prediction_analysis()
                if predicted_class.lower() in demo_analysis_text:
                    st.markdown(demo_analysis_text[predicted_class.lower()])

                # Demo analysis insights
                if demo_option != "None" and "demo_type" in locals():
                    st.subheader("🎓 Demo Analysis Insights")

                    analysis_text = demo_prediction_analysis()
                    label_key = "normal" if "Normal" in demo_option else "abnormal"

                    if label_key in analysis_text:
                        st.info(analysis_text[label_key])

                    # Technical note
                    with st.expander("🔧 Technical Note"):
                        if "synthetic" in demo_type:
                            st.write("""
                            **Synthetic Audio Generation:**
                            - Normal: Regular lub-dub pattern with fundamental frequencies
                            - Abnormal: Added murmur components and irregular patterns
                            - Used for testing system functionality
                            """)
                        elif "real dataset" in demo_type:
                            st.write("""
                            **Real Dataset Sample:**
                            - From PhysioNet 2016 heart sound database
                            - Pre-processed and validated by medical experts
                            - Represents actual clinical recordings
                            """)

                # Medical disclaimer
                st.markdown("---")
                st.warning("""
                ⚠️ **Medical Disclaimer**

                This tool is for educational and research purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.
                """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using TensorFlow, Streamlit, and Librosa</p>
        <p>PhysioNet 2016 Dataset • CNN Classification Model</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()