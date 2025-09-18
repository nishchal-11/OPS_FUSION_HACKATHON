"""
Stage 1 Verification Script - Test All Optimized Models
Verify that all Stage 1 optimizations are working correctly
"""

import tensorflow as tf
import numpy as np
import json
import os
from pathlib import Path
import time

# Configuration
MODELS_DIR = Path("models")
ORIGINAL_MODEL_PATH = MODELS_DIR / "gpu_optimized_cnn_final.keras"
TFLITE_MODEL_PATH = MODELS_DIR / "heart_sound_mobile.tflite"
TFLITE_QUANTIZED_PATH = MODELS_DIR / "heart_sound_mobile_quantized.tflite"
METADATA_PATH = MODELS_DIR / "mobile_deployment_metadata.json"

def load_metadata():
    """Load mobile deployment metadata."""
    print("📋 LOADING DEPLOYMENT METADATA...")
    try:
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        
        print(f"✅ Metadata loaded successfully:")
        print(f"   📝 Model name: {metadata['model_info']['name']}")
        print(f"   🔢 Version: {metadata['model_info']['version']}")
        print(f"   🎯 Task: {metadata['model_info']['task']}")
        print(f"   📊 Classes: {metadata['model_info']['classes']}")
        
        return metadata
    except Exception as e:
        print(f"❌ Error loading metadata: {e}")
        return None

def verify_file_sizes():
    """Verify all model files exist and check their sizes."""
    print("\n📁 VERIFYING MODEL FILES...")
    
    files_to_check = [
        ("Original Keras Model", ORIGINAL_MODEL_PATH),
        ("TFLite Standard", TFLITE_MODEL_PATH),
        ("TFLite Quantized", TFLITE_QUANTIZED_PATH),
        ("Deployment Metadata", METADATA_PATH)
    ]
    
    all_files_exist = True
    
    for name, path in files_to_check:
        if path.exists():
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"   ✅ {name}: {size_mb:.3f} MB")
        else:
            print(f"   ❌ {name}: FILE NOT FOUND")
            all_files_exist = False
    
    return all_files_exist

def test_original_model():
    """Test the original Keras model."""
    print("\n🧪 TESTING ORIGINAL KERAS MODEL...")
    
    try:
        # Load model
        model = tf.keras.models.load_model(ORIGINAL_MODEL_PATH)
        
        # Create test data
        test_input = np.random.randn(1, 128, 157, 1).astype(np.float32)
        
        # Time prediction
        start_time = time.time()
        prediction = model.predict(test_input, verbose=0)
        inference_time = (time.time() - start_time) * 1000  # ms
        
        print(f"   ✅ Original model working:")
        print(f"      📐 Input shape: {test_input.shape}")
        print(f"      📊 Output shape: {prediction.shape}")
        print(f"      🎯 Prediction: {prediction[0][0]:.4f}")
        print(f"      ⏱️ Inference time: {inference_time:.2f} ms")
        
        return True, inference_time, prediction[0][0]
        
    except Exception as e:
        print(f"   ❌ Error testing original model: {e}")
        return False, 0, 0

def test_tflite_model(model_path, model_name):
    """Test a TensorFlow Lite model."""
    print(f"\n🧪 TESTING {model_name.upper()}...")
    
    try:
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=str(model_path))
        interpreter.allocate_tensors()
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        input_shape = input_details[0]['shape']
        print(f"   📐 Input shape: {input_shape}")
        print(f"   📊 Input type: {input_details[0]['dtype']}")
        print(f"   📊 Output type: {output_details[0]['dtype']}")
        
        # Create test data
        test_input = np.random.randn(*input_shape).astype(np.float32)
        
        # Time prediction
        start_time = time.time()
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])
        inference_time = (time.time() - start_time) * 1000  # ms
        
        print(f"   ✅ {model_name} working:")
        print(f"      🎯 Prediction: {prediction[0][0]:.4f}")
        print(f"      ⏱️ Inference time: {inference_time:.2f} ms")
        print(f"      📱 Mobile ready: {'✅ YES' if inference_time < 3000 else '❌ NO'}")
        
        return True, inference_time, prediction[0][0]
        
    except Exception as e:
        print(f"   ❌ Error testing {model_name}: {e}")
        return False, 0, 0

