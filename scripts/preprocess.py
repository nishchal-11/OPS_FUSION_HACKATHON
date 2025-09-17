#!/usr/bin/env python
"""
Standalone preprocessing script for heart sound analysis.
Can be used independently or as part of the notebook workflow.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import *
from config import *

def main():
    parser = argparse.ArgumentParser(description='Preprocess heart sound dataset')
    parser.add_argument('--data-dir', type=str, default=str(PHYSIONET_DIR),
                       help='Path to PhysioNet dataset directory')
    parser.add_argument('--output-dir', type=str, default=str(SPECTROGRAMS_DIR),
                       help='Output directory for spectrograms')
    parser.add_argument('--sample-rate', type=int, default=SAMPLE_RATE,
                       help='Target sample rate in Hz')
    parser.add_argument('--duration', type=float, default=AUDIO_DURATION,
                       help='Target audio duration in seconds')
    parser.add_argument('--n-mels', type=int, default=N_MELS,
                       help='Number of mel frequency bins')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing of existing files')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of files to process (for testing)')
    
    args = parser.parse_args()
    
    print("🎵 Heart Sound Preprocessing Script")
    print("=" * 50)
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Sample rate: {args.sample_rate} Hz")
    print(f"Duration: {args.duration}s")
    print(f"Mel bins: {args.n_mels}")
    print(f"Force reprocess: {args.force}")
    print(f"File limit: {args.limit or 'None'}")
    print("=" * 50)
    
    # Load dataset labels
    print("📊 Loading dataset labels...")
    labels_df = get_physionet_labels(args.data_dir)
    
    if len(labels_df) == 0:
        print("❌ No labels found in dataset directory")
        return 1
    
    print_dataset_summary(labels_df)
    
    # Limit files if specified
    if args.limit:
        labels_df = labels_df.head(args.limit)
        print(f"🔍 Limited to {len(labels_df)} files for processing")
    
    # Create preprocessing config
    preprocess_config = create_preprocessing_config(
        sr=args.sample_rate,
        duration=args.duration,
        n_mels=args.n_mels,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH
    )
    
    # Save config
    config_path = Path(args.output_dir).parent / "preprocess_config.json"
    save_preprocessing_config(preprocess_config, str(config_path))
    print(f"💾 Preprocessing config saved to: {config_path}")
    
    # Process files
    print(f"🔄 Processing {len(labels_df)} audio files...")
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    for label in ['normal', 'abnormal']:
        (output_dir / label).mkdir(exist_ok=True)
    
    processed_files = []
    failed_files = []
    
    for idx, row in tqdm(labels_df.iterrows(), total=len(labels_df), desc="Processing"):
        file_id = row['file_id']
        label = row['binary_label']
        file_path = row['file_path']
        
        # Define output path
        output_file = output_dir / label / f"{file_id}.npy"
        
        # Skip if exists and not forcing
        if output_file.exists() and not args.force:
            processed_files.append({
                'file_id': file_id,
                'label': label,
                'spectrogram_path': str(output_file),
                'status': 'cached'
            })
            continue
        
        try:
            # Load and preprocess audio
            audio, sr = load_audio(file_path, target_sr=args.sample_rate)
            if len(audio) == 0:
                raise ValueError("Empty audio file")
            
            processed_audio = preprocess_audio(audio, sr, duration=args.duration)
            
            # Convert to spectrogram
            mel_spec = audio_to_melspectrogram(
                processed_audio, sr,
                n_mels=args.n_mels,
                n_fft=N_FFT,
                hop_length=HOP_LENGTH
            )
            
            # Save spectrogram
            np.save(output_file, mel_spec)
            
            processed_files.append({
                'file_id': file_id,
                'label': label,
                'spectrogram_path': str(output_file),
                'status': 'processed'
            })
            
        except Exception as e:
            failed_files.append({
                'file_id': file_id,
                'file_path': file_path,
                'error': str(e)
            })
            continue
    
    # Save processing results
    results_df = pd.DataFrame(processed_files)
    results_path = output_dir.parent / "preprocessing_results.csv"
    results_df.to_csv(results_path, index=False)
    
    # Print summary
    print("\n✅ Preprocessing complete!")
    print(f"  Successfully processed: {len(processed_files)}")
    print(f"  Failed: {len(failed_files)}")
    print(f"  Results saved to: {results_path}")
    
    if failed_files:
        print(f"\n❌ Failed files (first 5):")
        for fail in failed_files[:5]:
            print(f"  {fail['file_id']}: {fail['error']}")
    
    # Print class distribution
    if len(results_df) > 0:
        print(f"\n📊 Processed files by class:")
        print(results_df['label'].value_counts().to_dict())
        
        # Print sample shapes
        sample_file = results_df.iloc[0]['spectrogram_path']
        sample_shape = np.load(sample_file).shape
        print(f"   Spectrogram shape: {sample_shape}")
    
    return 0 if len(failed_files) == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)