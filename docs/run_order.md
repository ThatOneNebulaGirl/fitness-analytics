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

This step builds the project's measurement database. The original body measurement records are imported into a raw MySQL table, validated, standardized, and exported as a cleaned dataset for downstream integration and analysis.

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

This script reads the original `measurements.csv` file and imports every observation into the SQL table.

During the import the script:

- Converts pandas missing values (`NaN`) into SQL `NULL` values.
- Truncates the existing table before loading to prevent duplicate imports.
- Preserves the raw measurement values without performing any cleaning or transformations.

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

**Purpose**

Apple Health exports all <span style="color:lime">HealthKit</span> data into a single XML file containing more than 1.7 million records across dozens of different HealthKit record types. Before cleaning or analysis can begin, the available record types must first be identified so that only datasets relevant to this project are extracted.

---

### Step 3.1 — Audit Available HealthKit Record Types

Using the terminal, inspect the Apple Health XML export to identify the available <span style="color:lime">HealthKit</span> record types.

Example:

```bash
grep '<Record type="' apple_export.xml \
| sed -n 's/.*type="\([^"]*\)".*/\1/p' \
| sort \
| uniq
```

After identifying the available <span style="color:lime">HealthKit</span> record types, perform a second audit to determine the frequency of project-relevant datasets.

Example:

```bash
grep '<Record type="' apple_export.xml \
| sed -n 's/.*type="\([^"]*\)".*/\1/p' \
| awk '
/Sleep|Energy|Exercise|Walking|Body|Flights|Heart|Waist|Count/ {
    count[$0]++
}
END {
    for (k in count)
        printf "%8d %s\n", count[k]
}' \
| sort -nr
```

This audit is used to determine which <span style="color:lime">HealthKit</span> datasets should be extracted and which can be excluded from the remainder of the project.

---

### Step 3.2 — Extract Selected HealthKit Datasets

Run:

```text
scripts/cleaning/apple_health_extract.py
```

This script:

- Reads the Apple Health XML export.
- Discovers all available HealthKit record types.
- Filters record types using project-specific keywords.
- Excludes HealthKit datasets that are not used in this study.
- Exports each selected <span style="color:lime">HealthKit</span> record type into its own raw CSV file.

The extracted datasets are saved to:

```text
data/processed/apple_data_raw_extract/
```

These raw CSV files become the input for the Apple Health cleaning pipeline.
