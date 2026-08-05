"""
============================================================
BUILD GARMIN FEATURE WINDOWS
============================================================

Purpose
-------
Create 7-day feature windows for every processed Garmin
daily metric using the recovered body-weight timeline.

For each weight measurement date, calculate either:

    • 7-day SUM
    • 7-day MEAN

depending on the feature.

Outputs are written to:

data/processed/garmin_features/

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

GARMIN_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "garmin_daily"
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
    / "garmin_features"
)

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# AGGREGATION METHODS
# ============================================================

FEATURE_METHOD = {

    # Weekly totals
    "distance_daily.csv": "sum",
    "calories_daily.csv": "sum",
    "totaltime_daily.csv": "sum",
    "steps_daily.csv": "sum",
    "totalascent_daily.csv": "sum",
    "totaldescent_daily.csv": "sum",
    "totalreps_daily.csv": "sum",
    "totalsets_daily.csv": "sum",

    # Weekly averages
    "avg_hr_daily.csv": "mean",
    "max_hr_daily.csv": "mean",
    "avg_speed_daily.csv": "mean",
    "max_speed_daily.csv": "mean",
    "avg_stride_length_daily.csv": "mean",
    "bodybatterydrain_daily.csv": "mean"
}

# ============================================================
# LOAD WEIGHT DATA
# ============================================================

weight_df = load_csv(
    WEIGHT_FILE
)

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

    garmin_df = load_csv(
        GARMIN_FOLDER / feature_file
    )

    garmin_df = convert_to_datetime(
        garmin_df,
        "date"
    )

    feature_df = weight_df.copy()

    value_column = garmin_df.columns[-1]

    if method == "sum":
      suffix = "total"
    else:
        suffix = "avg"

    feature_column = (
        feature_file
        .replace("_daily.csv", "")
        + "_7day_"
        + suffix
    )

    feature_df[feature_column] = feature_df["date"].apply(
        lambda measurement_date:
        aggregate_metric_before_measurement(
            measurement_date=measurement_date,
            df=garmin_df,
            method=method,
            days=7,
            value_column=value_column
        )
    )

    feature_df = feature_df[
        [
            "date",
            "weight_lb",
            feature_column
        ]
    ]

    output_name = (
        feature_file
        .replace("_daily.csv", "_features.csv")
    )

    save_csv(
        feature_df,
        OUTPUT_FOLDER / output_name
    )

print()
print("=" * 70)
print("Finished building Garmin feature windows.")
print("=" * 70)