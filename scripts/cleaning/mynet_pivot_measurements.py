from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "myNetDiary"
    / "mynet_body_measurements.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "myNetDiary"
    / "mynet_body_measurements_wide.csv"
)

# ---------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

# ---------------------------------------------------------------------
# Standardize
# ---------------------------------------------------------------------

df["Date"] = pd.to_datetime(df["Date"])

# ---------------------------------------------------------------------
# Pivot
# ---------------------------------------------------------------------

wide = (
    df.pivot(
        index="Date",
        columns="Measurement",
        values="Value"
    )
    .reset_index()
)

# ---------------------------------------------------------------------
# Rename columns
# ---------------------------------------------------------------------

wide = wide.rename(
    columns={
        "Date": "date",
        "Body Weight": "weight_lb",
        "Chest size": "chest",
        "Waist size": "waist",
        "Hip Size": "hip",
        "Thigh size": "thigh",
    }
)

# ---------------------------------------------------------------------
# Sort
# ---------------------------------------------------------------------

wide = (
    wide
    .sort_values("date")
    .reset_index(drop=True)
)

# ---------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------

print("\nColumns\n")

print(wide.columns.tolist())

print("\nMissing values\n")

print(
    wide
    .isna()
    .sum()
)

print("\nDate range\n")

print(
    wide["date"].min().date(),
    "→",
    wide["date"].max().date()
)

print("\nDuplicate dates\n")

duplicates = (
    wide
    .groupby("date")
    .size()
    .reset_index(name="Count")
)

duplicates = duplicates[
    duplicates["Count"] > 1
]

print(duplicates)

# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------

wide.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved:")
print(OUTPUT_FILE)