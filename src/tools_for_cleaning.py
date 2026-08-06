import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import csv
from datetime import timedelta


# _________LOAD AND SAVE
def load_csv(file_name):

    df = pd.read_csv(file_name)

    print(
        f"Loaded {len(df)} rows"
    )

    return df

def save_csv(df, file_name):
    df.to_csv(
        file_name,
        index=False
    )

    print(
        f"Saved {len(df)} rows to {file_name}"
    )

# get file names of current fed path
def get_file_names( 
        directory,
    pattern="*_raw2.csv"
):

    file_names = []

    for file in Path(directory).rglob(pattern):
        file_names.append(file.name)

    return file_names  

# convert to NUMBER
def convert_value_to_numeric(df):

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    return df
def standardize_date_column(df, column_name="date"):
    
    """ Convert a date column to pandas datetime.
    Invalid dates become NaT. """

    df[column_name] = pd.to_datetime(
        df[column_name],
        errors="coerce"
    )
    return df

# make sure names have lower case and commas.
def standardize_column_names(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

def remove_suffix(
    file_names,
    suffix="_raw.csv"
):

    cleaned_names = []

    for name in file_names:

        cleaned_names.append(
            name.replace(
                suffix,
                "_clean_v1.csv"
            )
        )

    return cleaned_names


# Usage: df = convert_value_to_numeric(df)
#  GET range of dates
# def report_duplicate_dates(
#     df,
#     date_column="date"
# ):

#     duplicate_count = (
#         df[date_column]
#         .duplicated()
#         .sum()
#     )

#     print(
#         f"\nDuplicate Dates: {duplicate_count}"
#     )

def report_duplicate_dates(df, date_column="date"):

    duplicates = df[
        df[date_column].duplicated(keep=False)
    ]

    print(f"\nDuplicate Dates: {len(duplicates)}")

    if duplicates.empty:
        print("No duplicate dates found.")
    else:
        print("Duplicate dates found:")
        print(
            duplicates
            .sort_values(date_column)
            .to_string(index=False)
        )

    return duplicates

def report_missing_values(df):
    print("\nMissing Values")
    print(df.isna().sum())

def report_date_range(df, date_column):

    print("\nDate Range")

    print(
        "Min:",
        df[date_column].min()
    )

    print(
        "Max:",
        df[date_column].max()
    )

def detect_value_type(df):

    numeric_values = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    if numeric_values.notna().all():
        return "numeric"

    return "categorical"

def report_column_types(df):
    print("\nColumn Types")
    print(df.dtypes)

def col_names(df):
  print("Col Names\n",df.columns.tolist())   

def show_rows(df, n=3):
    # .to_string() is here to force pandas to print every column
    print(df.head(n).to_string())   


    
     
def dataset_summary(df):

    print("\nRows:", len(df))
    print("Columns:", len(df.columns))

    report_column_types(df)

    report_missing_values(df)








def build_inventory(data_dir):

    inventory = []

    for csv_file in Path(data_dir).glob("*_raw.csv"):

        df = pd.read_csv(csv_file)

        inventory.append({
            "file_name": csv_file.name,
            "rows": len(df),
            "columns": len(df.columns)
        })

    inventory_df = pd.DataFrame(inventory)

    return inventory_df.sort_values(
        "rows",
        ascending=False
    )





def count_unique_values(df, column_name):

    count = (
        df[column_name]
        .nunique()
    )

    print(
        f"\nUnique {column_name}: {count}"
    )

    return count

def report_unique_dates(
    df,
    date_column
):

    unique_dates = (
        df[date_column]
        .nunique()
    )

    print(
        f"\nUnique Dates: {unique_dates}"
    )

    return unique_dates


#  code needed for extracting large apple data
def extract_health_records(
    input_file,
    output_file,
    target_type
):
    """
    Extract a specific Apple Health record type
    from export.xml into a CSV file.
    """

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "source_name",
            "unit",
            "start_date",
            "end_date",
            "value"
        ])

        count = 0

        for event, elem in ET.iterparse(
            input_file,
            events=("end",)
        ):

            if (
                elem.tag == "Record"
                and elem.attrib.get("type") == target_type
            ):

                writer.writerow([
                    elem.attrib.get("sourceName"),
                    elem.attrib.get("unit"),
                    elem.attrib.get("startDate"),
                    elem.attrib.get("endDate"),
                    elem.attrib.get("value")
                ])

                count += 1

            elem.clear()

    print(
        f"\nYay! I exported {count} records "
        f"to {output_file} \n⋆✦⋆ cute ⋆✦⋆"
    )    






# aduit functions


def audit_csv_file(file_path):

    print("\n" + "=" * 50)

    print(
        Path(file_path).name
    )

    df = load_csv(file_path)

    report_column_types(df)

    report_missing_values(df)

    show_rows(df)

    return df




