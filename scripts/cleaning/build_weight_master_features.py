"""
============================================================
BUILD WEIGHT MASTER FEATURES
============================================================

Purpose
-------
Merge every engineered Apple Health and Garmin feature
dataset into one master modeling dataset.

Each row represents a single body-weight observation.
Every engineered feature is merged using the measurement
date as the common key.

Outputs are written to:

data/processed/weight_master_features.csv

Author:
    Melody Sanchez

Project:
    Longitudinal Fitness Analytics
============================================================
"""

from pathlib import Path
import sys

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

# ============================================================
# TOOLS
# ============================================================

from src.tools_for_cleaning import (
    load_csv,
    save_csv,
    convert_to_datetime,
    show_rows
)

# ============================================================
# INPUTS
# ============================================================

WEIGHT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "weight_aug2026.csv"
)

APPLE_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apple_features"
)

GARMIN_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "garmin_features"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weight_master_features.csv"
)

# ============================================================
# LOAD WEIGHT DATA
# ============================================================

master_df = load_csv(
    WEIGHT_FILE
)

master_df = convert_to_datetime(
    master_df,
    "date"
)

print()
print("=" * 70)
print("Loaded weight timeline")
print("=" * 70)

print(master_df.head())

# ============================================================
# MERGE APPLE FEATURES
# ============================================================

print()
print("=" * 70)
print("Merging Apple Features")
print("=" * 70)

for csv_file in sorted(
    APPLE_FOLDER.glob("*_features.csv")
):

    feature_df = load_csv(csv_file)

    feature_df = convert_to_datetime(
        feature_df,
        "date"
    )

    feature_column = feature_df.columns[-1]

    master_df = master_df.merge(

        feature_df[
            [
                "date",
                feature_column
            ]
        ],

        on="date",
        how="left"

    )

    print(
        f"Merged: {csv_file.name}"
    )

# ============================================================
# MERGE GARMIN FEATURES
# ============================================================

print()
print("=" * 70)
print("Merging Garmin Features")
print("=" * 70)

for csv_file in sorted(
    GARMIN_FOLDER.glob("*_features.csv")
):

    feature_df = load_csv(csv_file)

    feature_df = convert_to_datetime(
        feature_df,
        "date"
    )

    feature_column = feature_df.columns[-1]

    master_df = master_df.merge(

        feature_df[
            [
                "date",
                feature_column
            ]
        ],

        on="date",
        how="left"

    )

    print(
        f"Merged: {csv_file.name}"
    )


# ============================================================
# STANDARDIZE FEATURE NAMES
# ============================================================

master_df = master_df.rename(
    columns={

        # Garmin totals
        "distance_7day_total": "distance_7day_sum",
        "calories_7day_total": "calories_7day_sum",
        "steps_7day_total": "steps_7day_sum",
        "totaltime_7day_total": "totaltime_7day_sum",
        "totalreps_7day_total": "totalreps_7day_sum",
        "totalsets_7day_total": "totalsets_7day_sum",
        "totalascent_7day_total": "totalascent_7day_sum",
        "totaldescent_7day_total": "totaldescent_7day_sum",

        # Garmin averages
        "avg_hr_7day_avg": "avg_hr_7day_mean",
        "avg_stride_length_7day_avg": "avg_stride_length_7day_mean",
        "bodybatterydrain_7day_avg": "bodybatterydrain_7day_mean"

    }
)

# ============================================================
# RECONCILE DISTANCE FEATURES
# ============================================================

# Prefer Garmin distance when available.
# Otherwise use the Apple Health distance.

master_df["distance_7day_sum"] = (
    master_df["distance_7day_sum"]
    .fillna(master_df["distancewalkingrunning_7day_sum"])
)

# Remove the redundant Apple feature.
master_df = master_df.drop(
    columns=["distancewalkingrunning_7day_sum"]
)
# ============================================================
# FINAL AUDIT
# ============================================================

print()
print("=" * 70)
print("Master Dataset")
print("=" * 70)

print()

print(
    "Rows:",
    len(master_df)
)

print(
    "Columns:",
    len(master_df.columns)
)

print()

print(master_df.columns.tolist())

print()

print(
    master_df.isna().sum()
)

show_rows(
    master_df,
    5
)

# ============================================================
# SAVE
# ============================================================

save_csv(
    master_df,
    OUTPUT_FILE
)

print()
print("=" * 70)
print("Finished building master dataset.")
print("=" * 70)