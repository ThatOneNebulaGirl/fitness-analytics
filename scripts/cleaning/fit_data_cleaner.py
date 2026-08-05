import pandas as pd
# _____ SCRIPT 1 _________


#________Loading data
def load_data(csv_path="../../data/raw/fitnessData.csv"):
    return pd.read_csv(csv_path)
df = load_data()

print("done loading")

#________Remove obvious junk columns
drop_cols = [
    "Favorite",
    "Training Stress Score®",
    "Avg Power",
    "Max Power",
    "Total Strokes",
    "Decompression",
    "Number of Laps",
    "Avg Resp",
    "Min Resp",
    "Max Resp",
    "Stress Change",
    "Stress Start",
    "Stress End",
    "Avg Stress",
    "Max Stress",
    "Avg Bike Cadence",
    "Max Bike Cadence",
    "Moving Time",
    "Elapsed Time",
    "Min Elevation",
    "Max Elevation"
]

df_clean = df.drop(columns=drop_cols, errors="ignore")
df_clean = df_clean.replace("--", pd.NA)



#________Convert types
numeric_cols = [
    "Distance",
    "Calories",
    "Avg HR",
    "Max HR",
    "Avg Speed",
    "Max Speed",
    "Total Ascent",
    "Total Descent",
    "Avg Stride Length",
    "Steps",
    "Total Reps",
    "Total Sets",
    "Body Battery Drain"
]

# ============================================================
# BODY BATTERY DRAIN - final cleaning steps
# ============================================================
# Garmin exports Body Battery Drain values like "'-7"
if "Body Battery Drain" in df_clean.columns:
    df_clean["Body Battery Drain"] = (
        df_clean["Body Battery Drain"]
        .astype(str)
        .str.lstrip("'")
    )
for col in numeric_cols:
    if col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")





# ______________ Convert Types
if "Date" in df_clean.columns:
    df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")

for col in ["Total Time", "Best Lap Time"]:
    if col in df_clean.columns:
        df_clean[col] = pd.to_timedelta(df_clean[col], errors="coerce")


#________Identify activity types
print("\nGarmin registered the following activity types:")
print(df_clean["Activity Type"].value_counts())


#________Identify which activities contain meaningful distance values
print("\nInspecting which activities contain meaningful Distance values:")
distance_summary = (
    df_clean
    .groupby("Activity Type")
    .agg(count=("Distance", "count"), mean=("Distance", "mean"))
)
distance_summary = distance_summary[
    (distance_summary["count"] > 0) &
    (distance_summary["mean"] > 0)
]
print(distance_summary.round(2))

distance_activities = distance_summary.index.tolist()
print("\nKeeping Distance for:", distance_activities)

df_clean.loc[
    ~df_clean["Activity Type"].isin(distance_activities),
    "Distance"
] = pd.NA

# ============================================================
# MODEL DATASET
# ============================================================

df_model = df_clean.copy()

df_model = df_model[
    ~(
        (df_model["Activity Type"] == "Running")
        &
        (df_model["Distance"] < 0.25)
    )
]


def format_time_for_display(df):
    display = df.copy()

    timedelta_cols = display.select_dtypes(include="timedelta").columns
    print(display.dtypes)
    for col in timedelta_cols:
        display[col] = display[col].apply(format_timedelta)

    return display


#________Stamps - visual separators for terminal output
def stamp_profile(col):
    print(f"\n{'='*40}")
    print(f"PROFILE: {col}")
    print(f"{'='*40}")

def stamp_IQR(col):
    print(f"\n{'='*40}")
    print(f"IQR ANALYSIS: {col}")
    print(f"{'='*40}")

def stamp_review(col):
    print(f"\n{'='*40}")
    print(f"REVIEW: {col}")
    print(f"{'='*40}")

#________Format timedelta for terminal output -- i want it pretty.
def format_timedelta(td):
    if pd.isna(td):
        return pd.NA

    if not isinstance(td, pd.Timedelta):
        return td

    total_seconds = int(td.total_seconds())

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"

