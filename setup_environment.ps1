# Heart Sound Analysis - Environment Setup Script
# Run with: powershell -ExecutionPolicy Bypass -File setup_environment.ps1

Write-Host "🚀 Setting up Heart Sound Analysis Environment..." -ForegroundColor Green

# Check if conda is available
$condaAvailable = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaAvailable) {
    Write-Host "❌ Conda not found. Please install Miniconda or Anaconda first." -ForegroundColor Red
    exit 1
}

# Environment name
$envName = "heart-analysis"

Write-Host "📦 Creating conda environment: $envName" -ForegroundColor Yellow

# Create environment with Python 3.9 (stable with TensorFlow)
conda create -n $envName python=3.9 -y

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create conda environment" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Environment created successfully" -ForegroundColor Green

# Activate environment
Write-Host "🔧 Activating environment..." -ForegroundColor Yellow
conda activate $envName

# Install conda-forge packages first (better compatibility)
Write-Host "📥 Installing conda-forge packages..." -ForegroundColor Yellow
conda install -c conda-forge numpy pandas matplotlib seaborn scikit-learn librosa soundfile jupyter notebook ipykernel tqdm -y

# Install pip packages (TensorFlow and specialized packages)
Write-Host "📥 Installing pip packages..." -ForegroundColor Yellow
pip install --no-cache-dir -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install requirements" -ForegroundColor Red
    exit 1
}

# Set environment variable for protobuf compatibility
Write-Host "🔧 Setting protobuf compatibility..." -ForegroundColor Yellow
conda env config vars set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python -n $envName

# Install Jupyter kernel for the environment
Write-Host "🔧 Installing Jupyter kernel..." -ForegroundColor Yellow
python -m ipykernel install --user --name $envName --display-name "Heart Analysis (Python 3.9)"

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart your terminal/VS Code" -ForegroundColor White  
Write-Host "  2. Run: conda activate $envName" -ForegroundColor White
Write-Host "  3. Open train_model.ipynb and select 'Heart Analysis' kernel" -ForegroundColor White
Write-Host "  4. Run the TensorFlow test cell to verify installation" -ForegroundColor White

Write-Host "`n🎯 Environment ready for full dataset training!" -ForegroundColor Green