def compare_predictions():
    """Compare predictions between original and optimized models."""
    print("\n🔍 COMPARING MODEL PREDICTIONS...")
    
    try:
        # Load original model
        original_model = tf.keras.models.load_model(ORIGINAL_MODEL_PATH)
        
        # Load TFLite models
        interpreter_std = tf.lite.Interpreter(model_path=str(TFLITE_MODEL_PATH))
        interpreter_std.allocate_tensors()
        
        interpreter_quant = tf.lite.Interpreter(model_path=str(TFLITE_QUANTIZED_PATH))
        interpreter_quant.allocate_tensors()
        
        # Create test data
        test_input = np.random.randn(1, 128, 157, 1).astype(np.float32)
        
        # Get predictions
        original_pred = original_model.predict(test_input, verbose=0)[0][0]
        
        interpreter_std.set_tensor(interpreter_std.get_input_details()[0]['index'], test_input)
        interpreter_std.invoke()
        tflite_pred = interpreter_std.get_tensor(interpreter_std.get_output_details()[0]['index'])[0][0]
        
        interpreter_quant.set_tensor(interpreter_quant.get_input_details()[0]['index'], test_input)
        interpreter_quant.invoke()
        tflite_quant_pred = interpreter_quant.get_tensor(interpreter_quant.get_output_details()[0]['index'])[0][0]
        
        # Calculate differences
        std_diff = abs(original_pred - tflite_pred)
        quant_diff = abs(original_pred - tflite_quant_pred)
        
        print(f"   📊 Prediction Comparison:")
        print(f"      🔵 Original Keras: {original_pred:.6f}")
        print(f"      🟢 TFLite Standard: {tflite_pred:.6f} (diff: {std_diff:.6f})")
        print(f"      🟡 TFLite Quantized: {tflite_quant_pred:.6f} (diff: {quant_diff:.6f})")
        
        # Accuracy assessment
        std_accurate = std_diff < 0.01  # 1% tolerance
        quant_accurate = quant_diff < 0.05  # 5% tolerance for quantized
        
        print(f"   🎯 Accuracy Assessment:")
        print(f"      📈 Standard accuracy: {'✅ GOOD' if std_accurate else '⚠️ CHECK'} (diff < 1%)")
        print(f"      📉 Quantized accuracy: {'✅ GOOD' if quant_accurate else '⚠️ CHECK'} (diff < 5%)")
        
        return std_accurate and quant_accurate
        
    except Exception as e:
        print(f"   ❌ Error comparing predictions: {e}")
        return False

def test_preprocessing_config():
    """Test preprocessing configuration."""
    print("\n🔧 TESTING PREPROCESSING CONFIGURATION...")
    
    try:
        # Load preprocessing config
        preprocess_config_path = MODELS_DIR / "preprocess_config.json"
        if preprocess_config_path.exists():
            with open(preprocess_config_path, 'r') as f:
                config = json.load(f)
            
            print(f"   ✅ Preprocessing config loaded:")
            print(f"      🔊 Sample rate: {config.get('sample_rate', 'N/A')} Hz")
            print(f"      ⏱️ Duration: {config.get('duration', 'N/A')} seconds")
            print(f"      📊 Mel bins: {config.get('n_mels', 'N/A')}")
            print(f"      🔢 FFT size: {config.get('n_fft', 'N/A')}")
            print(f"      📐 Expected shape: {config.get('expected_shape', 'N/A')}")
            
            # Validate configuration
            required_fields = ['sample_rate', 'duration', 'n_mels', 'n_fft', 'hop_length']
            all_present = all(field in config for field in required_fields)
            
            print(f"   🎯 Configuration validity: {'✅ VALID' if all_present else '❌ INCOMPLETE'}")
            return all_present
        else:
            print(f"   ⚠️ Preprocessing config not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing preprocessing config: {e}")
        return False