#________First look: sort values + grouped describe
def profile_col(df, col, group_by="Activity Type", title=None):

    if title is None:
        title = col

    stamp_profile(title)

    # Format timedeltas for display only.
    display_df = format_time_for_display(df)

    display_cols = [c for c in [group_by, "Title", col] if c in display_df.columns]

    print("\nBottom 10 Lowest values:")
    print(
        display_df[display_cols]
        .sort_values(col)
        .head(10)
    )

    print("\nTop 10 Highest Values:")
    print(
        display_df[display_cols]
        .sort_values(col, ascending=False)
        .head(10)
    )

    print("\nGrouped describe:")

    describe_df = (
    df[df[col].notna()]
    .groupby(group_by)[col]
    .describe()
    )

    if pd.api.types.is_timedelta64_dtype(df[col]):

        time_cols = ["mean", "std", "min", "25%", "50%", "75%", "max"]

        for c in time_cols:
            describe_df[c] = describe_df[c].apply(format_timedelta)

    print(describe_df)


#________Calculate IQR bounds per group - does NOT modify data
# used as a Investigation Function 
def suggest_iqr_thresholds(
    df,
    col,
    group_by="Activity Type",
    multiplier=2.5
):
    thresholds = {}
    stamp_IQR(col)

    for group_name, group_df in df[df[col].notna()].groupby(group_by):
        q1 = group_df[col].quantile(0.25)
        q3 = group_df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        thresholds[group_name] = {
            "lower": lower,
            "upper": upper
        }

        print(f"\n{group_name}")
        print(f"  Suggested Lower: {lower:.3f}")
        print(f"  Suggested Upper: {upper:.3f}")

    return thresholds


#________Review flagged rows WITHOUT modifying data
def review_col(
    df,
    col,
    low_threshold=None,
    high_threshold=None,
    group_by="Activity Type"
):
    stamp_review(col)

    mask = pd.Series(False, index=df.index)

    if low_threshold is not None:
        mask |= df[col] < low_threshold
    if high_threshold is not None:
        mask |= df[col] > high_threshold

    suspicious = df[mask]
        # Format Total Time for cleaner terminal output
    suspicious = format_time_for_display(suspicious)

    if suspicious.empty:
        print("  No suspicious rows found.")
        return
    
    display_cols = [
        c for c in
        ["Date", group_by, "Title", col, "Distance", "Total Time", "Avg HR", "Steps"]
        if c in suspicious.columns
]
# deduplicate while preserving order
    display_cols = list(dict.fromkeys(display_cols))

    print(suspicious[display_cols].sort_values(col).to_string())


#________Apply IQR thresholds from suggest_iqr_thresholds() to null outliers
def clean_col_by_group(
    df_clean,
    col,
    thresholds,
    clean_lower=True,
    clean_upper=True,
    group_by="Activity Type"
):
    total_nulled = 0

    for group_name, bounds in thresholds.items():
        upper = bounds["upper"]
        lower = bounds["lower"]

        mask = (
            df_clean[group_by] == group_name
        )

        if clean_lower and clean_upper:

            mask &= (
                (df_clean[col] < lower)
                |
                (df_clean[col] > upper)
            )

        elif clean_lower:
            mask &= (
                df_clean[col] < lower
            )

        elif clean_upper:
            mask &= (
                df_clean[col] > upper
            )

        else:
            continue

        nulled = mask.sum()
        total_nulled += nulled

        df_clean.loc[
            mask,
            col
        ] = pd.NA

        print(
            f"{group_name}: nulled {nulled} values "
            f"(outside [{lower:.2f}, {upper:.2f}])"
        )

    print(f"\nTotal nulled: {total_nulled}")
    print("\nAfter cleaning:")
    print(
        df_clean[
            df_clean[col].notna()
        ]
        .groupby(group_by)[col]
        .describe()
    )
    return df_clean


def review_iqr_outliers(
    df,
    col,
    thresholds,
    use_lower=True,
    use_upper=True,
    group_by="Activity Type"
):

    for activity, bounds in thresholds.items():

        low = bounds["lower"] if use_lower else None
        high = bounds["upper"] if use_upper else None

        # print(f"\n{activity}")
        # print("Lower:", low)
        # print("Upper:", high)
        # print("Rows:", len(df[df[group_by] == activity]))
        # print("Max:", df[df[group_by] == activity][col].max())

        review_col(
            df[df[group_by] == activity],
            col,
            low_threshold=low,
            high_threshold=high
        )




