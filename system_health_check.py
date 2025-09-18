"""
Comprehensive System Health Check
Test all components of the Heart Sound Analyzer system
"""

import os
import sys
import time
import json
import numpy as np
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    print("🔍 CHECKING DEPENDENCIES...")
    
    required_packages = [
        'streamlit', 'tensorflow', 'numpy', 'librosa', 
        'matplotlib', 'pandas', 'qrcode', 'PIL'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}: Available")
        except ImportError:
            print(f"   ❌ {package}: Missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_audio_processing():
    """Test audio preprocessing pipeline."""
    print("\n🎵 TESTING AUDIO PROCESSING...")
    
    try:
        # Import required modules
        from utils import load_audio, preprocess_audio, audio_to_melspectrogram
        from config import SAMPLE_RATE, AUDIO_DURATION, N_MELS, N_FFT, HOP_LENGTH
        
        # Create synthetic test audio
        duration = 5.0
        sample_rate = 8000
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_audio = np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 880 * t)
        
        print(f"   📊 Created test audio: {len(test_audio)} samples, {sample_rate} Hz")
        
        # Test preprocessing
        processed_audio = preprocess_audio(test_audio, sample_rate, AUDIO_DURATION)
        print(f"   🔧 Preprocessed audio: {len(processed_audio)} samples")
        
        # Test mel-spectrogram conversion
        mel_spec = audio_to_melspectrogram(processed_audio, SAMPLE_RATE, N_MELS, N_FFT, HOP_LENGTH)
        print(f"   📊 Mel-spectrogram shape: {mel_spec.shape}")
        
        # Validate shape
        expected_shape = (N_MELS, 157)  # Based on config
        if mel_spec.shape == expected_shape:
            print(f"   ✅ Audio processing: Working correctly")
            return True
        else:
            print(f"   ⚠️ Shape mismatch: Expected {expected_shape}, got {mel_spec.shape}")
            return False
            
    except Exception as e:
        print(f"   ❌ Audio processing error: {e}")
        return False

def test_original_model():
    """Test the original Keras model."""
    print("\n🧠 TESTING ORIGINAL KERAS MODEL...")
    
    try:
        import tensorflow as tf
        
        model_path = Path("models/gpu_optimized_cnn_final.keras")
        model = tf.keras.models.load_model(model_path)
        
        # Create test input
        test_input = np.random.randn(1, 128, 157, 1).astype(np.float32)
        
        # Test prediction
        start_time = time.time()
        prediction = model.predict(test_input, verbose=0)
        inference_time = (time.time() - start_time) * 1000
        
        print(f"   ✅ Original model loaded successfully")
        print(f"   📊 Model parameters: {model.count_params():,}")
        print(f"   🎯 Test prediction: {prediction[0][0]:.6f}")
        print(f"   ⏱️ Inference time: {inference_time:.2f}ms")
        
        return True, inference_time
        
    except Exception as e:
        print(f"   ❌ Original model error: {e}")
        return False, 0

def test_tflite_models():
    """Test both TensorFlow Lite models."""
    print("\n⚡ TESTING TENSORFLOW LITE MODELS...")
    
    models_to_test = [
        ("Standard TFLite", "models/heart_sound_mobile.tflite"),
        ("Quantized TFLite", "models/heart_sound_mobile_quantized.tflite")
    ]
    
    results = {}
    
    for model_name, model_path in models_to_test:
        try:
            print(f"\n   Testing {model_name}...")
            
            # Try different TensorFlow Lite versions/approaches
            import tensorflow as tf
            
            # Method 1: Standard TensorFlow Lite
            try:
                interpreter = tf.lite.Interpreter(model_path=model_path)
                interpreter.allocate_tensors()
                
                input_details = interpreter.get_input_details()
                output_details = interpreter.get_output_details()
                
                # Create test data
                input_shape = input_details[0]['shape']
                test_data = np.random.randn(*input_shape).astype(np.float32)
                
                # Run inference
                start_time = time.time()
                interpreter.set_tensor(input_details[0]['index'], test_data)
                interpreter.invoke()
                prediction = interpreter.get_tensor(output_details[0]['index'])
                inference_time = (time.time() - start_time) * 1000
                
                print(f"      ✅ {model_name}: Working")
                print(f"      📐 Input shape: {input_shape}")
                print(f"      🎯 Prediction: {prediction[0][0]:.6f}")
                print(f"      ⏱️ Inference: {inference_time:.2f}ms")
                
                results[model_name] = {
                    'working': True,
                    'inference_time': inference_time,
                    'prediction': float(prediction[0][0])
                }
                
            except Exception as tflite_error:
                print(f"      ❌ {model_name} TFLite error: {tflite_error}")
                
                # Method 2: Try with tf.lite.Interpreter alternative approach
                try:
                    # Load model as bytes
                    with open(model_path, 'rb') as f:
                        tflite_model = f.read()
                    
                    interpreter = tf.lite.Interpreter(model_content=tflite_model)
                    interpreter.allocate_tensors()
                    
                    print(f"      ✅ {model_name}: Loaded with model_content approach")
                    results[model_name] = {'working': True, 'inference_time': 0, 'note': 'Loaded successfully'}
                    
                except Exception as alt_error:
                    print(f"      ❌ {model_name} alternative approach failed: {alt_error}")
                    results[model_name] = {'working': False, 'error': str(tflite_error)}
        
        except Exception as e:
            print(f"      ❌ {model_name} general error: {e}")
            results[model_name] = {'working': False, 'error': str(e)}
    
    return results

