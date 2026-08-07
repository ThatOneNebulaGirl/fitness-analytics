import pandas as pd
import matplotlib.pyplot as plt

import sys
from pathlib import Path
import seaborn as sns


import numpy as np
from scipy import stats

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

sys.path.append(
    str(PROJECT_ROOT / "src")
)

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

import statsmodels.api as sm

from statsmodels.stats.outliers_influence import (
    variance_inflation_factor
)

from tools_for_cleaning import (
    load_csv
)

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weight_master_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "figures"
    / "multiple_regression"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)
# --------------------------------------------------
# Plot Colors
# --------------------------------------------------

POINT_COLOR = "#F48FB1"      # pink
LINE_COLOR = "#58C4B6"       # teal
BORDER_COLOR = "#F48FB1"
TEXT_COLOR = "#222222"

df = load_csv(INPUT_FILE)



print(df.columns.tolist())

TARGET = "weight_lb"

FEATURES = [

    "distance_7day_sum",
    "walkingsteplength_7day_mean"

]


model_df = df[
    [TARGET] + FEATURES
].dropna()

# --------------------------------------------------
# Predictor Correlation Matrix
# --------------------------------------------------

corr_features = [
    "distance_7day_sum",
    "stepcount_7day_sum",
    "walkingsteplength_7day_mean"
]

corr_df = (
    df[corr_features]
    .dropna()
    .rename(columns={
        "distance_7day_sum": "Distance",
        "stepcount_7day_sum": "Apple Steps",
        "walkingsteplength_7day_mean": "Walking Step Length"
    })
)

corr = corr_df.corr(method="pearson")

plt.figure(figsize=(6,5))

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    annot_kws={"fontsize":12},
    cmap=sns.diverging_palette(
        340,
        145,
        as_cmap=True
    ),
    vmin=-1,
    vmax=1,
    square=True,
    linewidths=1.5,
    linecolor="white",
    cbar_kws={
        "label":"Pearson r",
        "shrink":0.85
    }
)

plt.xticks(
    rotation=20,
    ha="right",
    fontsize=12
)

plt.yticks(
    rotation=0,
    fontsize=12
)

plt.title(
    "Candidate Predictor Correlation Matrix",
    fontsize=15,
    weight="bold",
    color=BORDER_COLOR,
    pad=20
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "multiple_regression_predictor_correlation.png",
    dpi=300
)

plt.close()



print(
    f"Rows used: {len(model_df)}"
)

X = model_df[
    FEATURES
]

y = model_df[
    TARGET
]

model = LinearRegression()

model.fit(
    X,
    y
)

predictions = model.predict(
    X
)

# --------------------------------------------------
# Statistical Inference
# --------------------------------------------------

X_stats = sm.add_constant(X)
print()
print("=" * 70)
print("Variance Inflation Factors")
print("=" * 70)

vif = pd.DataFrame()

vif["Feature"] = X.columns

vif["VIF"] = [

    variance_inflation_factor(
        X.values,
        i
    )

    for i in range(
        X.shape[1]
    )

]

print(vif)




ols_model = sm.OLS(
    y,
    X_stats
).fit()

print(ols_model.summary())



model.coef_[0]
print()

print(
    "=" * 70
)

print(
    "Model 1"
)

print(
    "=" * 70
)

for feature, coef in zip(
    FEATURES,
    model.coef_
):

    print(
        f"{feature:<30}"
        f"{coef:10.6f}"
    )

print()

print(
    f"Intercept: "
    f"{model.intercept_:.3f}"
)


# --------------------------------------------------
# Residual Diagnostics
# --------------------------------------------------


residuals = y - predictions
plt.figure(figsize=(8,6))

plt.scatter(
    predictions,
    residuals,
    s=180,
    color=POINT_COLOR,
    edgecolor="white",
    linewidth=1.5,
    alpha=0.95
)

plt.axhline(
    0,
    color=LINE_COLOR,
    linewidth=4
)

plt.xlabel(
    "Predicted Weight (lb)",
    fontsize=16
)

plt.ylabel(
    "Residual (lb)",
    fontsize=16
)

plt.title(
    "Residuals vs. Fitted",
    fontsize=28,
    weight="bold",
    color=BORDER_COLOR,
    pad=20
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "multiple_regression_residuals.png",
    dpi=300
)

plt.close()

plt.figure(figsize=(8, 6))

stats.probplot(residuals, dist="norm", plot=plt)

ax = plt.gca()

ax.get_lines()[0].set_markerfacecolor(POINT_COLOR)
ax.get_lines()[0].set_markeredgecolor("white")
ax.get_lines()[0].set_markersize(10)

ax.get_lines()[1].set_color(LINE_COLOR)
ax.get_lines()[1].set_linewidth(4)

plt.title(
    "Normal Q-Q Plot",
    fontsize=28,
    weight="bold",
    color=BORDER_COLOR,
    pad=20
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "multiple_regression_qqplot.png",
    dpi=300
)

plt.close()

plt.figure(figsize=(7,7))

plt.scatter(
    y,
    predictions,
    s=180,
    color=POINT_COLOR,
    edgecolor="white",
    linewidth=1.5,
    alpha=0.95
)

mn = min(y.min(), predictions.min())
mx = max(y.max(), predictions.max())

plt.plot(
    [mn, mx],
    [mn, mx],
    "--",
    color=LINE_COLOR,
    linewidth=4
)

plt.xlabel("Actual Weight (lb)", fontsize=16)
plt.ylabel("Predicted Weight (lb)", fontsize=16)

plt.title(
    "Actual vs. Predicted Weight",
    fontsize=28,
    weight="bold",
    color=BORDER_COLOR,
    pad=20
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "multiple_regression_actual_vs_predicted.png",
    dpi=300
)

plt.close()


mae = mean_absolute_error(y, predictions)

rmse = np.sqrt(
    mean_squared_error(y, predictions)
)

print(f"MAE : {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

print("\nModel Performance")
print("-----------------------")
print(f"MAE      : {mae:.3f}")
print(f"RMSE     : {rmse:.3f}")
# print(f"R²       : {r2:.3f}")
# print(f"Adj. R²  : {adj_r2:.3f}")
