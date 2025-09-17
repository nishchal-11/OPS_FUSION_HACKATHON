@echo off
echo 🚀 Heart Sound Analysis - Quick Setup
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found. Run this from the project root directory.
    pause
    exit /b 1
)

echo 📦 Installing packages in current environment...
echo.

REM Install conda packages first for better compatibility
echo 📥 Installing conda-forge packages...
conda install -c conda-forge numpy pandas matplotlib seaborn scikit-learn librosa soundfile jupyter notebook ipykernel tqdm -y

if %errorlevel% neq 0 (
    echo ❌ Conda installation failed
    pause
    exit /b 1
)

REM Set protobuf environment variable
echo 🔧 Setting protobuf compatibility...
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

REM Install remaining packages with pip
echo 📥 Installing pip requirements...
pip install --no-cache-dir -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Pip installation failed
    pause
    exit /b 1
)

echo.
echo ✅ Installation complete!
echo 📋 Next: Open train_model.ipynb and test TensorFlow import
echo.
pause