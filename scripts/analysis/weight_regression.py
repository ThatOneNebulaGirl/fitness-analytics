"""
============================================================
WEIGHT REGRESSION
============================================================

Purpose
-------
Fit an ordinary least squares (OLS) regression model to
predict body weight from engineered Apple Health and
Garmin features.

Outputs

    figures/weight_actual_vs_predicted.png

Author:
    Melody Sanchez

Project:
    Longitudinal Fitness Analytics
============================================================
"""

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
# needed libary for STAT modeling!! 
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression




# ============================================================
# PROJECT ROOT
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# FUNCTION I MADE -TOOLS_FOR_CLEANING import 
# ============================================================
from src.tools_for_cleaning import load_csv

# ============================================================
# PATHS for LOADING
# ============================================================

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weight_master_features.csv"
)

FIGURE_DIR = (
    PROJECT_ROOT
    / "figures"
)


# ============================================================
# LOAD DATA
# ============================================================
df = load_csv(DATA_FILE)

# ============================================================
# TIER 1 FEATURES
# ============================================================
TIER1_FEATURES = {

    "distance_7day_sum":
        "Distance",

    "stepcount_7day_sum":
        "Apple Step Count",

    "flightsclimbed_7day_sum":
        "Flights Climbed",

    "walkingspeed_7day_mean":
        "Walking Speed",

    "walkingsteplength_7day_mean":
        "Walking Step Length",

    "activeenergyburned_7day_sum":
        "Active Energy Burned",

    "basalenergyburned_7day_sum":
        "Basal Energy Burned",

    "heartrate_7day_mean":
        "Heart Rate"

}

# ============================================================
# TIER 2 FEATURES
# ============================================================
TIER2_FEATURES = {

    "appleexercisetime_7day_sum":
        "Exercise Time",

    "heartratevariabilitysdnn_7day_mean":
        "Heart Rate Variability",

    "walkingheartrateaverage_7day_mean":
        "Walking Heart Rate"

}

TARGET = "weight_lb"

# ============================================================
# REGRESSION FUNCTION
# ============================================================

