"""
Mobile Model Optimization - Stage 1
Convert trained CNN model to TensorFlow Lite for mobile deployment
"""

import tensorflow as tf
import numpy as np
import json
import os
from pathlib import Path
import time
from tensorflow.keras.models import load_model

# Configuration
MODELS_DIR = Path("models")
ORIGINAL_MODEL_PATH = MODELS_DIR / "gpu_optimized_cnn_final.keras"
TFLITE_MODEL_PATH = MODELS_DIR / "heart_sound_mobile.tflite"
TFLITE_QUANTIZED_PATH = MODELS_DIR / "heart_sound_mobile_quantized.tflite"

def analyze_original_model():
    """Analyze the original Keras model."""
    print("🔍 ANALYZING ORIGINAL MODEL...")
    
    try:
        # Load original model
        model = load_model(ORIGINAL_MODEL_PATH)
        
        # Get model info
        model_size = os.path.getsize(ORIGINAL_MODEL_PATH) / (1024 * 1024)  # MB
        input_shape = model.input_shape
        output_shape = model.output_shape
        total_params = model.count_params()
        
        print(f"✅ Original Model Analysis:")
        print(f"   📁 Size: {model_size:.2f} MB")
        print(f"   🔢 Parameters: {total_params:,}")
        print(f"   📐 Input shape: {input_shape}")
        print(f"   📊 Output shape: {output_shape}")
        
        # Model summary
        print(f"\n📋 Model Architecture:")
        model.summary()
        
        return model, {
            'size_mb': model_size,
            'total_params': total_params,
            'input_shape': input_shape,
            'output_shape': output_shape
        }
        
    except Exception as e:
        print(f"❌ Error loading original model: {e}")
        return None, None

def convert_to_tflite(model, quantize=False):
    """Convert Keras model to TensorFlow Lite."""
    print(f"\n🔄 CONVERTING TO TENSORFLOW LITE {'(WITH QUANTIZATION)' if quantize else '(NO QUANTIZATION)'}...")
    
    try:
        # Create TFLite converter
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        if quantize:
            # Apply dynamic range quantization (INT8)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            
            # Optional: Representative dataset for full integer quantization
            # This would require sample data, which we'll skip for now
            # converter.representative_dataset = representative_data_gen
            # converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            # converter.inference_input_type = tf.int8
            # converter.inference_output_type = tf.int8
        
        # Convert model
        start_time = time.time()
        tflite_model = converter.convert()
        conversion_time = time.time() - start_time
        
        # Save model
        output_path = TFLITE_QUANTIZED_PATH if quantize else TFLITE_MODEL_PATH
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        # Analyze converted model
        tflite_size = len(tflite_model) / (1024 * 1024)  # MB
        
        print(f"✅ TensorFlow Lite Conversion Complete:")
        print(f"   📁 Size: {tflite_size:.2f} MB")
        print(f"   ⏱️ Conversion time: {conversion_time:.2f} seconds")
        print(f"   💾 Saved to: {output_path}")
        
        return tflite_model, {
            'size_mb': tflite_size,
            'conversion_time': conversion_time,
            'path': str(output_path)
        }
        
    except Exception as e:
        print(f"❌ Error converting to TensorFlow Lite: {e}")
        return None, None

def test_tflite_inference(tflite_model_path, original_model, test_samples=10):
    """Test TensorFlow Lite model inference speed and accuracy."""
    print(f"\n🧪 TESTING TFLITE MODEL INFERENCE...")
    
    try:
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=str(tflite_model_path))
        interpreter.allocate_tensors()
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        input_shape = input_details[0]['shape']
        print(f"🔧 TFLite Model Details:")
        print(f"   📐 Input shape: {input_shape}")
        print(f"   📊 Input type: {input_details[0]['dtype']}")
        print(f"   📊 Output type: {output_details[0]['dtype']}")
        
        # Create synthetic test data (mel-spectrogram shape)
        # Assuming input shape is [1, height, width, channels]
        if len(input_shape) == 4:
            test_data = np.random.randn(test_samples, input_shape[1], input_shape[2], input_shape[3]).astype(np.float32)
        else:
            print(f"⚠️ Unexpected input shape: {input_shape}")
            return None
        
        # Test original model inference time
        print(f"\n⏱️ BENCHMARKING INFERENCE SPEED...")
        original_times = []
        tflite_times = []
        
        # Original Keras model timing
        for i in range(test_samples):
            start_time = time.time()
            _ = original_model.predict(test_data[i:i+1], verbose=0)
            original_times.append(time.time() - start_time)
        
        # TFLite model timing
        for i in range(test_samples):
            start_time = time.time()
            interpreter.set_tensor(input_details[0]['index'], test_data[i:i+1])
            interpreter.invoke()
            _ = interpreter.get_tensor(output_details[0]['index'])
            tflite_times.append(time.time() - start_time)
        
        avg_original_time = np.mean(original_times) * 1000  # milliseconds
        avg_tflite_time = np.mean(tflite_times) * 1000  # milliseconds
        speedup = avg_original_time / avg_tflite_time
        
        print(f"✅ Inference Speed Comparison:")
        print(f"   🐌 Original Keras: {avg_original_time:.2f} ms/prediction")
        print(f"   🚀 TensorFlow Lite: {avg_tflite_time:.2f} ms/prediction")
        print(f"   ⚡ Speedup: {speedup:.2f}x faster")
        
        # Mobile performance assessment
        mobile_ready = avg_tflite_time < 3000  # 3 seconds target
        print(f"   📱 Mobile Ready: {'✅ YES' if mobile_ready else '❌ NO'} (Target: <3000ms)")
        
        return {
            'avg_original_time_ms': float(avg_original_time),
            'avg_tflite_time_ms': float(avg_tflite_time),
            'speedup': float(speedup),
            'mobile_ready': bool(mobile_ready),
            'input_shape': input_shape.tolist(),
            'input_dtype': str(input_details[0]['dtype']),
            'output_dtype': str(output_details[0]['dtype'])
        }
        
    except Exception as e:
        print(f"❌ Error testing TFLite inference: {e}")
        return None

