# Longitudinal Fitness Analytics

## Overview

The frustration of not seeing meaningful changes in my body composition led me to ask a simple question:

> _Why isn't my body composition changing?_

Although I had years of health and fitness data, the answer wasn't obvious. The information was scattered across multiple platforms, making it difficult to evaluate long-term trends or determine whether my training habits were producing measurable results.

Instead of relying on memory, intuition, or how I felt after a workout, I wanted evidence. I wanted to know whether the data actually supported the conclusions I was drawing about my own progress, and whether my reasoning could stand up to the data rather than assumptions.

Answering that question required building an end-to-end analytics pipeline that integrates four independent health data sources, cleans and validates heterogeneous datasets, engineers analytical features, and prepares both an auditable cleaned dataset (`df_clean`) and a modeling dataset (`df_model`) for statistical modeling.

The overall data pipeline follows the workflow below:

```text
Raw exports
      │
      ▼
Python ingestion
      │
      ▼
MySQL relational database
      │
      ▼
SQL validation & cleaning
      │
      ▼
Merged analytical datasets
      │
      ▼
Statistical analysis
```

The resulting pipeline supports longitudinal analyses of body composition, training volume, strength progression, recovery metrics, and relationships between exercise behavior and physical outcomes.

---

## Skills Demonstrated

This project demonstrates:

- Python
- Pandas
- NumPy
- SQL (MySQL)
- Data Cleaning
- ETL Pipelines
- Data Integration
- Feature Engineering
- Exploratory Data Analysis (EDA)
- Statistical Analysis
- Pearson Correlation Analysis
- Linear Regression
- Regression Diagnostics
- Hypothesis Testing
- Data Visualization
- Longitudinal Data Analysis
- Reproducible Research

---

## Research Questions

This project investigates questions including:

- Can weekly training volume predict changes in waist circumference?
- Which physiological and training metrics are most strongly associated with body composition?
- How do body measurements change over time relative to exercise behavior?
- Can historical activity data be transformed into measurement windows suitable for predictive modeling?
- How has strength progressed over time after accounting for changes in body weight?
- Which variables appear to have the strongest relationships with long-term fitness outcomes?

---

## Data Sources

The project combines data exported from four independent platforms:

- Garmin Connect
- Apple Health
- myNetDiary
- Manual body measurements

These datasets are imported into a relational MySQL database, validated and standardized through a combination of Python and SQL workflows, and ultimately merged into unified analytical datasets for downstream statistical modeling.

---

## Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- MySQL
- Jupyter Notebook
- Garmin Connect
- Apple Health
- Git
- GitHub

---

## Repository Structure

```text
fitness-analytics/
├── notebooks/
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
├── scripts/
├── src/
├── sql/
├── figures/
├── docs/
├── config/
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/ThatOneNebulaGirl/fitness-analytics.git
cd fitness-analytics
```

Required software

- Python 3.12+
- Jupyter Notebook
- MySQL 8+

---

## Usage

The project is designed as a reproducible analytics pipeline.

The recommended execution order is documented in:

```text
docs/run_order.md
```

The pipeline performs:

- Garmin activity data cleaning and validation
- Apple Health XML record discovery and extraction
- Construction of raw MySQL database tables
- SQL-based validation and standardization
- Data cleaning and datatype conversion
- Feature profiling and quality assessment
- Construction of auditable cleaned datasets (`df_clean`)
- Construction of modeling datasets (`df_model`)
- Feature engineering
- Dataset integration across multiple health platforms
- Statistical analysis
- Visualization generation

---

## Results

The completed pipeline produces reproducible analytical datasets supporting exploratory statistical analyses of longitudinal fitness behavior.

Current analyses include:

- Relative strength progression adjusted for body weight.
- Longitudinal body-weight and body-composition trends.
- Seven-day measurement-window feature engineering.
- Pearson correlation analysis across engineered behavioral and physiological features.
- Simple linear regression screening of engineered predictors.
- Regression diagnostics, including residual analysis and normal Q–Q assessment.
- Identification of behavioral features most strongly associated with body weight.

Current findings indicate that weekly Apple Step Count and Distance exhibited the strongest linear relationships with body weight, while Walking Step Length demonstrated a weaker but statistically significant association. The remaining engineered predictors explained little of the observed variation in body weight.

_(Representative figures will be added as the project continues.)_

---

## Documentation

Additional documentation is located in the `docs/` directory.

- `run_order.md` — execution order for reproducing the project.
- Additional documentation describing the data pipeline and methodology.

---

## Future Improvements

Potential future extensions include:

- Time-series forecasting of body composition.
- Machine learning models for predicting measurement outcomes.
- Interactive dashboards for exploratory analysis.
- Automated Garmin and Apple Health data ingestion.
- Expanded statistical validation and model comparison.

---

## License

MIT License
