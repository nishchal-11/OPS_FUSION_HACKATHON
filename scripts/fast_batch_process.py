#!/usr/bin/env python3
"""
Fast Batch Processing Script for Heart Sound Dataset
Processes all 3,240 files efficiently with parallel processing
"""

import os
import sys
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from pathlib import Path
import json
from tqdm import tqdm
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# Set TensorFlow environment variable
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Add parent directory for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils import *
from config import *

def process_single_file(args):
    """Process a single audio file to spectrogram."""
    row, output_dir = args
    file_id = row['file_id']
    label = row['binary_label']
    file_path = row['file_path']

    try:
        # Load audio
        audio, sr = load_audio(file_path, target_sr=SAMPLE_RATE)
        if len(audio) == 0:
            return {'file_id': file_id, 'status': 'failed', 'error': 'Empty audio'}

        # Preprocess
        processed_audio = preprocess_audio(audio, sr, duration=AUDIO_DURATION)

        # Convert to spectrogram
        mel_spec = audio_to_melspectrogram(
            processed_audio, sr,
            n_mels=N_MELS, n_fft=N_FFT, hop_length=HOP_LENGTH
        )

        # Save spectrogram
        label_dir = output_dir / label
        label_dir.mkdir(exist_ok=True)
        spec_path = label_dir / f"{file_id}.npy"
        np.save(spec_path, mel_spec)

        return {
            'file_id': file_id,
            'label': label,
            'spectrogram_path': str(spec_path),
            'shape': mel_spec.shape,
            'status': 'success'
        }

    except Exception as e:
        return {'file_id': file_id, 'status': 'failed', 'error': str(e)}

def main():
    print("🚀 Fast Batch Processing for Full Dataset")
    print("=" * 50)

    # Load dataset
    print("📊 Loading dataset...")
    labels_df = get_physionet_labels(str(PHYSIONET_DIR))

    if len(labels_df) == 0:
        print("❌ No dataset found!")
        return

    print(f"📋 Found {len(labels_df)} files to process")
    print(f"   Distribution: {labels_df['binary_label'].value_counts().to_dict()}")

    # Create output directory
    SPECTROGRAMS_DIR.mkdir(parents=True, exist_ok=True)

    # Use parallel processing
    num_workers = min(mp.cpu_count(), 8)  # Limit to 8 workers max
    print(f"🔄 Processing with {num_workers} parallel workers...")

    # Prepare arguments
    args_list = [(row, SPECTROGRAMS_DIR) for _, row in labels_df.iterrows()]

    # Process files
    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        future_to_row = {executor.submit(process_single_file, args): args[0] for args in args_list}

        # Process results as they complete
        with tqdm(total=len(args_list), desc="Processing files") as pbar:
            for future in as_completed(future_to_row):
                result = future.result()
                results.append(result)
                pbar.update(1)

                # Print progress every 100 files
                if len(results) % 100 == 0:
                    success_count = sum(1 for r in results if r['status'] == 'success')
                    print(f"   ✅ {success_count}/{len(results)} successful so far...")

    # Process results
    successful_results = [r for r in results if r['status'] == 'success']
    failed_results = [r for r in results if r['status'] == 'failed']

    print("\n📊 Processing Complete:")
    print(f"   ✅ Successful: {len(successful_results)}")
    print(f"   ❌ Failed: {len(failed_results)}")

    if failed_results:
        print("\n❌ Failed files (first 5):")
        for fail in failed_results[:5]:
            print(f"   {fail['file_id']}: {fail.get('error', 'Unknown error')}")

    # Create processed dataset dataframe
    if successful_results:
        processed_df = pd.DataFrame(successful_results)

        # Add split information (simple random split for now)
        processed_df['split'] = np.random.choice(['train', 'val'], size=len(processed_df), p=[0.8, 0.2])

        # Save results
        results_path = DATA_DIR / "full_processed_dataset.csv"
        processed_df.to_csv(results_path, index=False)

        print(f"\n💾 Results saved to: {results_path}")
        print(f"📊 Final dataset: {len(processed_df)} spectrograms")
        print(f"   Train: {len(processed_df[processed_df['split'] == 'train'])}")
        print(f"   Val: {len(processed_df[processed_df['split'] == 'val'])}")
        print(f"   Classes: {processed_df['label'].value_counts().to_dict()}")

        # Save preprocessing config
        preprocess_config = create_preprocessing_config(
            sr=SAMPLE_RATE,
            duration=AUDIO_DURATION,
            n_mels=N_MELS,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        config_path = DATA_DIR / "full_preprocess_config.json"
        save_preprocessing_config(preprocess_config, str(config_path))
        print(f"⚙️ Config saved to: {config_path}")

        print("\n🎉 Full dataset processing complete!")
        print("🚀 Ready for CNN training!")

    else:
        print("❌ No files were successfully processed!")

if __name__ == "__main__":
    main()