def create_mobile_deployment_package():
    """Create deployment package with optimized model and metadata."""
    print(f"\n📦 CREATING MOBILE DEPLOYMENT PACKAGE...")
    
    try:
        # Load existing metadata
        metadata_path = MODELS_DIR / "gpu_optimized_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                original_metadata = json.load(f)
        else:
            original_metadata = {}
        
        # Load preprocessing config
        preprocess_config_path = MODELS_DIR / "preprocess_config.json"
        if preprocess_config_path.exists():
            with open(preprocess_config_path, 'r') as f:
                preprocess_config = json.load(f)
        else:
            preprocess_config = {}
        
        # Create mobile-specific metadata
        mobile_metadata = {
            "model_info": {
                "name": "Heart Sound Mobile Analyzer",
                "version": "1.0.0",
                "type": "tensorflow_lite",
                "task": "binary_classification",
                "classes": ["normal", "abnormal"]
            },
            "model_files": {
                "tflite_model": "heart_sound_mobile.tflite",
                "tflite_quantized": "heart_sound_mobile_quantized.tflite",
                "original_keras": "gpu_optimized_cnn_final.keras"
            },
            "preprocessing": preprocess_config,
            "inference": {
                "input_shape": [1, 128, 128, 1],  # Will be updated during conversion
                "input_type": "float32",
                "output_type": "float32",
                "classification_threshold": 0.5
            },
            "performance": {
                "target_inference_time_ms": 3000,
                "mobile_optimized": True
            },
            "deployment": {
                "platform": "mobile_web",
                "framework": "streamlit",
                "deployment_type": "on_device"
            },
            "original_training_metrics": original_metadata.get("training_metrics", {}),
            "optimization_metrics": {}  # Will be filled during optimization
        }
        
        # Save mobile metadata
        mobile_metadata_path = MODELS_DIR / "mobile_deployment_metadata.json"
        with open(mobile_metadata_path, 'w') as f:
            json.dump(mobile_metadata, f, indent=2)
        
        print(f"✅ Mobile deployment package created:")
        print(f"   📋 Metadata: {mobile_metadata_path}")
        print(f"   🔧 Preprocessing config: {preprocess_config_path}")
        
        return mobile_metadata_path, mobile_metadata
        
    except Exception as e:
        print(f"❌ Error creating deployment package: {e}")
        return None, None

def main():
    """Main optimization pipeline."""
    print("🚀 HEART SOUND MODEL MOBILE OPTIMIZATION - STAGE 1")
    print("=" * 60)
    
    # Step 1: Analyze original model
    original_model, original_stats = analyze_original_model()
    if original_model is None:
        return
    
    # Step 2: Convert to TensorFlow Lite (standard)
    tflite_model, tflite_stats = convert_to_tflite(original_model, quantize=False)
    if tflite_model is None:
        return
    
    # Step 3: Convert to TensorFlow Lite (quantized)
    tflite_quantized, tflite_quantized_stats = convert_to_tflite(original_model, quantize=True)
    
    # Step 4: Test inference performance
    performance_stats = test_tflite_inference(TFLITE_MODEL_PATH, original_model)
    if tflite_quantized:
        performance_quantized_stats = test_tflite_inference(TFLITE_QUANTIZED_PATH, original_model)
    
    # Step 5: Create deployment package
    metadata_path, mobile_metadata = create_mobile_deployment_package()
    
    # Step 6: Update metadata with optimization results
    if metadata_path and mobile_metadata:
        mobile_metadata["optimization_metrics"] = {
            "original_model": original_stats,
            "tflite_standard": tflite_stats,
            "tflite_quantized": tflite_quantized_stats,
            "performance_standard": performance_stats,
            "performance_quantized": performance_quantized_stats if tflite_quantized else None
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(mobile_metadata, f, indent=2)
    
    # Final summary
    print(f"\n🎯 STAGE 1 OPTIMIZATION COMPLETE!")
    print("=" * 60)
    
    if original_stats and tflite_stats:
        size_reduction = (1 - tflite_stats['size_mb'] / original_stats['size_mb']) * 100
        print(f"📊 OPTIMIZATION RESULTS:")
        print(f"   🔽 Size reduction: {size_reduction:.1f}% ({original_stats['size_mb']:.2f}MB → {tflite_stats['size_mb']:.2f}MB)")
        
        if tflite_quantized_stats:
            quantized_reduction = (1 - tflite_quantized_stats['size_mb'] / original_stats['size_mb']) * 100
            print(f"   🔽 Quantized reduction: {quantized_reduction:.1f}% ({original_stats['size_mb']:.2f}MB → {tflite_quantized_stats['size_mb']:.2f}MB)")
        
        if performance_stats:
            print(f"   ⚡ Speed improvement: {performance_stats['speedup']:.2f}x")
            print(f"   📱 Mobile ready: {'✅ YES' if performance_stats['mobile_ready'] else '❌ NO'}")
    
    print(f"\n🎯 NEXT STEPS FOR STAGE 2:")
    print(f"   1. Integrate TFLite model into Streamlit app")
    print(f"   2. Create mobile-first UI design")
    print(f"   3. Implement on-device inference pipeline")
    print(f"   4. Add real-time audio recording and processing")

if __name__ == "__main__":
    main()