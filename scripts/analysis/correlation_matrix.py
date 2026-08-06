"""
============================================================
CORRELATION MATRIX
============================================================

Purpose
-------
Compute the Pearson correlation matrix for the completed
weight master dataset and visualize the relationships
between engineered features.

Outputs

    data/processed/correlation_matrix.csv

    figures/correlation_matrix.png

Author:
    Melody Sanchez

Project:
    Longitudinal Fitness Analytics
============================================================
"""

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# TOOLS
# ============================================================

from src.tools_for_cleaning import (
    load_csv,
    save_csv
)

# ============================================================
# PATHS
# ============================================================

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weight_master_features.csv"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "correlation_matrix.csv"
)

FIGURE_DIR = (
    PROJECT_ROOT
    / "figures"
)

FIGURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FIGURE = (
    FIGURE_DIR
    / "correlation_matrix.png"
)

# ============================================================
# LOAD DATA
# ============================================================

df = load_csv(DATA_FILE)

# ============================================================
# NUMERIC FEATURES
# ============================================================

numeric_df = df.select_dtypes(include="number")

# ============================================================
# SAVE FULL CORRELATION MATRIX
# ============================================================

corr_full = numeric_df.corr(method="pearson")

print()
print("=" * 70)
print("Correlation Matrix")
print("=" * 70)

print(corr_full.round(3))

save_csv(
    corr_full.round(4),
    OUTPUT_CSV
)

# ============================================================
# FEATURES TO HIDE FROM HEATMAP
#
# These remain in the dataset and CSV.
# They are hidden only from the figure because they are either
# redundant or have insufficient observations.
# ============================================================

DROP_COLUMNS = [

    # Nearly empty
    "heartratevariabilitysdnn_7day_mean",

    # Highly redundant with Active Calories
    "totalreps_7day_sum",
    "totalsets_7day_sum",

    # Highly redundant with Workout Calories
    "calories_7day_sum",

    # Apple & Garmin both have step metrics
    "steps_7day_sum"

]

plot_df = numeric_df.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
)

corr = plot_df.corr(method="pearson")

# ============================================================
# PRETTY FEATURE NAMES
# ============================================================

pretty_names = {

    "weight_lb":
        "Weight",

    "activeenergyburned_7day_sum":
        "Active Calories",

    "appleexercisetime_7day_sum":
        "Exercise Minutes",

    "basalenergyburned_7day_sum":
        "Basal Calories",

    "distance_7day_sum":
        "Distance",

    "stepcount_7day_sum":
        "Apple Steps",

    "flightsclimbed_7day_sum":
        "Flights Climbed",

    "heartrate_7day_mean":
        "Heart Rate",

    "walkingheartrateaverage_7day_mean":
        "Walking HR",

    "walkingspeed_7day_mean":
        "Walking Speed",

    "walkingsteplength_7day_mean":
        "Stride Length",

    "avg_hr_7day_mean":
        "Workout HR",

    "avg_stride_length_7day_mean":
        "Workout Stride",

    "bodybatterydrain_7day_mean":
        "Body Battery Drain",

    "distance_7day_sum":
        "Workout Distance",

    "totaltime_7day_sum":
        "Workout Duration",

    "totalascent_7day_sum":
        "Elevation Gain",

    "totaldescent_7day_sum":
        "Elevation Loss"

}

corr.rename(
    index=pretty_names,
    columns=pretty_names,
    inplace=True
)

# ============================================================
# HEATMAP
# ============================================================

plt.figure(
    figsize=(11, 9)
)

image = plt.imshow(
    corr,
    cmap="PiYG",
    vmin=-1,
    vmax=1,
    interpolation="nearest",
    aspect="equal"
)

plt.colorbar(image)

plt.xticks(
    range(len(corr.columns)),
    corr.columns,
    rotation=45,
    ha="right",
    fontsize=9
)

plt.yticks(
    range(len(corr.columns)),
    corr.columns,
    fontsize=9
)

# Write correlation values inside cells
for i in range(len(corr.index)):
    for j in range(len(corr.columns)):

        value = corr.iloc[i, j]

        if pd.notna(value):

            plt.text(
                j,
                i,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color="black"
            )

plt.title(
    "Correlation Matrix of Behavioral, Physiological, and Body Composition Variables",
    fontsize=15
)

plt.tight_layout()

plt.savefig(
    OUTPUT_FIGURE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print()
print("=" * 70)
print("Saved")
print("=" * 70)

print(OUTPUT_CSV)
print(OUTPUT_FIGURE)