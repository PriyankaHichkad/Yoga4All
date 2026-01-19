"""
Create per-video numeric dataset CSVs from a video using MediaPipe pose.
Usage:
  python scripts/create_dataset_from_video.py \
      --video path/to/video.mp4 \
      --intervals data/pose_intervals_video1.csv \
      --output data/downloaded_video1_dataset.csv

This script labels frames according to the intervals CSV (columns: pose_num,start,end),
maps pose_num -> pose_class using POSE_CLASS_MAPPING similar to the notebook,
and saves a CSV containing only numeric features + frame/video metadata.

If the output file exists, new rows are appended with column alignment.
"""
import argparse
import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

# Landmarks and mapping consistent with notebook
LANDMARKS_OF_INTEREST = {
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
}

# Keep the same mapping used in the notebook
POSE_CLASS_MAPPING = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 3,
    11: 2,
    12: 1,
}


def load_intervals(csv_path):
    df = pd.read_csv(csv_path)
    intervals = {}
    for _, r in df.iterrows():
        pose_num = int(r['pose_num'])
        start = float(r['start'])
        end = float(r['end'])
        intervals[pose_num] = (start, end)
    return intervals


def get_pose_for_time(t, intervals):
    for pose_num, (s, e) in intervals.items():
        if s <= t < e:
            return pose_num, POSE_CLASS_MAPPING.get(pose_num, pose_num)
    return 0, 0


def process_video(input_video, intervals_csv, output_csv):
    intervals = load_intervals(intervals_csv) if intervals_csv and os.path.exists(intervals_csv) else {}

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1,
                        enable_segmentation=False, min_detection_confidence=0.3, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {input_video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_idx = 0
    rows = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        timestamp = frame_idx / fps
        pose_num, pose_class = get_pose_for_time(timestamp, intervals) if intervals else (0, 0)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        row = {'frame': frame_idx, 'pose_class': int(pose_class)}

        # Save raw MediaPipe landmark coordinates (x, y, z) and visibility — no normalization here.
        # Append rows ONLY when a pose is detected AND the frame is labeled (pose_class > 0)
        if results.pose_landmarks and int(pose_class) > 0:
            lms = results.pose_landmarks.landmark
            for idx, name in LANDMARKS_OF_INTEREST.items():
                lm = lms[idx]
                # MediaPipe landmarks are normalized to image (x,y in [0,1]) and z is relative depth.
                row[f"{name}_x"] = float(lm.x)
                row[f"{name}_y"] = float(lm.y)
                row[f"{name}_z"] = float(lm.z)
                row[f"{name}_visibility"] = float(lm.visibility)

            rows.append(row)
        else:
            # Skip frames without detected pose or without a label (pose_class == 0)
            pass

    cap.release()
    pose.close()

    df_new = pd.DataFrame(rows)
    df_new['video_source'] = os.path.splitext(os.path.basename(input_video))[0]

    # reorder columns
    feature_cols = [c for c in df_new.columns if c not in ['frame', 'pose_class', 'video_source']]
    df_new = df_new[['frame', 'pose_class'] + sorted(feature_cols) + ['video_source']]

    # append to existing output if exists (align columns)
    if os.path.exists(output_csv):
        df_existing = pd.read_csv(output_csv)
        # add missing columns
        for c in set(df_new.columns) - set(df_existing.columns):
            df_existing[c] = 0.0
        for c in set(df_existing.columns) - set(df_new.columns):
            df_new[c] = 0.0
        df_new = df_new[df_existing.columns]
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(output_csv, index=False)
    print(f"Saved dataset CSV: {output_csv} ({len(df_combined)} rows)")
    return output_csv


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--video', required=True, help='Input video file')
    p.add_argument('--intervals', required=False, help='CSV with pose intervals (pose_num,start,end)')
    p.add_argument('--output', required=True, help='Output dataset CSV path')
    args = p.parse_args()

    out = process_video(args.video, args.intervals, args.output)
    print('Done:', out)