def run_regression(
    FEATURES,
    tier
):
  # ============================================================
  # STORE RESULTS
  # ============================================================

  results = []

  FIGURE_DIR = (
      PROJECT_ROOT
      / "figures"
      / "weight_regression"
      / tier
  )

  FIGURE_DIR.mkdir(
      parents=True,
      exist_ok=True
  )

  DIAGNOSTIC_DIR = (
      FIGURE_DIR
      / "diagnostics"
  )

  DIAGNOSTIC_DIR.mkdir(
      parents=True,
      exist_ok=True
  )
    
  for feature, label in FEATURES.items():
      OUTPUT_FIGURE = (
      FIGURE_DIR
      / f"{feature}_regression.png"
  )

      # -------------------------------
      # Keep complete cases
      # -------------------------------

      model_df = df[
          [TARGET, feature]
      ].dropna()

      print()
      print("=" * 70)
      print(label)
      print("=" * 70)

      print(
          f"Rows used : {len(model_df)}"
      )

      # -------------------------------
      # Predictor / Target
      # -------------------------------

      X = model_df[[feature]]

      y = model_df[TARGET]

      # -------------------------------
      # Fit model
      # -------------------------------

      model = LinearRegression()

      model.fit(
          X,
          y
      )

      predictions = model.predict(X)
      
      # ============================================================
      # RESIDUALS
      # ============================================================

      residuals = y - predictions
      # -------------------------------
      # Metrics
      # -------------------------------
      r = X[feature].corr(y)
      r2 = r2_score(
          y,
          predictions
      )
      mae = mean_absolute_error(
          y,
          predictions
      )
      rmse = (
          mean_squared_error(
              y,
              predictions
          ) ** 0.5
      )
      # -------------------------------
      # Statistical Inference
      # -------------------------------

      X_stats = sm.add_constant(X)

      ols_model = sm.OLS(
          y,
          X_stats
      ).fit()

      p_value = ols_model.pvalues.iloc[1]

      t_value = ols_model.tvalues.iloc[1]

      std_error = ols_model.bse.iloc[1]

      conf_low = ols_model.conf_int().iloc[1, 0]

      conf_high = ols_model.conf_int().iloc[1, 1]

      adj_r2 = ols_model.rsquared_adj

      f_stat = ols_model.fvalue


      # -------------------------------
      # Print Results
      # -------------------------------

      print()
      print(
          f"Slope      : {model.coef_[0]:.6f}"
      )
      print(
          f"Intercept  : {model.intercept_:.3f}"
      )
      print()
      print(
          "Equation:"
      )
      print(
          f"Weight = "
          f"{model.intercept_:.3f}"
          f" + "
          f"({model.coef_[0]:.6f}) × {feature}"
      )
      print()
      print(
          f"r    : {r:.3f}"
      )
      print(
          f"R²   : {r2:.3f}"
      )
      print(
          f"MAE  : {mae:.3f} lb"
      )
      print(
          f"RMSE : {rmse:.3f} lb"
      )
      print()
      print(
          f"Adj R²        : {adj_r2:.3f}"
      )
      print(
          f"F Statistic   : {f_stat:.3f}"
      )
      print(
          f"t Statistic   : {t_value:.3f}"
      )
      print(
          f"Std Error     : {std_error:.6f}"
      )
      print(
          f"p-value       : {p_value:.6f}"
      )
      print(
          f"95% CI        : [{conf_low:.6f}, {conf_high:.6f}]"
      )

      # -------------------------------
      # Save Results
      # -------------------------------

      results.append({

      "Feature": label,

      "Rows": len(model_df),

      "Slope": model.coef_[0],

      "Intercept": model.intercept_,

      "r": r,

      "R2": r2,

      "Adj_R2": adj_r2,

      "MAE": mae,

      "RMSE": rmse,

      "F": f_stat,

      "t": t_value,

      "Std_Error": std_error,

      "p_value": p_value,

      "CI_Low": conf_low,

      "CI_High": conf_high

  })
      

      # ============================================================
      # PLOT
      # ============================================================

      plt.figure(figsize=(8, 7))

      # ------------------------------------------------------------
      # Scatter
      # ------------------------------------------------------------

      plt.scatter(
          X[feature],
          y,
          s=90,
          color="#F78FB3",
          edgecolors="white",
          linewidth=0.8,
          alpha=0.75,
          zorder=3
      )

      # ------------------------------------------------------------
      # Regression Line
      # ------------------------------------------------------------

      plt.plot(
          X[feature],
          predictions,
          color="#63C7B2",
          linewidth=3,
          zorder=2
      )

      # ------------------------------------------------------------
      # Labels
      # ------------------------------------------------------------

      plt.xlabel(
          label,
          fontsize=18
      )

      plt.ylabel(
          "Body Weight (lb)",
          fontsize=18
      )

      plt.title(
          f"Weight vs. {label}",
          fontsize=28,
          color="#F06CA8",
          fontweight="bold",
          pad=20
      )

      # ------------------------------------------------------------
      # Make plot breathe
      # ------------------------------------------------------------

      plt.margins(
          x=0.06,
          y=0.08
      )


      # ------------------------------------------------------------
      # Pretty Axis Styling
      # ------------------------------------------------------------

      ax = plt.gca()

      for spine in ax.spines.values():
          spine.set_color("#666666")
          spine.set_linewidth(1.4)

      ax.tick_params(
          axis="both",
          labelsize=13,
          colors="#555555",
          length=4,
          width=1.2
      )

      # Light background

      ax.set_facecolor("#FFFDFC")

      # Soft grid

      ax.grid(
          alpha=0.15,
          linestyle="--"
      )

      # ------------------------------------------------------------
      # Statistics Box
      # ------------------------------------------------------------

      if model.coef_[0] < 0:
          textbox_location = (0.98, 0.98)
          alignment = "right"
      else:
          textbox_location = (0.02, 0.98)
          alignment = "left"

      stats = (
          f"$n$ = {len(model_df)}\n"
          f"$r$ = {r:.3f}\n"
          f"$R^2$ = {r2:.3f}\n"
          f"MAE = {mae:.2f} lb"
      )

      ax.text(
          textbox_location[0],
          textbox_location[1],
          stats,
          transform=ax.transAxes,
          ha=alignment,
          va="top",
          fontsize=13,
          color="#444444",
          bbox=dict(
              boxstyle="round,pad=0.55",
              facecolor="#FFF8FC",
              edgecolor="#F06CA8",
              linewidth=2,
              alpha=0.95
          ),
          zorder=10
      )

      plt.tight_layout()

      plt.savefig(
          OUTPUT_FIGURE,
          dpi=300,
          bbox_inches="tight"
      )
      print(f"Saved regression plot: {OUTPUT_FIGURE}")

      plt.close()


      # ============================================================
      # RESIDUALS VS FITTED
      # ============================================================

      plt.figure(figsize=(8,7))

      plt.scatter(
          predictions,
          residuals,
          s=90,
          color="#F78FB3",
          edgecolors="white",
          linewidth=0.8,
          alpha=0.80
      )

      plt.axhline(
          0,
          color="#63C7B2",
          linewidth=2
      )

      plt.xlabel(
          "Predicted Weight (lb)",
          fontsize=18
      )

      plt.ylabel(
          "Residual (lb)",
          fontsize=18
      )

      plt.title(
          f"Residuals vs. Fitted\n{label}",
          fontsize=24,
          color="#F06CA8",
          fontweight="bold"
      )

      plt.grid(False)

      ax = plt.gca()

      for spine in ax.spines.values():
          spine.set_color("#555555")

      plt.tight_layout()

      plt.savefig(
          DIAGNOSTIC_DIR /
          f"{feature}_residuals.png",
          dpi=300,
          bbox_inches="tight"
      )

      plt.close()


      # ============================================================
      # HISTOGRAM OF RESIDUALS
      # ============================================================

      plt.figure(figsize=(8, 7))

      plt.hist(
          residuals,
          bins=10,
          color="#F78FB3",
          edgecolor="white",
          linewidth=1.2,
          alpha=0.85
      )

      plt.xlabel(
          "Residual (lb)",
          fontsize=18
      )

      plt.ylabel(
          "Frequency",
          fontsize=18
      )

      plt.title(
          f"Residual Distribution\n{label}",
          fontsize=24,
          color="#F06CA8",
          fontweight="bold",
          pad=18
      )

      ax = plt.gca()

      # Soft axes
      for spine in ax.spines.values():
          spine.set_color("#666666")
          spine.set_linewidth(1.3)

      ax.tick_params(
          labelsize=13,
          colors="#555555"
      )

      ax.set_facecolor("#FFFDFC")

      ax.grid(
          alpha=0.15,
          linestyle="--"
      )

      plt.tight_layout()

      plt.savefig(
          DIAGNOSTIC_DIR /
          f"{feature}_histogram.png",
          dpi=300,
          bbox_inches="tight"
      )

      plt.close()

      # ============================================================
      # NORMAL Q-Q PLOT
      # ============================================================

      fig = sm.qqplot(
          residuals,
          line="45",
          fit=True
      )

      ax = fig.axes[0]

      # ----------------------------------------
      # Style the points
      # ----------------------------------------

      points = ax.get_lines()[0]

      points.set_marker("o")
      points.set_markersize(8)
      points.set_markerfacecolor("#F78FB3")
      points.set_markeredgecolor("white")
      points.set_markeredgewidth(0.8)
      points.set_linestyle("")

      # ----------------------------------------
      # Style the reference line
      # ----------------------------------------

      line = ax.get_lines()[1]

      line.set_color("#63C7B2")
      line.set_linewidth(3)

      # ----------------------------------------
      # Labels
      # ----------------------------------------

      ax.set_title(
          f"Normal Q-Q Plot\n{label}",
          fontsize=24,
          color="#F06CA8",
          fontweight="bold",
          pad=18
      )

      ax.set_xlabel(
          "Theoretical Quantiles",
          fontsize=18
      )

      ax.set_ylabel(
          "Sample Quantiles",
          fontsize=18
      )

      # ----------------------------------------
      # Pretty styling
      # ----------------------------------------

      ax.set_facecolor("#FFFDFC")

      for spine in ax.spines.values():
          spine.set_color("#666666")
          spine.set_linewidth(1.3)

      ax.tick_params(
          labelsize=13,
          colors="#555555"
      )

      ax.grid(
          alpha=0.15,
          linestyle="--"
      )

      plt.tight_layout()

      plt.savefig(
          DIAGNOSTIC_DIR /
          f"{feature}_qqplot.png",
          dpi=300,
          bbox_inches="tight"
      )

      plt.close()


      # # ============================================================
      # # OUTPUT FIGURE
      # # ===========================================================
      # OUTPUT_FIGURE = (
      #     FIGURE_DIR
      #     / f"{feature}_regression.png"
      # )

      plt.close()


  # ============================================================
  # BUILD SUMMARY TABLE
  # ============================================================

  results_df = pd.DataFrame(results)
  if results_df.empty:
    print()
    print("=" * 70)
    print(f"No features found for {tier}. Skipping.")
    print("=" * 70)
    return results_df

  results_df = results_df.sort_values(
      by="R2",
      ascending=False
  )

  results_df = results_df.round({

      "Slope": 6,
      "Intercept": 3,
      "r": 3,
      "R2": 3,
      "Adj_R2": 3,
      "MAE": 3,
      "RMSE": 3,
      "F": 3,
      "t": 3,
      "Std_Error": 6,
      "p_value": 6,
      "CI_Low": 6,
      "CI_High": 6

  })

  # ============================================================
  # SAVE SUMMARY
  # ============================================================

  OUTPUT_SUMMARY = (
      PROJECT_ROOT
      / "data"
      / "processed"
      / f"{tier}_regression_summary.csv"
  )

  results_df.to_csv(
      OUTPUT_SUMMARY,
      index=False
  )

  print()
  print("=" * 70)
  print("Regression Summary")
  print("=" * 70)
  print(results_df)

  print()
  print("=" * 70)
  print("Saved")
  print("=" * 70)
  print(OUTPUT_SUMMARY)
  return results_df


  


# ============================================================
# RUN TIER 1
# ============================================================
tier1_results = run_regression(
    TIER1_FEATURES,
    "tier1"
)

# ============================================================
# RUN TIER 2
# ============================================================

tier2_results = run_regression(
    TIER2_FEATURES,
    "tier2"
)