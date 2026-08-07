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

<div style="color:red; font-weight:bold;">
## ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

**Do not continue to Section 2 yet.**

## ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

## </div>

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

# Step 6 — Load Daily Apple Health Datasets into MySQL

**Input**

```text
data/processed/apple_daily/
```

Run

```text
scripts/loading/load_appleFeatures.py
```

**Purpose**

The processed Apple Health datasets are now stored as standardized daily observations, but they still exist only as CSV files. Rather than importing each dataset manually through MySQL Workbench, this project uses a reusable Python ETL pipeline to automatically populate the SQL database.

The loading pipeline consists of reusable loading utilities together with a single driver script that automatically discovers every processed Apple Health dataset and imports it into its corresponding SQL table.

The pipeline performs the following steps for every dataset:

- Automatically discovers every `*_clean.csv` file inside `data/processed/apple_daily/`.
- Determines the destination SQL table from the filename.
- Loads the CSV into Pandas.
- Converts date columns into SQL-compatible datatypes.
- Renames feature columns to match the SQL schema.
- Truncates the destination table before loading to prevent duplicate imports.
- Bulk inserts every observation into MySQL.
- Validates the imported row count.
- Displays sample observations for verification.

The reusable loading utilities are implemented in:

```text
src/tools_for_loading_SQL.py
```

while the automated ETL pipeline is executed from:

```text
scripts/loading/load_appleFeatures.py
```

**Output**

```text
fitnessData (MySQL)

├── activeenergyburned
├── appleexercisetime
├── basalenergyburned
├── bodymass
├── bodymassindex
├── distancewalkingrunning
├── flightsclimbed
├── heartrate
├── heartratevariabilitysdnn
├── respiratoryrate
├── stepcount
├── waistcircumference
├── walkingheartrateaverage
├── walkingspeed
└── walkingsteplength
```

At the completion of this step, every processed Apple Health feature has been loaded into MySQL using a reproducible ETL pipeline. These tables provide the standardized SQL inputs used during subsequent body-composition integration, feature engineering, and statistical analysis.

---

# Step 7 — Extract myNetDiary Measurements

**Input**

```text
data/raw/myNetDiary/
```

Run

```text
scripts/cleaning/load_mynet_measurements.py
```

**Purpose**

Extract the historical body-composition measurements from the archived myNetDiary export. Retain only measurements relevant to the project while excluding derived or sparsely populated variables.

**Output**

```text
data/cleaned/myNetDiary/
```

---

# Step 8 — Reshape myNetDiary Body Measurements

**Input**

```text
data/cleaned/myNetDiary/
```

Run

```text
scripts/cleaning/mynet_pivot_measurements.py
```

**Purpose**

Convert the long-format myNetDiary measurement records into a wide-format table where each measurement date occupies one row and each body measurement occupies its own dedicated column. This creates a schema compatible with the manually collected measurement database.

**Output**

```text
data/cleaned/measurements_clean_myNetDiary.csv
```

---

# Step 9 — Integrate myNetDiary Body Measurements

**Input**

```text
data/cleaned/measurements_clean_myNetDiary.csv
```

Run

```text
sql/mynet_measurements.sql
```

**Purpose**

Validate imported measurement dates, identify duplicate observations, and merge only unique historical chest, waist, and hip measurements into the validated `measurements_clean` database.

The resulting SQL table is validated by confirming the expected record count, checking for duplicate dates, and verifying chronological ordering.

**Output**

```text
measurements_clean
```

---

# Step 10 — Integrate Apple Health Waist Measurements

**Input**

```text
data/processed/apple_daily/waistcircumference_clean.csv
```

Run

```text
sql/waist_data_integration.sql
```

**Purpose**

Compare Apple Health waist circumference measurements against the validated measurement database. Existing waist measurements are updated where matching dates already exist, while new historical observations are inserted only when no corresponding measurement date is present.

The merged dataset is validated by checking record counts, duplicate dates, and chronological ordering to ensure a single longitudinal waist measurement history.

**Output**

```text
measurements_clean
```

---

# Step 11 — Build Apple Feature Windows

**Input**

```text
data/raw/weight_aug2026.csv

data/processed/apple_daily/
```

**Run**

```text
scripts/processing/build_apple_features.py
```

**Purpose**

The processed Apple Health datasets contain one standardized daily observation for each health metric. This step transforms those daily observations into engineered predictor variables aligned with each body-weight measurement.