# ============================================================
# DISTANCE
# ============================================================
profile_col(df_clean, "Distance")
# Review unusually short movement activities.
review_col(
    df_clean,
    "Distance",
    low_threshold=0.20
)
# ============================================================
# MODEL DATASET - DISTANCE
# ============================================================

df_model = df_clean.copy()

# Remove likely accidental movement activities.
df_model = df_model[
    ~(
        (
            df_model["Activity Type"].isin(
                ["Running", "Walking", "Street Running"]
            )
        )
        &
        (
            (df_model["Distance"] < 0.20)
            |
            (
                (df_model["Activity Type"].isin(["Running", "Street Running"]))
                &
                (df_model["Total Time"] < pd.Timedelta(minutes=10))
            )
        )
    )
]

display = format_time_for_display(df_model)
print(display)
print("Result of cleaning, size of raw distance data: ", len(df_clean), "size of clean distance data: ", len(df_model))
print("process removed: ",len(df_clean)-len(df_model), " files.")
# ============================================================
# REVIEW POSSIBLE DISTANCE CUTOFF
# ============================================================
# Candidate distances to investigate
"""
candidate = df_clean[
    (df_clean["Distance"] >= 0.15) &
    (df_clean["Distance"] <= 0.25)
].sort_values("Distance")

print(candidate[
    ["Date", "Activity Type", "Title", "Distance"]
])

# Find every activity that occurred on those dates.
dates = candidate["Date"].dt.normalize().unique()

review = (
    df_clean[
        df_clean["Date"].dt.normalize().isin(dates)
    ]
    .sort_values(["Date", "Activity Type"])
)

print(
    format_time_for_display(
        review[
            [
                "Date",
                "Activity Type",
                "Title",
                "Distance",
                "Total Time",
                "Calories",
                "Steps"
            ]
        ]
    )
)

""" 

# ============================================================
# STRENGTH TRAINING
# ============================================================
profile_col(
    df_clean[df_clean["Activity Type"] == "Strength Training"],
    "Total Time",
    title="Strength Training"
)

# Review unusually short strength workouts.
short_strength = df_clean[
    (df_clean["Activity Type"] == "Strength Training")
    &
    (df_clean["Total Time"] < pd.Timedelta(minutes=10))
]
display = format_time_for_display(short_strength)
print(
    display[
        ["Date", "Title", "Total Time", "Calories", "Steps"]
    ]
)
# Remove incomplete strength workouts.
removed = len(short_strength)

df_model = df_model.drop(short_strength.index)

print(f"Removed incomplete strength workouts: {removed}")

profile_col(
    df_model[df_model["Activity Type"] == "Strength Training"],
    "Total Time",
    title="Strength Training"
)



# ============================================================
# TOTAL ASCENT
# ============================================================
profile_col(df_clean, "Total Ascent")
ascent_thresholds = suggest_iqr_thresholds(
    df_clean,
    "Total Ascent"
)

review_iqr_outliers(
    df_clean,
    "Total Ascent",
    ascent_thresholds
)
print("ascent_thresholds\n",ascent_thresholds)
 

# ============================================================
# STEPS
# ============================================================
profile_col(df_clean, "Steps")
review_col(
    df_clean,
    "Steps",
    low_threshold=20
)
# Removing strength training <10min, since I know for a fact I workout at 10min minimum
# ============================================================
# MODEL DATASET
# ============================================================
removed = (
    (df_model["Activity Type"] == "Strength Training")
    &
    (df_model["Total Time"] < pd.Timedelta(minutes=10))
).sum()

df_model = df_model[
    ~(
        (df_model["Activity Type"] == "Strength Training")
        &
        (df_model["Total Time"] < pd.Timedelta(minutes=10))
    )
]
print(f"Removed incomplete strength workouts: {removed}")
profile_col(df_model, "Steps")


# ============================================================
# CALORIES
# ============================================================
profile_col(df_clean, "Calories")
review_col(
    df_clean,
    "Calories",
    low_threshold=8,
    high_threshold=770
)

# ============================================================
# MODEL DATASET
# ============================================================
df_model = df_model[
    ~(
        (df_model["Calories"] < 8)
        |
        (df_model["Calories"] > 770)
    )
]
profile_col(df_model, "Calories")


# ============================================================
# AVG HR
# ============================================================
profile_col(df_clean, "Avg HR")
review_col(
    df_clean,
    "Avg HR",
)
# AVG HR data is perfect so no need to remove any rows. 

