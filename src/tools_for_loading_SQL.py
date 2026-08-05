"""
============================================================
TOOLS FOR LOADING
============================================================

Reusable functions for importing cleaned CSV files into MySQL.

Author: Melody Sanchez
Project: Longitudinal Fitness Analytics
"""

import pandas as pd

# ============================================================
# DATABASE
# ============================================================

from config.credentials import get_connection


# ============================================================
# CONNECTION
# ============================================================

def close_connection(connection):
    """
    Close MySQL connection.
    """

    connection.close()

    print("Connection closed.")


# ============================================================
# CSV
# ============================================================

def load_csv(file_path):
    """
    Load a CSV into a pandas DataFrame.
    """

    df = pd.read_csv(file_path)

    print(f"Loaded {len(df)} rows.")
    print(df.head())

    return df


def prepare_dataframe(df, datetime_columns=None):
    """
    Prepare dataframe for SQL insertion.

    Converts datetime columns (if they exist) and replaces
    pandas NaN values with SQL NULL values.
    """

    if datetime_columns:

        for column in datetime_columns:

            if column in df.columns:

                df[column] = pd.to_datetime(df[column])

    df = df.where(pd.notnull(df), None)

    return df


# ============================================================
# FEATURE COLUMN RENAMING
# ============================================================
FEATURE_COLUMNS = {

    "activeenergyburned": "calories",

    "appleexercisetime": "minutes",

    "basalenergyburned": "calories",

    "distancewalkingrunning": "miles",

    "flightsclimbed": "flights",

    "stepcount": "steps",

    "heartrate": "heartrate",

    "heartratevariabilitysdnn": "hrv",

    "respiratoryrate": "respiratory_rate",

    "walkingheartrateaverage": "heartrate",

    "walkingspeed": "walking_speed",

    "walkingsteplength": "step_length",

    "bodymass": "weight_lb",

    "bodymassindex": "bmi",

    "waistcircumference": "waist_inches"

}


def prepare_feature_dataframe(df, table_name):
    """
    Convert a processed Apple feature dataframe into the
    schema expected by its SQL table.

    Input:
        date
        unit
        value

    Output:
        date
        <feature_column>
    """

    feature_column = FEATURE_COLUMNS[table_name]

    df = (
        df[
            [
                "date",
                "value"
            ]
        ]
        .rename(
            columns={
                "value": feature_column
            }
        )
    )

    return df


# ============================================================
# TABLES
# ============================================================

def truncate_table(connection, table_name):
    """
    Delete all rows from an existing table.
    """

    cursor = connection.cursor()

    cursor.execute(f"TRUNCATE TABLE {table_name}")

    connection.commit()

    cursor.close()

    print(f"Table '{table_name}' truncated.")


def count_rows(connection, table_name):
    """
    Return row count.
    """

    cursor = connection.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")

    count = cursor.fetchone()[0]

    cursor.close()

    print(f"{table_name}: {count} rows")

    return count


def preview_table(connection, table_name, limit=5):
    """
    Display first few imported rows.
    """

    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")

    rows = cursor.fetchall()

    cursor.close()

    print()

    for row in rows:

        print(row)


# ============================================================
# IMPORT
# ============================================================

def insert_dataframe(connection, df, table_name):
    """
    Bulk insert dataframe into an existing SQL table.
    """

    cursor = connection.cursor()

    columns = list(df.columns)

    column_string = ", ".join(columns)

    placeholders = ", ".join(["%s"] * len(columns))

    sql = f"""
    INSERT INTO {table_name}
    ({column_string})
    VALUES ({placeholders})
    """

    values = [tuple(row) for row in df.itertuples(index=False)]

    cursor.executemany(sql, values)

    connection.commit()

    cursor.close()

    print(f"Inserted {len(values)} rows into '{table_name}'.")