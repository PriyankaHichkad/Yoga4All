"""
Merge multiple per-video dataset CSVs into a single combined dataset,
matching the format expected by the notebook (before normalization step).

Usage:
  python scripts/merge_datasets.py --inputs data/downloaded_video1_dataset.csv data/downloaded_video2_dataset.csv --output data/combined_dataset.csv
"""
import argparse
import pandas as pd


def merge_datasets(input_files, output_file, shuffle=True, random_state=42):
    """
    Merge multiple dataset CSVs into one, optionally shuffle, and save.
    Removes visibility columns to match notebook format (only x,y,z coords).
    """
    dfs = []
    for f in input_files:
        print(f"Loading {f}...")
        df = pd.read_csv(f)
        dfs.append(df)
    
    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)
    print(f"\nMerged dataset: {len(merged_df)} rows from {len(input_files)} file(s)")
    
    # Remove visibility columns to match notebook format (only keep x, y, z)
    # The notebook normalization expects only x,y,z coordinates (not visibility)
    visibility_cols = [c for c in merged_df.columns if c.endswith('_visibility')]
    if visibility_cols:
        print(f"Removing {len(visibility_cols)} visibility columns to match notebook format...")
        merged_df = merged_df.drop(columns=visibility_cols)
    
    # Shuffle if requested
    if shuffle:
        print(f"Shuffling with random_state={random_state}...")
        merged_df = merged_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Save combined dataset
    merged_df.to_csv(output_file, index=False)
    print(f"\nSaved combined dataset: {output_file}")
    print(f"  Shape: {merged_df.shape}")
    print(f"  Columns: {list(merged_df.columns)[:10]}... (showing first 10)")
    print(f"  Unique pose_class: {sorted(merged_df['pose_class'].unique())}")
    
    # Class distribution
    print(f"\nClass distribution:")
    class_counts = merged_df['pose_class'].value_counts().sort_index()
    for cls, count in class_counts.items():
        pct = count / len(merged_df) * 100
        print(f"  Class {cls}: {count:4d} samples ({pct:5.1f}%)")
    
    return merged_df


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--inputs', nargs='+', required=True, help='Input dataset CSV files to merge')
    p.add_argument('--output', required=True, help='Output combined dataset CSV path')
    p.add_argument('--no-shuffle', action='store_true', help='Skip shuffling')
    p.add_argument('--random-state', type=int, default=42, help='Random state for shuffling')
    args = p.parse_args()
    
    df = merge_datasets(args.inputs, args.output, shuffle=not args.no_shuffle, random_state=args.random_state)
    print('\nDone!')
