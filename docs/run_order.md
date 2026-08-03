# Project Execution Guide

This document describes how the project is reproduced from the original raw data to the final analyses.

---

## Step 1 — Garmin Raw Activity Export

**Input**

```text
data/raw/fitnessData.csv
```

**Purpose**

This is the original Garmin activity export downloaded from Garmin Connect. It contains every recorded activity before any cleaning or preprocessing.

**Run**

```text
fit_data_cleaner.py
```

**Outputs**

```text
data/cleaned/
├── garmin_fitnessData_clean3.csv
└── garmin_fitnessData_model.csv
```

A cleaned Garmin activity dataset (`df_clean`) used for data inspection, quality assurance, and reproducibility.

A modeling dataset (`df_model`) derived from `df_clean` by applying sequential modeling-specific quality filters.

---

## What happens?

- Removes irrelevant columns.
- Converts timestamps, timedeltas, and numeric values to appropriate data types.
- Cleans Garmin-specific formatting inconsistencies (for example, Body Battery Drain values exported with leading apostrophes).
- Identifies activity types that contain meaningful Distance measurements.
- Profiles each feature to inspect distributions, potential outliers, and missing values.
- Performs manual review of suspicious observations before applying any modeling-specific cleaning rules.
- Creates `df_model` from `df_clean`.
- Applies sequential modeling-specific quality filters to `df_model`.
- Saves the cleaned Garmin activity dataset.

---

## Modeling Pipeline

````text
## Modeling Pipeline

