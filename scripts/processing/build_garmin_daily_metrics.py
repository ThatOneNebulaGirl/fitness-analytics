"""
============================================================
BUILD GARMIN DAILY METRICS
============================================================

Purpose
-------
Convert cleaned Garmin activity data into daily metrics.

Garmin activities are stored one activity per row. Since
multiple activities may occur on the same day, each metric
is aggregated into a daily time series before feature
engineering.

Outputs are written to:

    data/processed/garmin_daily/

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
    aggregate_daily_sum,
    aggregate_daily_mean
)

# ============================================================
# INPUT / OUTPUT
# ============================================================

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "garmin_fitnessData_model.csv"
)

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "garmin_daily"
)

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# LOAD DATA
# ============================================================

df = load_csv(INPUT_FILE)

df = convert_to_datetime(
    df,
    "Date"
)

# ============================================================
# DAILY TOTALS
# ============================================================

DAILY_TOTALS = {

    "Distance": "distance_daily.csv",
    "Calories": "calories_daily.csv",
    "Total Time": "totaltime_daily.csv",
    "Steps": "steps_daily.csv",
    "Total Ascent": "totalascent_daily.csv",
    "Total Descent": "totaldescent_daily.csv",
    "Total Reps": "totalreps_daily.csv",
    "Total Sets": "totalsets_daily.csv",
    "Body Battery Drain": "bodybatterydrain_daily.csv"

}

# ============================================================
# DAILY AVERAGES
# ============================================================

DAILY_MEANS = {

    "Avg HR": "avg_hr_daily.csv",
    "Max HR": "max_hr_daily.csv",
    "Avg Speed": "avg_speed_daily.csv",
    "Max Speed": "max_speed_daily.csv",
    "Avg Stride Length": "avg_stride_length_daily.csv"

}

# ============================================================
# BUILD DAILY TOTALS
# ============================================================

for column, output_file in DAILY_TOTALS.items():

    print()
    print("=" * 70)
    print(column)
    print("=" * 70)

    daily = aggregate_daily_sum(

        df,

        date_column="Date",

        value_column=column

    )

    save_csv(

        daily,

        OUTPUT_FOLDER / output_file

    )

# ============================================================
# BUILD DAILY AVERAGES
# ============================================================

for column, output_file in DAILY_MEANS.items():

    print()
    print("=" * 70)
    print(column)
    print("=" * 70)

    daily = aggregate_daily_mean(

        df,

        date_column="Date",

        value_column=column

    )

    save_csv(

        daily,

        OUTPUT_FOLDER / output_file

    )

print()
print("=" * 70)
print("Finished building Garmin daily metrics.")
print("=" * 70)