# ============================================================
# MAX HR
# ============================================================
profile_col(df_clean, "Max HR")

# ============================================================
# BODY BATTERY DRAIN
# ============================================================
profile_col(df_clean, "Body Battery Drain")
review_col(
    df_clean,
    "Body Battery Drain",
    low_threshold=-2,
)        

print("\nBody Battery Drain completeness")
print("-" * 35)

missing = df_clean["Body Battery Drain"].isna().sum()
present = df_clean["Body Battery Drain"].notna().sum()

print(f"Present : {present}")
print(f"Missing : {missing}")
print(f"Percent Missing: {missing / len(df_clean):.2%}")

# ============================================================
# TOTAL DESCENT
# ============================================================
profile_col(df_clean, "Total Descent")
# review_col(
#     df_clean,
#     "Total Descent",
#     # low_threshold=20,
#     high_threshold=600
# )




# ============================================================
# REVIEW LONGEST YOGA DAYS
# ============================================================
""" 
# Five longest yoga sessions.
top_yoga = (
    df_clean[
        df_clean["Activity Type"] == "Yoga"
    ]
    .sort_values("Total Time", ascending=False)
    .head(5)
)

# Extract the dates (ignore the time of day).
dates = top_yoga["Date"].dt.normalize().unique()

# Show every activity that happened on those dates.
review = (
    df_clean[
        df_clean["Date"].dt.normalize().isin(dates)
    ]
    .sort_values(["Date", "Activity Type"])
)

display = format_time_for_display(review)

print(
    display[
        [
            "Date",
            "Activity Type",
            "Title",
            "Distance",
            "Calories",
            "Total Time",
            "Avg HR",
            "Max HR",
            "Steps",
            "Total Sets",
            "Body Battery Drain"
        ]
    ]
)
"""


# ============================================================
# MANUAL ACTIVITY CORRECTIONS
# ============================================================
# Garmin occasionally recorded cooldown cardio sessions as Yoga.
# These activities were manually verified and reclassified.

activity_fixes = {
    "2025-08-16 08:12:52": "Cardio",
    "2024-04-10 18:44:58": "Cardio",
    "2024-06-16 16:06:10": "Cardio",
}

for date, activity in activity_fixes.items():

    df_clean.loc[
        df_clean["Date"] == pd.Timestamp(date),
        "Activity Type"
    ] = activity

    df_model.loc[
        df_model["Date"] == pd.Timestamp(date),
        "Activity Type"
    ] = activity

# ============================================================
# YOGA
# ============================================================
profile_col(
    df_clean[df_clean["Activity Type"] == "Yoga"],
    "Total Time",
    title="Yoga"
)

# Review unusually short yoga sessions.
short_yoga = df_clean[
    (df_clean["Activity Type"] == "Yoga")
    &
    (df_clean["Total Time"] < pd.Timedelta(minutes=10))
]

display = format_time_for_display(short_yoga)

print(
    display[
        ["Date", "Title", "Total Time", "Calories", "Steps"]
    ]
)

# ============================================================
# MODEL DATASET
# ============================================================

# (Only add filtering here if manual review justifies it.)

profile_col(
    df_model[df_model["Activity Type"] == "Yoga"],
    "Total Time",
    title="Yoga"
)

# Keep only the calendar date
df_model["Date"] = (
    pd.to_datetime(df_model["Date"])
    .dt.date
)

# Best Lap Time is not used in the model
df_model = df_model.drop(
    columns=["Best Lap Time"],
    errors="ignore"
)

# Convert workout duration to minutes
df_model["Total Time"] = (
    df_model["Total Time"]
    .dt.total_seconds()
    .div(60)
    .round(2)
)

# Save in chronological order
df_model = (
    df_model
    .sort_values("Date")
    .reset_index(drop=True)
)


# ============================================================
# SAVE CLEANED DATASET
# ============================================================

output_path = "../../data/cleaned/garmin_fitnessData_clean3.csv"
output_path_model = "../../data/cleaned/garmin_fitnessData_model.csv"



df_clean.to_csv(
    output_path,
    index=False
)
df_model.to_csv(
    output_path_model,
    index=False
)



print("\n" + "=" * 40)
print("Complete")
print("=" * 40)