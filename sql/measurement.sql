# this code inspects and prepares my measurement data.
create database fitnessData;
use fitnessData;

-- ============================================================
-- SECTION 1 — CREATE THE RAW MEASUREMENTS TABLE
--
-- Run ONLY this section first.
--
-- After this section completes, execute:
--
--     scripts/cleaning/load_measurements.py
--
-- Then return to this file and continue with Section 2.
-- ============================================================

# create table for data/raw/measurements.csv
# expected row count: 21
# (Import Wizard kept failing on sparse numeric columns,
# so the raw CSV is loaded using load_measurements.py.)



DROP TABLE IF EXISTS measurements;
CREATE TABLE measurements (
    date VARCHAR(10), # this has to be VARCHAR because of raw data date-error.
    neck DOUBLE,
    shoulder DOUBLE,
    chest DOUBLE,
    waist DOUBLE,
    abdomen DOUBLE,
    hip DOUBLE,
    left_bicep DOUBLE,
    right_bicep DOUBLE,
    left_thigh DOUBLE,
    right_thigh DOUBLE,
    left_calf DOUBLE,
    right_calf DOUBLE,
    underboob DOUBLE,
    left_bicep_flex DOUBLE,
    right_bicep_flex DOUBLE
);
select count(*) from measurements; # at this point you should see zero 


-- ============================================================
-- END OF SECTION 1
--
-- NOW RUN:
--
--     scripts/cleaning/load_measurements.py
--
-- This imports the raw CSV into the measurements table.
--
-- After the import completes successfully, continue below.
-- ============================================================






-- ============================================================
-- SECTION 2 — VALIDATE AND STANDARDIZE THE IMPORTED DATA
--
-- Execute this section ONLY AFTER
-- load_measurements.py has successfully imported the data.
-- ============================================================

# verify import
SELECT COUNT(*)
FROM measurements;

# raw dates are stored as MM/DD/YYYY
# create a proper SQL DATE column
ALTER TABLE measurements
ADD COLUMN date_clean DATE;
# convert the dates
UPDATE measurements
SET date_clean = STR_TO_DATE(date, '%m/%d/%Y');
# did it work?!
SELECT
    date,
    date_clean
FROM measurements
LIMIT 10;
# sweet it worcked! so dumping the old date
ALTER TABLE measurements
DROP COLUMN date;
# renaming cuz we like consistency
ALTER TABLE measurements
CHANGE COLUMN date_clean date DATE;


select count(*) from measurements; # should still be 21

# checking for duplicates
SELECT
    date,
    COUNT(*) AS occurrences
FROM measurements
GROUP BY date
HAVING COUNT(*) > 1;



# making a new table that has the cleaned up measurments from this script
DROP TABLE IF EXISTS measurements_clean;

CREATE TABLE measurements_clean AS
SELECT *
FROM measurements
ORDER BY date DESC;

select count(*) from measurements_clean;
select * from measurements_clean;