For every body-weight observation contained within `weight_aug2026.csv`, the script searches the previous seven calendar days of each processed Apple Health dataset and summarizes those observations into a single engineered feature.

Aggregation methods are selected according to the type of metric being processed.

### Seven-Day Totals

The following metrics are summarized using cumulative seven-day totals.

- Active Energy Burned
- Apple Exercise Time
- Basal Energy Burned
- Distance Walking Running
- Flights Climbed
- Step Count

### Seven-Day Averages

The following metrics are summarized using seven-day averages.

- Heart Rate
- Heart Rate Variability (SDNN)
- Respiratory Rate
- Walking Heart Rate Average
- Walking Speed
- Walking Step Length

For every processed dataset the script:

- Loads the processed daily Apple Health dataset.
- Searches the seven days preceding each body-weight measurement.
- Aggregates observations using the appropriate summary statistic.
- Generates one engineered feature for every body-weight observation.
- Exports each engineered feature dataset independently.

The feature engineering utilities are implemented in

```text
src/tools_for_cleaning.py
```

and executed by

```text
scripts/processing/build_apple_features.py
```

**Output**

```text
data/processed/apple_features/

├── activeenergyburned_features.csv
├── appleexercisetime_features.csv
├── basalenergyburned_features.csv
├── distancewalkingrunning_features.csv
├── flightsclimbed_features.csv
├── heartrate_features.csv
├── heartratevariabilitysdnn_features.csv
├── respiratoryrate_features.csv
├── stepcount_features.csv
├── walkingheartrateaverage_features.csv
├── walkingspeed_features.csv
└── walkingsteplength_features.csv
```

These engineered datasets provide the Apple Health predictor variables used to construct the project's final modeling dataset.

---

# Step 12 — Build Garmin Feature Windows

**Input**

```text
data/raw/weight_aug2026.csv

data/processed/garmin_daily/
```

**Run**

```text
scripts/processing/build_garmin_features.py
```

**Purpose**

After the Garmin activity data has been cleaned and aggregated into standardized daily metrics, this step transforms those daily observations into engineered predictor variables aligned with each body-weight measurement.

For every body-weight observation contained within `weight_aug2026.csv`, the script searches the previous seven calendar days of each processed Garmin dataset and summarizes those observations into a single engineered feature.

Aggregation methods are selected according to the type of metric being processed.

### Seven-Day Totals

The following metrics are summarized using cumulative seven-day totals.

- Distance
- Calories
- Total Time
- Steps
- Total Ascent
- Total Descent
- Total Repetitions
- Total Sets

### Seven-Day Averages

The following metrics are summarized using seven-day averages.

- Average Heart Rate
- Maximum Heart Rate
- Average Speed
- Maximum Speed
- Average Stride Length
- Body Battery Drain

For every processed dataset the script:

- Loads the standardized daily dataset.
- Searches the seven days preceding each body-weight measurement.
- Aggregates observations using the appropriate summary statistic.
- Generates one engineered feature for every body-weight observation.
- Exports each engineered feature dataset independently.

The feature engineering utilities are implemented in

```text
src/tools_for_cleaning.py
```

and executed by

```text
scripts/processing/build_garmin_features.py
```

**Output**

```text
data/processed/garmin_features/

├── distance_features.csv
├── calories_features.csv
├── totaltime_features.csv
├── steps_features.csv
├── totalascent_features.csv
├── totaldescent_features.csv
├── totalreps_features.csv
├── totalsets_features.csv
├── avg_hr_features.csv
├── max_hr_features.csv
├── avg_speed_features.csv
├── max_speed_features.csv
├── avg_stride_length_features.csv
└── bodybatterydrain_features.csv
```

These engineered datasets provide the Garmin predictor variables used to construct the project's final modeling dataset.

---

# Step 13 — Build Master Modeling Dataset

**Input**

```text
data/raw/weight_aug2026.csv

data/processed/apple_features/

data/processed/garmin_features/
```

**Run**

```text
scripts/cleaning/build_weight_master_features.py
```

**Purpose**

At this stage, engineered predictor variables have been created independently from both Apple Health and Garmin data. This step combines every engineered feature into a single longitudinal modeling dataset aligned with the recovered body-weight timeline.

The pipeline automatically loads every Apple Health feature dataset and every Garmin feature dataset before merging them using the measurement date as the common key.

After all engineered features have been merged, feature names are standardized to maintain consistent naming conventions across data sources.

