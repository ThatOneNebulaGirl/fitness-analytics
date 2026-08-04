-- 👻 this SQL code merges the manually entered waist measurements with apple
create database fitnessData;
use fitnessData;
# make a dedicated waist table first by using the waist values found in TABLE measurements 
DROP TABLE IF EXISTS waist;
CREATE TABLE waist (
    measurement_date DATE NOT NULL PRIMARY KEY,
    waist_inches DECIMAL(5,2) NOT NULL
);
INSERT INTO waist (
    measurement_date,
    waist_inches
)
SELECT
    date,
    waist
FROM measurements
WHERE waist IS NOT NULL
ORDER BY date DESC;

SELECT *
FROM waist;

SELECT COUNT(*)
FROM waist;




-- APPLE DATA 
DROP TABLE IF EXISTS waist_appleData;
CREATE TABLE waist_appleData (
    start_date DATE,
    value DECIMAL(5,2)
);
# Imported waist values from data/processed/apple_daily/waistcircumference_clean.csv
-- Import the cleaned Apple Health waist dataset
-- Source:
--    data/processed/apple_daily/waistcircumference_clean.csv
select * from waist_appleData;
-- checking if this table has and dupes 
SELECT
    start_date,
    COUNT(*) AS occurrences
FROM waist_appleData
GROUP BY start_date
HAVING COUNT(*) > 1;
# the code above showed that there where duplicates so i went ahead and removed it. 
DELETE FROM waist_appleData
WHERE start_date = '2025-02-06'
  AND value = 32.61
LIMIT 1;

DELETE FROM waist_appleData
WHERE start_date = '2024-09-28'
  AND value = 34.33
LIMIT 1;

-- now time to merge, start by making the merg container
INSERT INTO waist (
    measurement_date,
    waist_inches
)
SELECT
    a.start_date,
    a.value
FROM waist_appleData AS a
LEFT JOIN waist AS w
    ON a.start_date = w.measurement_date
WHERE w.measurement_date IS NULL;

-- the merg into waist, the count went from 21 to 28 
SELECT COUNT(*) from waist;
SELECT * from waist;
-- checking for dupes  
SELECT
    measurement_date,
    COUNT(*) AS occurrences
FROM waist
GROUP BY measurement_date
HAVING COUNT(*) > 1;


UPDATE measurements_clean AS m
JOIN waist AS w
    ON m.date = w.measurement_date
SET m.waist = w.waist_inches;

INSERT INTO measurements_clean (
    date,
    waist
)
SELECT
    w.measurement_date,
    w.waist_inches
FROM waist AS w
LEFT JOIN measurements_clean AS m
    ON w.measurement_date = m.date
WHERE m.date IS NULL;

# table is now updated from 26 to 31 measurment counts
select count(*) from measurements_clean;
select * from measurements_clean;


-- ============================================================
-- VALIDATION
-- ============================================================

SELECT COUNT(*) AS total_measurements
FROM measurements_clean;

SELECT *
FROM measurements_clean
ORDER BY date DESC;

SELECT
    date,
    COUNT(*) AS occurrences
FROM measurements_clean
GROUP BY date
HAVING COUNT(*) > 1;


SELECT
    m.date,
    m.waist,
    w.waist_inches
FROM measurements_clean AS m
JOIN waist AS w
    ON m.date = w.measurement_date;