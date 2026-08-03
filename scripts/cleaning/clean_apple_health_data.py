from pathlib import Path
import sys

# --------------------------------------------------
# Project Paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = PROJECT_ROOT / "src"

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apple_data_raw_extract"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "apple"
)

sys.path.insert(0, str(SRC_DIR))
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# --------------------------------------------------
# Imports
# --------------------------------------------------

from tools_for_cleaning import (
    get_file_names,
    load_csv,
    save_csv,
    standardize_date_column,
    report_column_types,
    report_missing_values,
    report_date_range,
    count_unique_values,
    show_rows,
)

# --------------------------------------------------
# Process Files
# --------------------------------------------------
file_names = get_file_names(RAW_DIR)
print("RAW_DIR:", RAW_DIR)
print("Number of files:", len(file_names))
print(file_names)


for file_name in file_names:

    print("\n" + "=" * 50)
    print(file_name)

    file_path = RAW_DIR / file_name

    # Load
    df = load_csv(file_path)

    # Standardize
    df = standardize_date_column(df, "start_date")
    df = standardize_date_column(df, "end_date")

    # Audit
    report_column_types(df)
    report_missing_values(df)
    show_rows(df)
    report_date_range(df, "start_date")
    count_unique_values(df, "start_date")

    # Save
    clean_name = file_name.replace(
        "_raw2.csv",
        "_clean.csv"
    )

    output_file = OUTPUT_DIR / clean_name

    save_csv(
        df,
        output_file
    )