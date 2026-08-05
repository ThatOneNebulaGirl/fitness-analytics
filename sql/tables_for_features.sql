USE fitnessData;

-- ============================================================
-- ACTIVE ENERGY BURNED
-- ============================================================

DROP TABLE IF EXISTS activeenergyburned;

CREATE TABLE activeenergyburned (
    date DATE NOT NULL PRIMARY KEY,
    calories DOUBLE NOT NULL
);

-- ============================================================
-- APPLE EXERCISE TIME
-- ============================================================

DROP TABLE IF EXISTS appleexercisetime;

CREATE TABLE appleexercisetime (
    date DATE NOT NULL PRIMARY KEY,
    minutes DOUBLE NOT NULL
);

-- ============================================================
-- BASAL ENERGY BURNED
-- ============================================================

DROP TABLE IF EXISTS basalenergyburned;

CREATE TABLE basalenergyburned (
    date DATE NOT NULL PRIMARY KEY,
    calories DOUBLE NOT NULL
);

-- ============================================================
-- DISTANCE WALKING RUNNING
-- ============================================================

DROP TABLE IF EXISTS distancewalkingrunning;

CREATE TABLE distancewalkingrunning (
    date DATE NOT NULL PRIMARY KEY,
    miles DOUBLE NOT NULL
);

-- ============================================================
-- FLIGHTS CLIMBED
-- ============================================================

DROP TABLE IF EXISTS flightsclimbed;

CREATE TABLE flightsclimbed (
    date DATE NOT NULL PRIMARY KEY,
    flights DOUBLE NOT NULL
);

-- ============================================================
-- STEP COUNT
-- ============================================================

DROP TABLE IF EXISTS stepcount;

CREATE TABLE stepcount (
    date DATE NOT NULL PRIMARY KEY,
    steps DOUBLE NOT NULL
);

-- ============================================================
-- HEART RATE
-- ============================================================

DROP TABLE IF EXISTS heartrate;

CREATE TABLE heartrate (
    date DATE NOT NULL PRIMARY KEY,
    heartrate DOUBLE NOT NULL
);

-- ============================================================
-- HEART RATE VARIABILITY
-- ============================================================

DROP TABLE IF EXISTS heartratevariabilitysdnn;

CREATE TABLE heartratevariabilitysdnn (
    date DATE NOT NULL PRIMARY KEY,
    hrv DOUBLE NOT NULL
);

-- ============================================================
-- RESPIRATORY RATE
-- ============================================================

DROP TABLE IF EXISTS respiratoryrate;

CREATE TABLE respiratoryrate (
    date DATE NOT NULL PRIMARY KEY,
    respiratory_rate DOUBLE NOT NULL
);

-- ============================================================
-- WALKING HEART RATE AVERAGE
-- ============================================================

DROP TABLE IF EXISTS walkingheartrateaverage;

CREATE TABLE walkingheartrateaverage (
    date DATE NOT NULL PRIMARY KEY,
    heartrate DOUBLE NOT NULL
);

-- ============================================================
-- BODY MASS
-- ============================================================

DROP TABLE IF EXISTS bodymass;

CREATE TABLE bodymass (
    date DATE NOT NULL PRIMARY KEY,
    weight_lb DOUBLE NOT NULL
);

-- ============================================================
-- BODY MASS INDEX
-- ============================================================

DROP TABLE IF EXISTS bodymassindex;

CREATE TABLE bodymassindex (
    date DATE NOT NULL PRIMARY KEY,
    bmi DOUBLE NOT NULL
);

-- ============================================================
-- WAIST CIRCUMFERENCE
-- ============================================================

DROP TABLE IF EXISTS waistcircumference;

CREATE TABLE waistcircumference (
    date DATE NOT NULL PRIMARY KEY,
    waist_inches DOUBLE NOT NULL
);

-- ============================================================
-- VALIDATION
-- ============================================================

SHOW TABLES;



-- ============================================================
-- WALKING HEART RATE AVERAGE
-- ============================================================

DROP TABLE IF EXISTS walkingheartrateaverage;

CREATE TABLE walkingheartrateaverage (
    date DATE NOT NULL PRIMARY KEY,
    heartrate DOUBLE NOT NULL
);

-- ============================================================
-- WALKING SPEED
-- ============================================================

DROP TABLE IF EXISTS walkingspeed;

CREATE TABLE walkingspeed (
    date DATE NOT NULL PRIMARY KEY,
    walking_speed DOUBLE NOT NULL
);

-- ============================================================
-- WALKING STEP LENGTH
-- ============================================================

DROP TABLE IF EXISTS walkingsteplength;

CREATE TABLE walkingsteplength (
    date DATE NOT NULL PRIMARY KEY,
    step_length DOUBLE NOT NULL
);