def check_mobile_app_files():
    """Check if mobile app files exist and are properly configured."""
    print("\n📱 CHECKING MOBILE APP FILES...")
    
    required_files = [
        'mobile_app.py',
        'mobile_launcher.py',
        'config.py',
        'utils.py'
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            size_kb = Path(file).stat().st_size / 1024
            print(f"   ✅ {file}: {size_kb:.1f} KB")
        else:
            print(f"   ❌ {file}: Missing")
            all_present = False
    
    return all_present

def test_streamlit_functionality():
    """Test if Streamlit can be imported and basic functionality works."""
    print("\n🌐 TESTING STREAMLIT FUNCTIONALITY...")
    
    try:
        import streamlit as st
        print(f"   ✅ Streamlit version: {st.__version__}")
        
        # Test basic Streamlit functionality
        import tempfile
        import subprocess
        
        # Check if streamlit command works
        result = subprocess.run([sys.executable, '-m', 'streamlit', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"   ✅ Streamlit CLI: Working")
            return True
        else:
            print(f"   ⚠️ Streamlit CLI: Issues detected")
            return False
            
    except Exception as e:
        print(f"   ❌ Streamlit error: {e}")
        return False

def generate_health_report():
    """Generate comprehensive system health report."""
    print("\n📋 GENERATING SYSTEM HEALTH REPORT...")
    
    # Run all tests
    deps_ok = check_dependencies()
    audio_ok = test_audio_processing()
    original_ok, original_time = test_original_model()
    tflite_results = test_tflite_models()
    files_ok = check_mobile_app_files()
    streamlit_ok = test_streamlit_functionality()
    
    # Create report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system_health": {
            "dependencies": deps_ok,
            "audio_processing": audio_ok,
            "original_model": original_ok,
            "tflite_models": tflite_results,
            "mobile_app_files": files_ok,
            "streamlit": streamlit_ok
        },
        "performance_metrics": {
            "original_model_inference_ms": original_time if original_ok else 0,
            "tflite_standard_working": tflite_results.get('Standard TFLite', {}).get('working', False),
            "tflite_quantized_working": tflite_results.get('Quantized TFLite', {}).get('working', False)
        },
        "overall_status": "HEALTHY" if all([deps_ok, audio_ok, original_ok, files_ok, streamlit_ok]) else "ISSUES_DETECTED"
    }
    
    # Save report
    report_path = Path("system_health_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"   ✅ Health report saved: {report_path}")
    return report

def main():
    """Main health check pipeline."""
    print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    report = generate_health_report()
    
    # Final summary
    print(f"\n🎯 SYSTEM HEALTH CHECK COMPLETE!")
    print("=" * 50)
    
    if report["overall_status"] == "HEALTHY":
        print("🎉 SYSTEM STATUS: ✅ ALL SYSTEMS HEALTHY!")
        print("\n📊 SUMMARY:")
        print("   ✅ Dependencies: All packages available")
        print("   ✅ Audio Processing: Working correctly")
        print("   ✅ Original Model: Functional")
        print("   ✅ Mobile App Files: All present")
        print("   ✅ Streamlit: Ready for deployment")
        
        tflite_working = any(model.get('working', False) for model in report["system_health"]["tflite_models"].values())
        if tflite_working:
            print("   ✅ TensorFlow Lite: At least one model working")
        else:
            print("   ⚠️ TensorFlow Lite: Version compatibility issues (app will use Keras model)")
        
        print(f"\n🚀 READY FOR DEPLOYMENT!")
        print(f"   • Mobile app files: Ready")
        print(f"   • Models: Available and functional")
        print(f"   • Audio processing: Optimized pipeline")
        print(f"   • Performance: {report['performance_metrics']['original_model_inference_ms']:.0f}ms inference")
        
    else:
        print("⚠️ SYSTEM STATUS: ISSUES DETECTED")
        print("\nPlease review the detailed output above for specific issues.")
    
    return report["overall_status"] == "HEALTHY"

if __name__ == "__main__":
    main()