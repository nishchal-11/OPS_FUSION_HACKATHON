#!/usr/bin/env python
"""
Quick setup script for Heart Sound Analyzer project.
Handles environment setup and dependency installation on Windows.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Set up Python virtual environment and install dependencies."""
    print("🚀 Setting up Heart Sound Analyzer environment...\n")
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Already in a virtual environment")
    else:
        print("📦 Creating virtual environment...")
        if not run_command("python -m venv venv"):
            return False
    
    print("\n📥 Installing dependencies...")
    
    # Use the appropriate pip command based on OS and venv status
    if os.name == 'nt':  # Windows
        pip_cmd = r".\venv\Scripts\python.exe -m pip"
        if not os.path.exists("venv"):
            pip_cmd = "python -m pip"
    else:  # Unix-like
        pip_cmd = "./venv/bin/python -m pip"
        if not os.path.exists("venv"):
            pip_cmd = "python -m pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        return False
    
    print("\n🔍 Verifying installation...")
    
    # Test critical imports
    test_imports = [
        "import numpy",
        "import pandas", 
        "import librosa",
        "import tensorflow as tf",
        "import streamlit",
        "import qrcode"
    ]
    
    for test_import in test_imports:
        if not run_command(f"{pip_cmd.replace('-m pip', '')} -c \"{test_import}\""):
            print(f"❌ Failed to import: {test_import}")
            return False
    
    print("\n✅ Environment setup complete!")
    print("\n🎯 Next steps:")
    print("1. Activate the environment: .\\venv\\Scripts\\Activate.ps1")
    print("2. Start Jupyter: jupyter notebook")
    print("3. Open notebooks/train_model.ipynb to begin preprocessing")
    print("4. Or run the app directly: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)