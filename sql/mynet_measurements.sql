USE fitnessData;

-- ============================================================
-- SECTION 1 — IMPORT myNetDiary BODY MEASUREMENTS
--
-- Run ONLY this section first.
--
-- After this section completes, execute:
--
--     scripts/cleaning/load_mynet_measurements.py
--
-- Then return to this file and continue with Section 2.
-- ============================================================

-- Create the SQL table used to store the standardized
-- myNetDiary body measurements.
--
-- Expected row count: 32
--
-- (The MySQL Import Wizard failed because the dataset contains
-- sparse numeric columns. The CSV is therefore loaded using
-- load_mynet_measurements.py, which converts missing values
-- into SQL NULL values before insertion.)

DROP TABLE IF EXISTS mynet_measurements;

CREATE TABLE mynet_measurements (
    date DATE,
    weight_lb DECIMAL(5,2),
    chest DECIMAL(5,2),
    waist DECIMAL(5,2),
    hip DECIMAL(5,2),
    thigh DECIMAL(5,2)
);

-- This import is performed by:
-- scripts/cleaning/load_mynet_measurements.py

SELECT COUNT(*)
FROM mynet_measurements;


-- ============================================================
-- END OF SECTION 1
--
-- NOW RUN:
--
--     scripts/cleaning/load_mynet_measurements.py
--
-- After the import completes successfully,
-- continue with Section 2.
-- ============================================================



-- ============================================================
-- SECTION 2 — INSPECT OVERLAPPING DATES
-- ============================================================

SELECT
    mc.date,

    mc.chest  AS manual_chest,
    m.chest   AS mynet_chest,

    mc.waist  AS manual_waist,
    m.waist   AS mynet_waist,

    mc.hip    AS manual_hip,
    m.hip     AS mynet_hip

FROM measurements_clean AS mc
JOIN mynet_measurements AS m
    ON mc.date = m.date
ORDER BY mc.date;



-- ============================================================
-- SECTION 3 — MERGE UNIQUE BODY MEASUREMENTS
-- ============================================================

INSERT INTO measurements_clean (
    date,
    chest,
    waist,
    hip
)
SELECT
    m.date,
    m.chest,
    m.waist,
    m.hip
FROM mynet_measurements AS m
LEFT JOIN measurements_clean AS mc
    ON m.date = mc.date
WHERE
    mc.date IS NULL
    AND (
        m.chest IS NOT NULL
        OR m.waist IS NOT NULL
        OR m.hip IS NOT NULL
    );



-- ============================================================
-- SECTION 4 — VALIDATION
-- ============================================================

-- Expected row count: 25
SELECT COUNT(*)
FROM measurements_clean;


-- Check for duplicate dates
SELECT
    date,
    COUNT(*) AS occurrences
FROM measurements_clean
GROUP BY date
HAVING COUNT(*) > 1
ORDER BY date;


-- Verify no empty body-measurement rows were inserted
SELECT *
FROM measurements_clean
WHERE
    chest IS NULL
    AND waist IS NULL
    AND hip IS NULL;


-- Review final table
SELECT *
FROM measurements_clean
ORDER BY date DESC;