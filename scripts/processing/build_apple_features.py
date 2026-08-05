"""
============================================================
BUILD APPLE FEATURE WINDOWS
============================================================

Purpose
-------
Create 7-day feature windows for every processed Apple
Health daily metric using the recovered weight timeline.

For each weight measurement date, calculate either:

    • 7-day SUM
    • 7-day MEAN

depending on the feature.

Outputs are written to:

data/processed/apple_features/

Author:
    Melody Sanchez

Project:
    Longitudinal Fitness Analytics
============================================================
"""

from pathlib import Path
import sys
import pandas as pd

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# TOOLS
# ============================================================

from src.tools_for_cleaning import (
    load_csv,
    save_csv,
    convert_to_datetime,
    aggregate_metric_before_measurement
)

# ============================================================
# INPUT FOLDERS
# ============================================================

APPLE_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apple_daily"
)

WEIGHT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "weight_aug2026.csv"
)

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apple_features"
)

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# AGGREGATION METHODS
# ============================================================

FEATURE_METHOD = {

    # Daily totals
    "activeenergyburned_clean.csv": "sum",
    "appleexercisetime_clean.csv": "sum",
    "basalenergyburned_clean.csv": "sum",
    "distancewalkingrunning_clean.csv": "sum",
    "flightsclimbed_clean.csv": "sum",
    "stepcount_clean.csv": "sum",

    # Daily averages
    "heartrate_clean.csv": "mean",
    "heartratevariabilitysdnn_clean.csv": "mean",
    "walkingheartrateaverage_clean.csv": "mean",
    "walkingspeed_clean.csv": "mean",
    "walkingsteplength_clean.csv": "mean",
}

# ============================================================
# LOAD WEIGHT DATA
# ============================================================

weight_df = load_csv(WEIGHT_FILE)

weight_df = convert_to_datetime(
    weight_df,
    "date"
)

# ============================================================
# BUILD FEATURES
# ============================================================

for feature_file, method in FEATURE_METHOD.items():

    print()
    print("=" * 70)
    print(feature_file)
    print("=" * 70)

    apple_df = load_csv(
        APPLE_FOLDER / feature_file
    )

    apple_df = convert_to_datetime(
        apple_df,
        "date"
    )

    feature_df = weight_df.copy()

    feature_df["value"] = feature_df["date"].apply(
        lambda measurement_date:
        aggregate_metric_before_measurement(
            measurement_date=measurement_date,
            df=apple_df,
            method=method,
            days=7,
            value_column="value"
        )
    )
    feature_column = (
    feature_file
    .replace("_clean.csv", "")
    + "_7day_"
    + method
)

    feature_df[feature_column] = feature_df["date"].apply(
        lambda measurement_date:
        aggregate_metric_before_measurement(
            measurement_date=measurement_date,
            df=apple_df,
            method=method,
            days=7,
            value_column="value"
        )
    )

    feature_df = feature_df[
        [
            "date",
            "weight_lb",
            feature_column
        ]
    ]

    feature_name = feature_file.replace(
            "_clean.csv",
            "_features.csv"
        )

    save_csv(
        feature_df,
        OUTPUT_FOLDER / feature_name
    )

print()
print("=" * 70)
print("Finished building Apple feature windows.")
print("=" * 70)