"""
============================================================
AUDIT WEIGHT MASTER DATASET
============================================================

Purpose
-------
Perform an exploratory audit of the completed
weight_master_features dataset prior to visualization
and predictive modeling.

Reports

    • Dataset shape
    • Column names
    • Data types
    • Missing values
    • Summary statistics
    • Correlation with weight

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
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# TOOLS
# ============================================================

from src.tools_for_cleaning import load_csv

# ============================================================
# LOAD DATA
# ============================================================

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weight_master_features.csv"
)

df = load_csv(DATA_FILE)

# ============================================================
# DATASET OVERVIEW
# ============================================================

print()
print("=" * 70)
print("Dataset Overview")
print("=" * 70)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

# ============================================================
# COLUMN NAMES
# ============================================================

print()
print("=" * 70)
print("Columns")
print("=" * 70)

for column in df.columns:
    print(column)

# ============================================================
# DATA TYPES
# ============================================================

print()
print("=" * 70)
print("Data Types")
print("=" * 70)

print(df.dtypes)

# ============================================================
# MISSING VALUES
# ============================================================

print()
print("=" * 70)
print("Missing Values")
print("=" * 70)

missing = (
    df
    .isna()
    .sum()
    .sort_values(ascending=False)
)

print(missing)


# ============================================================
# CORRELATION WITH WEIGHT
# ============================================================

print()
print("=" * 70)
print("Correlation with Weight")
print("=" * 70)

corr = (
    df
    .corr(numeric_only=True)["weight_lb"]
    .sort_values(ascending=False)
)

print(corr)

print()
print("=" * 70)
print("Audit Complete")
print("=" * 70)

print(df.describe(include="all"))

print()

print("=" * 70)
print("Complete Cases")
print("=" * 70)

complete = (
    df
    .notna()
    .sum()
    .sort_values(ascending=False)
)

print(complete)