Equivalent distance features are then reconciled by treating Garmin distance as the primary source whenever it is available. Apple Health distance is used only to fill historical observations that occurred before Garmin data existed. This preserves the complete historical distance record while avoiding duplicate measurements during periods where both data sources overlap.

The completed dataset contains one row for every body-weight observation together with every engineered predictor variable generated throughout the project.

The script performs the following steps:

- Loads the validated body-weight timeline.
- Merges every Apple Health engineered feature.
- Merges every Garmin engineered feature.
- Standardizes feature names.
- Reconciles overlapping distance features.
- Removes the redundant Apple distance feature after reconciliation.
- Audits the completed modeling dataset.
- Exports the final modeling dataset.

**Output**

```text
data/processed/

└── weight_master_features.csv
```

This dataset serves as the primary input for exploratory data analysis, correlation analysis, visualization, statistical modeling, and machine learning.

---

# Step 14 — Exploratory Statistical Analysis

**Input**

```text
data/processed/weight_master_features.csv
```

**Run**

```text
scripts/analysis/correlation_matrix.py
```

**Purpose**

This step performs exploratory analysis of the completed modeling dataset by computing Pearson correlation coefficients among the engineered behavioral, physiological, and body-composition variables.

The correlation matrix is used to identify candidate predictors for subsequent regression modeling while providing an overview of the relationships present within the longitudinal dataset.

The script performs the following steps:

- Loads the completed modeling dataset.
- Computes the Pearson correlation matrix.
- Exports the full correlation matrix.
- Generates a publication-quality correlation heatmap.

**Output**

```text
data/processed/
└── correlation_matrix.csv

figures/
└── correlation_matrix.png
```

---

# Step 15 — Regression Screening

**Input**

```text
data/processed/weight_master_features.csv
```

**Run**

```text
scripts/analysis/weight_regression.py
```

**Purpose**

Each engineered predictor is independently evaluated using ordinary least squares (OLS) regression to quantify its relationship with body weight.

For every predictor, the script computes:

- Sample size
- Pearson correlation
- Regression equation
- Coefficient of determination (R²)
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- t-statistic
- F-statistic
- p-value
- 95% confidence interval

Regression diagnostic figures are also generated to evaluate residual behavior and assess the assumptions of linear regression.

**Output**

```text
figures/
└── weight_regression/
    ├── tier1/
    ├── tier2/
    └── diagnostics/
```

The regression screening process identifies the strongest candidate predictors for subsequent statistical modeling.

---

# Step 16 — Multiple Linear Regression

**Input**

```text
data/processed/weight_master_features.csv
```

**Run**

```text
scripts/analysis/multiple_regression.py
```

**Purpose**

Construct a multiple linear regression model using the strongest predictors identified during the regression screening phase. Evaluate predictor independence, quantify multicollinearity using Variance Inflation Factors (VIFs), compare candidate models, and assess model assumptions using regression diagnostic plots.

The script performs the following steps:

- Loads the completed modeling dataset.
- Selects candidate predictors retained from regression screening.
- Removes incomplete observations.
- Computes predictor correlation matrix.
- Calculates Variance Inflation Factors (VIFs).
- Fits the multiple linear regression model.
- Reports regression coefficients and statistical inference.
- Computes MAE and RMSE.
- Generates regression diagnostic figures.

**Output**

```text
figures/multiple_regression/

├── multiple_regression_predictor_correlation.png
├── multiple_regression_residuals.png
├── multiple_regression_qqplot.png
└── multiple_regression_actual_vs_predicted.png
```

This analysis identifies the final multivariable statistical model used throughout the project.

---

---

# Step 17 — Jupyter Notebook

**Input**

```text
data/processed/weight_master_features.csv

figures/

outputs from Steps 1–16
```

**Open**

```text
notebooks/Longitudinal_Fitness_Analytics.ipynb
```

**Purpose**

The notebook serves as the final analytical report for the project. It documents the complete engineering workflow, data-cleaning methodology, feature engineering, exploratory analyses, statistical modeling, regression diagnostics, and project conclusions.

Rather than performing additional data processing, the notebook integrates the outputs generated throughout the previous steps into a reproducible research document that explains the analytical decisions, presents the statistical findings, discusses project limitations, and outlines future directions for continued data collection and model development.

**Output**

```text
Final reproducible analytical report
```

This notebook represents the culmination of the complete analytics pipeline and should be executed only after all previous processing, feature engineering, and statistical analysis steps have been completed successfully.
