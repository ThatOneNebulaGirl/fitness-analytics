import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.credentials import get_connection

# ---------------------------------------------------------------------
# Connect to MySQL
# ---------------------------------------------------------------------

conn = get_connection()
cursor = conn.cursor()

# Prevent duplicate imports
cursor.execute("TRUNCATE TABLE mynet_measurements")

# ---------------------------------------------------------------------
# Load CSV
# ---------------------------------------------------------------------

df = pd.read_csv(
    PROJECT_ROOT /
    "data/cleaned/myNetDiary/mynet_body_measurements_wide.csv"
)

# Convert dates to SQL format
df["date"] = (
    pd.to_datetime(df["date"])
      .dt.strftime("%Y-%m-%d")
)

# Convert pandas NaN -> SQL NULL
df = df.where(pd.notna(df), None)

# ---------------------------------------------------------------------
# SQL insert statement
# ---------------------------------------------------------------------

sql = """
INSERT INTO mynet_measurements (
    date,
    weight_lb,
    chest,
    waist,
    hip,
    thigh
)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# ---------------------------------------------------------------------
# Insert rows
# ---------------------------------------------------------------------

rows_inserted = 0

for row in df.itertuples(index=False):

    cursor.execute(sql, tuple(row))
    rows_inserted += 1

conn.commit()

# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------

print(f"{rows_inserted} rows inserted.")
print(
    "Code has now successfully uploaded the SQL table "
    "mynet_measurements.\nYay!"
)

# ---------------------------------------------------------------------
# Close connection
# ---------------------------------------------------------------------

cursor.close()
conn.close()