```text
Raw Garmin Export
        │
        ▼
     df_clean
        │
        ├── Data type conversion
        ├── Garmin-specific value standardization
        ├── Feature profiling
        ├── Missing value assessment
        ├── Manual review
        ▼
     df_model
        │
        ├── Validated modeling filters
        │      ├── Distance < 0.20 miles
        │      ├── Strength Training < 10 minutes
        │      └── Future validated filters
        ▼
Final modeling dataset
````

---

## Notes

Engineering decisions made during this step.

- `df_clean` is the project's cleaned, auditable dataset. It preserves all observations after data cleaning and standardization while correcting formatting issues, invalid representations, and inconsistent data types.
- `df_model` is created as a copy of `df_clean` and is progressively refined by applying modeling-specific quality filters. These filters are intended to improve downstream statistical analyses while preserving the original cleaned dataset for reproducibility.
- The final script exports **both** datasets. `garmin_fitnessData_clean3.csv` contains the cleaned, standardized activity data used for auditing and reproducibility, while `garmin_fitnessData_model.csv` contains the final analysis-ready dataset after all validated modeling filters have been applied.
- Garmin stores **Distance** differently across activity types, so Distance is retained only for activities where it represents meaningful movement.
- Garmin exports some variables using inconsistent formatting (for example, **Body Battery Drain** values prefixed with an apostrophe). These values are standardized before datatype conversion to ensure they are interpreted correctly as numeric values.
- Rather than selecting arbitrary cleaning thresholds, candidate observations are investigated through descriptive profiling, missing-value assessment, and manual review before any modeling rule is introduced.
- Short movement activities were manually investigated by reviewing activities occurring on the same dates. The objective was to identify the transition point where records began to resemble genuine workouts rather than accidental activity starts.
- Activities with a recorded **Distance** below **0.20 miles** (`Running`, `Walking`, and `Street Running`) consistently appeared to represent incomplete recordings or accidental activity starts. These observations were removed from `df_model` while remaining in `df_clean` for auditing and reproducibility.
- Strength Training activities with a **Total Time** below **10 minutes** were manually reviewed and determined to represent incomplete or accidental recordings. These observations were removed from `df_model` while remaining in `df_clean`.
- Not every reviewed feature results in a modeling filter. Features that pass manual inspection remain unchanged, documenting that they were evaluated and determined to be suitable for analysis.
- Apple Health timestamps required timezone normalization before merging with other datasets.

## Step 2 — Build Measurement Database

**Input**

```text
data/raw/measurements.csv
```

**Purpose**

This step establishes the project's measurement database. The original body measurement records are imported into a raw MySQL table, validated, standardized, and exported as a cleaned dataset that will later be integrated with Apple Health and myNetDiary body-composition records.

---

### Step 2.1 — Create the Raw SQL Table

Open:

```text
sql/measurement.sql
```

Run **Section 1 only**.

This creates the raw `measurements` table inside the `fitnessData` MySQL database.

## ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

**Do not continue to Section 2 yet.**

## ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

---

### Step 2.2 — Load the Raw Data

Run:

```text
scripts/cleaning/load_measurements.py
```

Originally, the raw `measurements.csv` file was intended to be imported directly using the MySQL Import Wizard. However, the import repeatedly failed because the dataset contains many sparse numeric columns where body measurements were intentionally left blank.

Rather than modifying the original dataset to satisfy the import tool, this script loads the raw CSV using Pandas and inserts the records into MySQL programmatically while preserving the original data.

During the import the script:

- Converts pandas missing values (`NaN`) into SQL `NULL` values.
- Truncates the existing table before loading to prevent duplicate imports during repeated execution.
- Inserts every observation into the raw `measurements` table.
- Preserves the original measurement values without performing any cleaning or transformations.

---

### Step 2.3 — Validate and Standardize the SQL Table

Return to:

```text
sql/measurement.sql
```

Run **Section 2**.

This section:

- Verifies the import completed successfully.
- Confirms the expected number of records were imported.
- Converts the imported date column into the SQL `DATE` datatype.
- Checks for duplicate measurement dates.
- Creates the finalized `measurements_clean` table ordered by descending date.
- Performs final validation of the cleaned table.

---

### Step 2.4 — Export the Cleaned Dataset

Using MySQL Workbench, manually export the `measurements_clean` table.

Save the exported CSV to:

```text
data/cleaned/
```

This exported dataset is used during later stages of the project for dataset integration, feature engineering, and downstream statistical analyses.

---

---

## Step 3 — Extract Apple Health Datasets

**Input**

```text
data/raw/apple_export.xml
```

### Step 3.1 — Audit Available HealthKit Record Types

Use the terminal to inspect the available HealthKit record types contained in the Apple Health XML export.

### Step 3.2 — Extract Selected HealthKit Datasets

Run:

```text
scripts/cleaning/apple_health_extract.py
```

This script extracts the selected HealthKit record types into individual raw CSV files.

Output:

```text
data/processed/apple_data_raw_extract/
```

---

## Step 4 — Clean Apple Health Datasets

**Input**

```text
data/processed/apple_data_raw_extract/
```

Run:

```text
scripts/cleaning/clean_apple_health_data.py
```

**Purpose**

This script performs the initial cleaning and validation of every extracted Apple Health dataset.

The cleaning process includes:

- Standardizing column names.
- Converting `start_date` and `end_date` into datetime objects.
- Auditing dataset structure.
- Reporting missing values.
- Reporting column data types.
- Reporting date ranges.
- Reporting duplicate dates where appropriate.
- Saving cleaned datasets.

Output:

```text
data/cleaned/apple/
```

These cleaned datasets become the input for later feature engineering and dataset integration.

---

## Step 5 — Build Daily Apple Health Datasets

**Input**

```text
data/cleaned/apple/
```

Run

```text
scripts/processing/build_daily_health_metrics.py
```

**Purpose**

The cleaned Apple Health datasets still contain timestamp-level observations, with many metrics recorded hundreds or thousands of times throughout a single day. Because the downstream analysis is performed at the daily level, these high-frequency observations are standardized into one daily record per metric.

Each dataset is processed according to the type of measurement it represents.

### Daily Accumulated Metrics

The following datasets are aggregated by calendar date using the daily sum of the recorded values.

- Active Energy Burned
- Apple Exercise Time
- Basal Energy Burned
- Distance Walking Running
- Flights Climbed
- Step Count

### Daily Physiological Metrics

The following datasets are aggregated by calendar date using the daily mean of the recorded values.

- Heart Rate
- Heart Rate Variability (SDNN)
- Respiratory Rate
- Walking Heart Rate Average
- Walking Speed
- Walking Step Length

### Point Measurements

The following datasets already represent individual body measurements and therefore require no aggregation.

- Body Mass
- Body Mass Index
- Waist Circumference

For every processed dataset, the script:

- Converts timestamps into calendar dates (`YYYY-MM-DD`).
- Removes unnecessary columns.
- Produces a standardized schema consisting of:

```text
date
unit
value
```

- Rounds numeric values to two decimal places.
- Saves the resulting daily datasets for downstream feature engineering.

**Output**

```text
data/processed/apple_daily/
```

These daily datasets provide the standardized inputs used during later stages of feature engineering and dataset integration.

---

## Step 6 — Extract myNetDiary Measurements

**Input**

```text
data/raw/myNetDiary/Measurements-*.csv
```

Run

```text
scripts/cleaning/mynet_measurement_extract.py
```

**Purpose**

This step consolidates historical myNetDiary measurement exports into standardized datasets for downstream integration with the project's manually collected body measurements and Apple Health records.

The script automatically:

- Loads every `Measurements-*.csv` file found in the raw myNetDiary directory.
- Combines the exports into a single dataset.
- Separates body-composition measurements from daily step records.
- Standardizes the date column.
- Sorts observations chronologically.
- Performs duplicate-date and duplicate-measurement audits.
- Reports measurement counts and date ranges.
- Saves cleaned datasets for later SQL integration.

**Outputs**

```text
data/cleaned/myNetDiary/
├── mynet_body_measurements.csv
└── mynet_daily_steps.csv
```

**Validation**

Verify that:

- Measurement counts match the original exports.
- No duplicate body measurements exist for the same date and measurement type.
- No duplicate daily step dates exist.
- Date ranges match the original myNetDiary exports.

---
