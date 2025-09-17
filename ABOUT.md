# OPS Fusion — Heart Sound Analyzer (Deep Dive)

A complete, hackathon-ready system to record heart sounds on a phone, transfer them to a desktop app, and classify them as Normal or Abnormal using a CNN trained on PhysioNet 2016. This document explains the project end‑to‑end, including architecture, key files, data flow, training, deployment, and troubleshooting.

---

## 1) What this project does

- Mobile web app to record heart sounds (via QR code from the desktop app).
- Streamlit desktop app to upload/inspect audio, run inference, and visualize results.
- Data pipeline to preprocess heart sounds to mel‑spectrograms.
- GPU‑optimized training scripts to train a compact CNN classifier.
- Launchers and validation scripts to verify the whole system.

---

## 2) Quick file index (name → purpose)

Top level
- `app.py` — Main Streamlit analyzer: upload/demo audio, analyze, show results (diagnosis, confidence, waveform, spectrogram, insights) + QR integration.
- `mobile_recorder.py` — Mobile‑optimized Streamlit page that captures audio in the browser using MediaRecorder/getUserMedia with live waveform and download.
- `qr_generator.py` — Utilities to build network URL for the recorder, render QR code in the main app, and show mobile workflow instructions.
- `launcher.py` — Starts both Streamlit apps (main at 8501, recorder at 8502), checks dependencies, prints local+network URLs, and monitors processes.
- `master_launcher.py`, `quick_mobile_launcher.py` — Alternative launch helpers (optional).
- `config.py` — Central config: paths, audio preprocessing constants, model constants, UI defaults.
- `utils.py` — Audio helpers: librosa‑based loading, trimming/normalizing/fixed‑length padding, mel‑spectrogram conversion, (de)serializing preprocessing configs, dataset label helpers.
- `README.md` — Short overview and quick start.
- `ABOUT.md` — This detailed explanation document.
- `requirements.txt` — Python deps for runtime and training.
- `setup.py`, `setup_environment.ps1`, `install_requirements.bat`, `commands.ps1` — Optional setup helpers on Windows.
- `mobile_access_test.py` — Prints local network IP and checks server reachability for phone access.
- `phase1_validation.py` — Self‑check of core assets: model, metadata, dataset availability, spectrogram cache, preprocessing, and a sample prediction.
- `phase2_validation.py` — Validates QR generation, recorder features, basic HTTP reachability, and integration imports.

Data and models
- `data/physionet2016/` — Original dataset layout (training‑a … training‑f, REFERENCE.csv labels, etc.).
- `data/spectrograms/{normal,abnormal}/` — Cached mel‑spectrograms as .npy for fast training.
- `data/full_processed_dataset.csv` — Index of all processed files with labels, splits, and spectrogram paths.
- `models/gpu_optimized_cnn_final.keras` — Primary trained CNN used in the app.
- `models/gpu_optimized_metadata.json` — Metadata captured at training time (AUC, input shape, epochs, etc.).
- `models/tensorboard_logs/` — Training logs for TensorBoard.

Training + preprocessing
- `scripts/preprocess.py` — Deterministic, single‑process preprocessor from raw WAV → mel‑spectrogram cache, writes `preprocess_config.json` and `preprocessing_results.csv`.
- `scripts/fast_batch_process.py` — Parallel preprocessor (ProcessPoolExecutor) to build the full spectrogram cache quickly.
- `scripts/gpu_optimized_train.py` — End‑to‑end trainer that loads the processed CSV, builds a compact CNN, applies class weighting, enables GPU/mixed precision when available, tracks AUC, and saves the final model+metadata.
- `scripts/fast_cnn_train.py` — Variant training entrypoint (if present) with similar flow.

Notebooks
- `notebooks/train_model.ipynb` — Interactive exploration, preprocessing, and model training; useful for iterative experimentation.

---

## 3) End‑to‑end architecture

1. Data ingestion
   - PhysioNet 2016 WAV + labels (REFERENCE.csv in each training-* folder)
   - `utils.get_physionet_labels()` builds a single DataFrame of file_id/label/subset/file_path and maps labels to {normal, abnormal}.

2. Preprocessing → mel‑spectrograms
   - `utils.preprocess_audio()` trims silence, normalizes, and enforces a fixed duration (default 5s at 8 kHz).
   - `utils.audio_to_melspectrogram()` returns a log mel‑spectrogram (shape roughly 128 × T).
   - `scripts/fast_batch_process.py` runs the above in parallel for all files and saves .npy spectrograms to `data/spectrograms/{normal,abnormal}/` with a `full_processed_dataset.csv` manifest.

3. Model training (GPU‑optimized)
   - `scripts/gpu_optimized_train.py` builds a small CNN with Conv2D → BN → Pool → Dropout blocks, GAP, Dense, and sigmoid output.
   - Uses class weights for imbalance, early stopping by val AUC, LR reduction, checkpointing, TensorBoard, and (when available) mixed precision + GPU memory growth.
   - Saves `models/gpu_optimized_cnn_final.keras` and `models/gpu_optimized_metadata.json`.

4. Inference pipeline (Streamlit)
   - `app.py` loads the model and metadata, exposes a two‑column layout: left for upload/demo + analyze button, right for QR and mobile guide.
   - Upload path: validate file → temp write → librosa load at 8 kHz → preprocess → mel‑spectrogram → expand dims to (1, H, W, 1) → model.predict → threshold.
   - Visualization: waveform, mel‑spectrogram heatmap, and a confidence gauge, plus text insights and recommendations.

5. Mobile capture via QR
   - `qr_generator.py` finds your LAN IP, builds recorder URL (port 8502), renders a QR code and instructions in the main app.
   - `mobile_recorder.py` serves a responsive page with a big RECORD button, browser MediaRecorder integration, live waveform via WebAudio Analyser, 10‑second auto‑stop, and download.

