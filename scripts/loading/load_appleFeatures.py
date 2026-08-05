"""
============================================================
LOAD ALL APPLE HEALTH FEATURES
============================================================

Purpose:
    Load every processed Apple Health feature dataset into
    its corresponding MySQL table.

Prerequisites:
    1. Run tables_for_features.sql
    2. Ensure all feature tables exist.
============================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from config.credentials import get_connection

from src.tools_for_loading_SQL import (
    close_connection,
    load_csv,
    prepare_dataframe,
    prepare_feature_dataframe,
    truncate_table,
    insert_dataframe,
    count_rows,
    preview_table
)

# ============================================================
# CONNECT TO DATABASE
# ============================================================

connection = get_connection()

# ============================================================
# FIND ALL APPLE DAILY FEATURE FILES
# ============================================================

APPLE_FOLDER = PROJECT_ROOT / "data" / "processed" / "apple_daily"

csv_files = sorted(
    APPLE_FOLDER.glob("*_clean.csv")
)

# ============================================================
# LOAD EACH FEATURE
# ============================================================

for csv_file in csv_files:

    table_name = csv_file.stem.replace("_clean", "")

    print()
    print("=" * 70)
    print(f"Loading: {table_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD CSV
    # --------------------------------------------------------

    df = load_csv(csv_file)

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    df = prepare_dataframe(
        df,
        datetime_columns=["date"]
    )

    df = prepare_feature_dataframe(
        df,
        table_name
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print()
    print(df.head())
    print()
    print(df.columns)

    # --------------------------------------------------------
    # IMPORT INTO SQL
    # --------------------------------------------------------

    truncate_table(
        connection,
        table_name
    )

    insert_dataframe(
        connection,
        df,
        table_name
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    count_rows(
        connection,
        table_name
    )

    preview_table(
        connection,
        table_name
    )

# ============================================================
# CLOSE CONNECTION
# ============================================================

close_connection(connection)