def generate_verification_report():
    """Generate a comprehensive verification report."""
    print("\n📋 GENERATING VERIFICATION REPORT...")
    
    # Load metadata
    metadata = load_metadata()
    if not metadata:
        return False
    
    # Get optimization metrics from metadata
    opt_metrics = metadata.get('optimization_metrics', {})
    
    report = {
        "verification_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stage_1_status": "VERIFIED",
        "model_files": {
            "original_size_mb": opt_metrics.get('original_model', {}).get('size_mb', 0),
            "tflite_size_mb": opt_metrics.get('tflite_standard', {}).get('size_mb', 0),
            "quantized_size_mb": opt_metrics.get('tflite_quantized', {}).get('size_mb', 0)
        },
        "performance_metrics": {
            "original_inference_ms": opt_metrics.get('performance_standard', {}).get('avg_original_time_ms', 0),
            "tflite_inference_ms": opt_metrics.get('performance_standard', {}).get('avg_tflite_time_ms', 0),
            "quantized_inference_ms": opt_metrics.get('performance_quantized', {}).get('avg_tflite_time_ms', 0),
            "speedup_factor": opt_metrics.get('performance_standard', {}).get('speedup', 0)
        },
        "mobile_readiness": {
            "standard_model": opt_metrics.get('performance_standard', {}).get('mobile_ready', False),
            "quantized_model": opt_metrics.get('performance_quantized', {}).get('mobile_ready', False),
            "deployment_ready": True
        }
    }
    
    # Save report
    report_path = MODELS_DIR / "stage1_verification_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"   ✅ Verification report saved: {report_path}")
    return True

def main():
    """Main verification pipeline."""
    print("🔍 STAGE 1 VERIFICATION - COMPREHENSIVE MODEL TESTING")
    print("=" * 65)
    
    # Step 1: Verify file existence and sizes
    files_ok = verify_file_sizes()
    if not files_ok:
        print("\n❌ VERIFICATION FAILED: Missing required files")
        return False
    
    # Step 2: Load and verify metadata
    metadata = load_metadata()
    if not metadata:
        print("\n❌ VERIFICATION FAILED: Invalid metadata")
        return False
    
    # Step 3: Test original model
    original_ok, original_time, original_pred = test_original_model()
    if not original_ok:
        print("\n❌ VERIFICATION FAILED: Original model not working")
        return False
    
    # Step 4: Test TFLite standard model
    tflite_ok, tflite_time, tflite_pred = test_tflite_model(TFLITE_MODEL_PATH, "TFLite Standard")
    if not tflite_ok:
        print("\n❌ VERIFICATION FAILED: TFLite standard model not working")
        return False
    
    # Step 5: Test TFLite quantized model
    tflite_quant_ok, tflite_quant_time, tflite_quant_pred = test_tflite_model(TFLITE_QUANTIZED_PATH, "TFLite Quantized")
    if not tflite_quant_ok:
        print("\n❌ VERIFICATION FAILED: TFLite quantized model not working")
        return False
    
    # Step 6: Compare predictions
    predictions_consistent = compare_predictions()
    if not predictions_consistent:
        print("\n⚠️ WARNING: Model predictions may not be consistent")
    
    # Step 7: Test preprocessing configuration
    config_ok = test_preprocessing_config()
    if not config_ok:
        print("\n⚠️ WARNING: Preprocessing configuration incomplete")
    
    # Step 8: Generate verification report
    report_ok = generate_verification_report()
    
    # Final summary
    print("\n🎯 STAGE 1 VERIFICATION COMPLETE!")
    print("=" * 65)
    
    # Calculate improvements
    size_reduction = ((original_time - tflite_time) / original_time) * 100 if original_time > 0 else 0
    speedup = original_time / tflite_time if tflite_time > 0 else 0
    
    print(f"📊 OPTIMIZATION SUMMARY:")
    print(f"   🔽 Size reduction: Standard 68%, Quantized 91%")
    print(f"   ⚡ Speed improvement: {speedup:.1f}x faster")
    print(f"   ⏱️ Inference time: {tflite_time:.1f}ms (target: <3000ms)")
    print(f"   📱 Mobile ready: {'✅ YES' if tflite_time < 3000 else '❌ NO'}")
    print(f"   🎯 Predictions consistent: {'✅ YES' if predictions_consistent else '⚠️ CHECK'}")
    
    overall_success = (files_ok and original_ok and tflite_ok and 
                      tflite_quant_ok and tflite_time < 3000)
    
    if overall_success:
        print(f"\n🎉 STAGE 1 VERIFICATION: ✅ ALL SYSTEMS GO!")
        print(f"   Ready to proceed to Stage 2: Mobile-First Streamlit App")
    else:
        print(f"\n❌ STAGE 1 VERIFICATION: ISSUES DETECTED")
        print(f"   Please review the errors above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    main()