6. Orchestration
   - `launcher.py` spawns both apps in background subprocesses, validates dependencies, prints URLs (localhost and LAN IP), and waits for readiness; cleans up on exit.

---

## 4) How to run the system (Windows PowerShell)

- Option A: One command launcher (recommended)
  ```powershell
  python launcher.py
  ```
  This starts:
  - Main Analyzer → http://localhost:8501
  - Mobile Recorder → http://localhost:8502
  It also prints the LAN URLs (e.g., http://192.168.x.x:8501/8502) for your phone.

- Option B: Start manually
  ```powershell
  streamlit run app.py --server.port 8501 --server.address 0.0.0.0
  streamlit run mobile_recorder.py --server.port 8502 --server.address 0.0.0.0
  ```

- If ports are busy
  ```powershell
  taskkill /f /im streamlit.exe /t
  ```

---

## 5) Using the apps

Desktop (Main Analyzer)
- Upload a WAV/FLAC/MP3, or pick a demo sample.
- Click “Analyze” to get:
  - Prediction: Normal vs Abnormal
  - Confidence gauge and percentage
  - Waveform and mel‑spectrogram
  - Plain‑English insights and recommendations

Mobile (Recorder)
- Scan the QR from the desktop app or open http://<your‑LAN‑IP>:8502.
- Tap RECORD, grant mic permission, record 5–10 seconds, STOP, DOWNLOAD.
- Upload the file back into the desktop app for analysis.

Note: Some mobile browsers only allow mic on HTTPS or localhost. If your phone says the mic is blocked on HTTP, see “HTTPS tunneling” below.

---

## 6) Data pipeline details

- Sample rate: 8 kHz (downsampled for compact spectrograms)
- Duration: 5 seconds per clip (padded/cropped centrally)
- Mel bins: 128; FFT: 1024; Hop: 256
- Outputs: log‑mel spectrograms saved as `.npy` arrays
- Manifest: `data/full_processed_dataset.csv` with columns like `file_id`, `label`, `spectrogram_path`, `split`

Edge cases handled
- Empty/failed loads return zeros and are skipped/flagged
- Size/type checks in `validate_audio_file()` before processing
- Temporary files are cleaned after preprocessing

---

## 7) Model details

- CNN (~110k–300k params depending on variant)
- Blocks: Conv → BN → MaxPool → Dropout (three stages) → GAP → Dense(128) → Dropout → Sigmoid
- Loss: Binary cross‑entropy
- Metrics: Accuracy, AUC
- Training extras: class weights, EarlyStopping on val AUC, ReduceLROnPlateau, TensorBoard
- Saves best model to `models/gpu_optimized_cnn.keras`, final model to `models/gpu_optimized_cnn_final.keras`, and metadata json.

---

## 8) Validation scripts

- Phase 1 (`phase1_validation.py`) checks:
  - Model and metadata load
  - Preprocessing config present
  - Spectrogram cache availability
  - Audio → mel spec → model input
  - Single inference sanity check

- Phase 2 (`phase2_validation.py`) checks:
  - HTTP reachability (localhost:8501/8502)
  - QR creation and base64 encoding
  - Mobile recorder HTML features present
  - Launcher imports and dependency check
  - App and recorder import without error

---

## 9) Networking, HTTPS, and mobile mic permissions

- LAN access: The QR uses your local IP (e.g., 192.168.x.x). Phone and PC must be on the same Wi‑Fi.
- Windows Firewall: If the phone can’t reach the app, allow python/streamlit through firewall or run as admin once.
- HTTPS requirement (some Android/iOS builds): Browsers may block getUserMedia on plain HTTP. Workarounds:
  - Use Chrome on Android (often allows mic on LAN HTTP if user‑initiated).
  - Or run a quick HTTPS tunnel (no code changes):
    - Cloudflared (recommended)
      ```powershell
      cloudflared tunnel --url http://localhost:8502
      ```
    - Ngrok
      ```powershell
      ngrok http 8502
      ```
    Use the HTTPS URL on your phone.

---

## 10) Troubleshooting

- Port is busy
  ```powershell
  taskkill /f /im streamlit.exe /t
  ```
- QR opens but page says “Browser not supported”
  - Try Chrome or Safari; ensure mic permission is allowed.
  - HTTPS tunnel if mic blocked on HTTP (see above).
- Phone can’t reach desktop URL
  - Confirm same network; use IP from `mobile_access_test.py`.
  - Temporarily disable firewall or add an allow rule.
- Model not loading in app
  - Ensure `models/gpu_optimized_cnn_final.keras` exists (train or copy).
- Upload works but analysis button missing
  - Use the new master/emergency analyze buttons added in the UI.

---

## 11) Extensibility and next steps

- Improve inference: calibration, ensembles, batch analysis, streaming.
- Export mobile recording as WAV (PCM) for maximum compatibility.
- Add Dockerfile for portable deployment.
- Add unit tests for utils and app routes.
- Package into a minimal desktop installer for demos.

---

## 12) Security and privacy

- Audio processed locally in the browser and on the desktop unless you opt into a tunnel.
- No recordings are uploaded to third‑party services by default.
- Add your own retention policy (auto‑delete temp files, redact paths in logs) if needed.

---

## 13) Credits

- Dataset: PhysioNet/CinC Challenge 2016.
- Libraries: TensorFlow, Librosa, Streamlit, NumPy/Pandas, Matplotlib/Seaborn, qrcode, PIL.

---

If anything feels unclear or you want diagrams added (e.g., data flow, model blocks), ping me and I’ll extend this doc with visuals.
