from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from tools_for_cleaning import *

INPUT_DIR = PROJECT_ROOT / "data" / "cleaned" / "apple"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "apple_daily"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)
# dictionary maps the filename to the aggregation method.
AGGREGATION_METHOD = {

    # Daily totals
    "activeenergyburned_clean.csv": "sum",
    "appleexercisetime_clean.csv": "sum",
    "basalenergyburned_clean.csv": "sum",
    "distancewalkingrunning_clean.csv": "sum",
    "flightsclimbed_clean.csv": "sum",
    "stepcount_clean.csv": "sum",

    # Daily averages
    "heartrate_clean.csv": "mean",
    "heartratevariabilitysdnn_clean.csv": "mean",
    "walkingheartrateaverage_clean.csv": "mean",
    "walkingspeed_clean.csv": "mean",
    "walkingsteplength_clean.csv": "mean",
    "respiratoryrate_clean.csv": "mean",

    # Point measurements
    "bodymass_clean.csv": "point",
    "bodymassindex_clean.csv": "point",
    "waistcircumference_clean.csv": "point",
}

# now that the three groups have been identified I will create three seprate functions 
def process_point_measurements(df):

    df = convert_to_datetime(
        df,
        "start_date"
    )

    df = create_date_column(
        df,
        "start_date",
        "date"
    )
    df["date"] = pd.to_datetime(df["date"]).dt.date

    df = (
        df[
            ["date","unit","value"]
        ]
        .copy()
    )

    return df
def process_daily_sum(df):

    df = convert_to_datetime(
        df,
        "start_date"
    )

    daily = aggregate_daily_sum(
        df,
        date_column="start_date",
        value_column="value"
    )

    daily["unit"] = (
        df["unit"]
        .iloc[0]
    )

    return daily[
        ["date","unit","value"]
    ]


def process_daily_mean(df):

    df = convert_to_datetime(
        df,
        "start_date"
    )

    daily = aggregate_daily_mean(df)

    daily["unit"] = (
        df["unit"]
        .iloc[0]
    )

    return daily[
        ["date","unit","value"]
    ]


# driver for the three functions above
for filename, method in AGGREGATION_METHOD.items():

    print(f"\nProcessing {filename}")

    input_file = INPUT_DIR / filename

    df = load_csv(input_file)

    df = convert_value_to_numeric(df)

    if method == "sum":
        df = process_daily_sum(df)

    elif method == "mean":
        df = process_daily_mean(df)

    elif method == "point":
        df = process_point_measurements(df)

    output_file = OUTPUT_DIR / filename

    save_csv(
        df,
        output_file
    )