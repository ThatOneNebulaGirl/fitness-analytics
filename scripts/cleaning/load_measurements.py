import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from config.credentials import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("TRUNCATE TABLE measurements") # makes sure that at run time we update the table not keep stacking it up.

df = pd.read_csv(PROJECT_ROOT / "data/raw/measurements.csv")     #  grab raw file
df = df.where(pd.notna(df), None)                                # Convert missing values

# handle my scandal --- sql
sql = """
INSERT INTO measurements (
    date,
    neck,
    shoulder,
    chest,
    waist,
    abdomen,
    hip,
    left_bicep,
    right_bicep,
    left_thigh,
    right_thigh,
    left_calf,
    right_calf,
    underboob,
    left_bicep_flex,
    right_bicep_flex
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


# insert into SQL
for row in df.itertuples(index=False):
    cursor.execute(sql, tuple(row))

conn.commit()

print(f"{cursor.rowcount} rows inserted.")
print("Code has now successfully uploaded the SQL table measurements.\nYay!")

# close the path
cursor.close()
conn.close()