def convert_to_datetime(df, column_name):
    df[column_name] = pd.to_datetime(
        df[column_name]
    )
    return df

def create_date_column(
    df,
    source_column="start_date",
    new_column="date"
):
    df[new_column] = (
        pd.to_datetime(
            df[source_column]
        )
        .dt.normalize()
    )

    return df

# used for APPLE agg
# def aggregate_daily_sum(
#     df,
#     date_column="start_date",
#     value_column="value"
# ):
#     temp = df.copy()

#     temp["date"] = (
#         pd.to_datetime(
#             temp[date_column]
#         )
#         .dt.normalize()
#     )

#     daily = (
#         temp
#         .groupby("date")[value_column]
#         .sum()
#         .reset_index()
#     )

#     daily["date"] = daily["date"].dt.date
#     daily["value"] = daily["value"].round(2)

#     return daily
# used for GARMIN aggr
def aggregate_daily_sum(
    df,
    date_column="start_date",
    value_column="value"
):
    temp = df.copy()

    # Remove rows where this metric is missing
    temp = temp[
        temp[value_column].notna()
    ]

    temp["date"] = (
        pd.to_datetime(
            temp[date_column]
        )
        .dt.normalize()
    )

    daily = (
        temp
        .groupby("date")[value_column]
        .sum()
        .reset_index()
    )

    daily["date"] = daily["date"].dt.date

    daily[value_column] = (
        daily[value_column]
        .round(2)
    )

    return daily
# used for APPLE agre
# def aggregate_daily_mean(
#     df,
#     date_column="start_date",
#     value_column="value"
# ):

#     temp = df.copy()

#     temp["date"] = (
#         pd.to_datetime(
#             temp[date_column]
#         )
#         .dt.normalize()
#     )

#     daily = (
#         temp
#         .groupby("date")[value_column]
#         .mean()
#         .reset_index()
#     )


#     daily["date"] = daily["date"].dt.date
#     daily["value"] = daily["value"].round(2)

#     return daily
# used for GARMIN aggre

def aggregate_daily_mean(
    df,
    date_column="start_date",
    value_column="value"
):

    temp = df.copy()

    # Remove rows where the metric is missing
    temp = temp[
        temp[value_column].notna()
    ]

    temp["date"] = (
        pd.to_datetime(
            temp[date_column]
        )
        .dt.normalize()
    )

    daily = (
        temp
        .groupby("date")[value_column]
        .mean()
        .reset_index()
    )

    daily["date"] = daily["date"].dt.date

    daily[value_column] = (
        daily[value_column]
        .round(2)
    )

    return daily

def get_window(
    df,
    end_date,
    days
):
    start_date = (
        end_date
        - timedelta(days=days-1)
    )

    return df[
        (df["date"] >= start_date)
        &
        (df["date"] <= end_date)
    ]


def aggregate_metric_before_measurement(
    measurement_date,
    df,
    method="mean",
    days=7,
    value_column="value"
):

    window = get_window(
        df,
        measurement_date,
        days
    )

    if len(window) == 0:
        return np.nan

    if method == "sum":
        return window[value_column].sum()

    elif method == "mean":
        return window[value_column].mean()

    elif method == "max":
        return window[value_column].max()

    elif method == "min":
        return window[value_column].min()

    else:
        raise ValueError(f"Unknown aggregation method: {method}")






def audit_dataset(
    df,
    dataset_name,
    date_column="Date"
):

    print("\n" + "=" * 70)
    print(f"AUDIT: {dataset_name}")
    print("=" * 70)
    print(f"\nRows: {len(df)}")

    report_date_range(
        df,
        date_column
    )
    print("\nColumn Types")
    print(df.dtypes)

    print("\nSources")

    if "Source" in df.columns:
        print(df["Source"].value_counts())
    else:
        print("N/A (aggregated dataset)")
    

    report_duplicate_dates(
        df,
        date_column
    )


def audit_duplicate_measurements(
    df,
    date_column="Date",
    value_column="Value",
    threshold=1.0
):

    duplicate_dates = (
        df.loc[
            df[date_column].duplicated(keep=False),
            date_column
        ]
        .drop_duplicates()
    )
    if len(duplicate_dates) == 0:
        print("\n" + "=" * 70)
        print("AUDIT: DUPLICATE MEASUREMENTS")
        print("=" * 70)
        print("\nDuplicate Dates: 0")
        print("No duplicate measurements found, Slay! 👽")

    for date in duplicate_dates:

        group = (
            df[df[date_column] == date]
            .sort_values("Start")
            .copy()
        )

        # Keep the ORIGINAL dataframe index
        group["Row"] = group.index

        group["Time"] = (
            group["Start"]
            .dt.strftime("%I:%M %p")
        )

        print("\n" + "#" * 70)
        print("AUDIT: DUPLICATE RESOLUTION SUGGESTION")
        # print(f"DATE: {date.date()}")
        print("#" * 70)
        median_value = group[value_column].median()

        print(f"\nMedian = {median_value:.3f}")

        for _, row in group.iterrows():

            difference = abs(
                row[value_column] - median_value
            )

            if difference > threshold:

                print(
                    f"REMOVE? "
                    f"Row={row['Row']}  "
                    f"{row['Time']}  "
                    f"{row[value_column]:.3f} "
                    f"({row['Source']}) "
                    f"Difference={difference:.3f}"
                )

            else:

                print(
                    f"KEEP    "
                    f"Row={row['Row']}  "
                    f"{row['Time']}  "
                    f"{row[value_column]:.3f} "
                    f"({row['Source']}) "
                    f"Difference={difference:.3f}"
                )












