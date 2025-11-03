# Heart Sound Analyzer 🫀

A hackathon-ready heart sound classification system that records audio via mobile QR code and classifies Normal vs Abnormal heart sounds using deep learning.

## Quick Start

### 1. Environment Setup (Windows)

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Mobile App

```powershell
# Windows - Double click or run:
start_mobile_app.bat

# Or use PowerShell:
.\start_mobile_app.ps1

# Or directly with Python:
python -m streamlit run mobile_app.py --server.port 8503
```

This will start:
- **Mobile App**: http://localhost:8503 (mobile-optimized interface)

### 3. Use the System

1. **Desktop**: Open http://localhost:8503 in your browser
2. **Mobile**: Connect your phone to the same WiFi and visit http://192.168.20.26:8503
3. **Upload** a heart sound audio file or use demo samples
4. **Analyze** to get instant Normal/Abnormal classification with AI insights

## Project Structure

```
OPS_fusion/
├── data/
│   ├── physionet2016/          # PhysioNet 2016 heart sound dataset
│   └── spectrograms/           # Processed spectrogram cache
├── notebooks/
│   └── train_model.ipynb       # Data preprocessing & model training
├── models/
│   └── gpu_optimized_cnn_final.keras  # Trained CNN model
├── scripts/
│   ├── fast_batch_process.py   # Parallel data processing
│   └── gpu_optimized_train.py  # GPU-optimized training
├── app.py                      # Main Streamlit analyzer app
├── mobile_recorder.py          # Mobile recording interface
├── qr_generator.py             # QR code generation utilities
├── launcher.py                 # Multi-app launcher script
├── config.py                   # Configuration settings
├── utils.py                    # Audio processing utilities
├── requirements.txt            # Python dependencies
└── README.md
```

## 🎙️ Mobile Recording Features

- **QR Code Access**: Scan QR code to open mobile recorder
- **Real-time Visualization**: Live audio waveform during recording
- **Auto-stop**: Automatic 10-second recording limit
- **Cross-platform**: Works on iOS Safari, Chrome Mobile, Firefox Mobile
- **Privacy-focused**: Audio processed locally on device
- **Easy Download**: One-click WAV file download for analysis

## Development Phases

- ✅ **Phase A**: Project scaffold & environment
- ✅ **Phase B**: Data preprocessing pipeline
- ✅ **Phase C**: CNN model training
- ✅ **Phase D**: Streamlit app + QR system
- ✅ **Phase E**: Audio capture integration (Mobile recorder)
- 🔄 **Phase F**: Enhanced inference pipeline
- ⏳ **Phase G**: Demo polish & deployment

## Technical Details

- **Dataset**: PhysioNet 2016 Challenge (Normal/Abnormal heart sounds)
- **Preprocessing**: Mel-spectrogram conversion (128 bins, 8kHz)
- **Model**: Lightweight CNN for binary classification
- **Interface**: Streamlit web app with mobile QR recording
- **Target**: 70-80% validation accuracy, <2s inference time

## Hardware Requirements

- **Training**: GPU recommended (3-6 hours vs 6+ hours CPU)
- **Inference**: CPU-friendly for demo deployment
- **Storage**: ~2GB for dataset + spectrograms

---

*⚠️ Disclaimer: This is a research prototype for educational/hackathon purposes only. Not intended for medical diagnosis.*