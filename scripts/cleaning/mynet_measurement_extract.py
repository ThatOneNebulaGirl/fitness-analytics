from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "myNetDiary"

OUTPUT_DIR = PROJECT_ROOT / "data" / "cleaned" / "myNetDiary"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ---------------------------------------------------------------------
# Measurement categories
# ---------------------------------------------------------------------

BODY_MEASUREMENTS = {
    "Body Weight",
    "Waist size",
    "Hip Size",
    "Chest size",
    "Thigh size",
}

STEP_MEASUREMENT = "Daily Steps Count"

# ---------------------------------------------------------------------
# Load every Measurements-*.csv
# ---------------------------------------------------------------------

files = sorted(
    INPUT_DIR.glob("Measurements-*.csv")
)

dfs = []

for file in files:

    print(f"Loading {file.name}")

    df = pd.read_csv(file)

    dfs.append(df)

measurements = pd.concat(
    dfs,
    ignore_index=True
)

print()
print(f"Loaded {len(files)} files")
print(f"Total observations: {len(measurements):,}")

# ---------------------------------------------------------------------
# Split datasets
# ---------------------------------------------------------------------

body_measurements = measurements[
    measurements["Measurement"].isin(BODY_MEASUREMENTS)
].copy()

daily_steps = measurements[
    measurements["Measurement"] == STEP_MEASUREMENT
].copy()

# ---------------------------------------------------------------------
# Standardize dates
# ---------------------------------------------------------------------

body_measurements["Date"] = pd.to_datetime(
    body_measurements["Date"]
)

daily_steps["Date"] = pd.to_datetime(
    daily_steps["Date"]
)

body_measurements = body_measurements.sort_values(
    "Date"
)

daily_steps = daily_steps.sort_values(
    "Date"
)

# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------

body_output = (
    OUTPUT_DIR /
    "mynet_body_measurements.csv"
)

steps_output = (
    OUTPUT_DIR /
    "mynet_daily_steps.csv"
)

body_measurements.to_csv(
    body_output,
    index=False
)

daily_steps.to_csv(
    steps_output,
    index=False
)

print()
print(
    f"Saved {len(body_measurements):,} body measurements"
)
print(body_output)

print()
print(
    f"Saved {len(daily_steps):,} daily step records"
)
print(steps_output)

print("\nMeasurement counts\n")

print(
    body_measurements["Measurement"]
    .value_counts()
)

print()

print(
    daily_steps["Measurement"]
    .value_counts()
)


print("\nDuplicate body measurements by date and type:\n")

duplicates = (
    body_measurements
    .groupby(["Date", "Measurement"])
    .size()
    .reset_index(name="Count")
)

duplicates = duplicates[
    duplicates["Count"] > 1
]

print(duplicates)

print("\nDuplicate daily step dates:\n")

duplicates = (
    daily_steps
    .groupby("Date")
    .size()
    .reset_index(name="Count")
)

duplicates = duplicates[
    duplicates["Count"] > 1
]

print(duplicates)



print("\nBody measurement date range:")
print(
    body_measurements["Date"].min().date(),
    "→",
    body_measurements["Date"].max().date()
)

print("\nDaily steps date range:")
print(
    daily_steps["Date"].min().date(),
    "→",
    daily_steps["Date"].max().date()
)