def audit_dense_dataset(
    df,
    dataset_name,
    date_column="Date"
):

    print("\n" + "=" * 70)
    print(f"AUDIT: {dataset_name}")
    print("=" * 70)
    print(f"\nRows: {len(df)}")

    report_date_range(
        df,
        date_column
    )
    print("\nColumn Types")
    print(df.dtypes)

    print("\nSources")

    if "Source" in df.columns:

        print(df["Source"].value_counts())

    else:

        print("N/A (aggregated dataset)")
                    




def audit_dense_timeseries(
    df,
    date_column="Date"
):

    print("\n" + "#" * 70)
    print("AUDIT: DENSE TIME SERIES")
    print("#" * 70)

    records_per_day = (
        df
        .groupby(date_column)
        .size()
    )

    print(
        "\nUnique Days:",
        records_per_day.size
    )

    print("\nRecords Per Day")

    print(
        "Mean:    ",
        round(records_per_day.mean(), 1)
    )

    print(
        "Median:  ",
        records_per_day.median()
    )

    print(
        "Maximum: ",
        records_per_day.max()
    )

    print("\nTop 10 busiest days\n")

    print(
        records_per_day
        .sort_values(ascending=False)
        .head(10)
    )
    print("\nValues")

    print(
        "Minimum:",
        df["Value"].min()
    )

    print(
        "Median:",
        df["Value"].median()
    )

    print(
        "Maximum:",
        df["Value"].max()
    )

    print(
        "Mean:",
        round(df["Value"].mean(), 2)
    )




     

def aggregate_by_date(
    df,
    aggregations,
    date_column="Date"
):
    """
    Aggregate records by date.

    Parameters
    ----------
    df : pandas.DataFrame

    aggregations : dict
        Example:
        {
            "Value": "sum",
            "Source": "first"
        }

    date_column : str
        Column used for grouping.

    Returns
    -------
    pandas.DataFrame
    """

    return (
        df
        .groupby(
            date_column,
            as_index=False
        )
        .agg(aggregations)
    )



################################
# Feature Engineering
################################

def rolling_average(
    df,
    value_column,
    window,
    date_column="Date"
):
    temp = (
        df.sort_values(date_column)
        .copy()
    )

    new_column = f"{value_column}_{window}DayAvg"

    temp[new_column] = (
        temp[value_column]
        .rolling(
            window=window,
            min_periods=1
        )
        .mean()
    )

    if window == 7:
        temp.loc[
            ~temp["Valid7Day"],
            new_column
        ] = np.nan

    elif window == 30:
        temp.loc[
            ~temp["Valid30Day"],
            new_column
        ] = np.nan

    return temp



def rolling_sum(
    df,
    value_column,
    window,
    date_column="Date"
):
    temp = (
        df.sort_values(date_column)
        .copy()
    )

    new_column = f"{value_column}_{window}DaySum"

    temp[new_column] = (
        temp[value_column]
        .rolling(
            window=window,
            min_periods=1
        )
        .sum()
    )

    return temp



def label_consecutive_streaks(
    df,
    date_column="Date"
):

    temp = (
        df
        .sort_values(date_column)
        .copy()
    )

    temp["DaysSincePrevious"] = (
        temp[date_column]
        .diff()
        .dt.days
    )

    gap = (
        temp["DaysSincePrevious"]
        .fillna(1)
    )
    temp["GapStartsHere"] = (
    temp["DaysSincePrevious"] > 1
)

    temp["StreakID"] = (
        gap.ne(1)
        .cumsum()
    )

    temp["StreakLength"] = (
        temp
        .groupby("StreakID")[date_column]
        .transform("count")
    )

    temp["DayInStreak"] = (
    temp
    .groupby("StreakID")
    .cumcount()
    + 1
)
    temp["Valid7Day"] = (
    temp["DayInStreak"] >= 7
)


      

    temp["Valid30Day"] = (
        temp["DayInStreak"] >= 30
    )
    

    return temp