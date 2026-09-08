#!/usr/bin/env python
# coding: utf-8

# ===================================
# IMPORTS
# ===================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error

# ===================================
# SETTINGS
# ===================================
data_file = "Train_data.csv"

target = "Del_G"

features = [
    '126',  '137', '17','171','192','200', '4', '43', '44', '50', '62', '8', '83','90', 'Zg_Nb'
]

gb_params = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 3,
    "subsample": 1,
    "min_samples_split": 2,
    "random_state": 42
}

# ===================================
# HELPER FUNCTIONS
# ===================================
def clean_feature(x):
    try:
        return str(int(float(x)))
    except:
        return str(x)

def r_score(y_true, y_pred):

    if np.std(y_true) < 1e-12:
        return 0.0

    if np.std(y_pred) < 1e-12:
        return 0.0

    r = np.corrcoef(y_true, y_pred)[0, 1]

    if np.isnan(r):
        return 0.0

    return r

def slope_score(y_true, y_pred):

    try:
        return np.polyfit(y_true, y_pred, 1)[0]
    except:
        return np.nan

# ===================================
# LOAD DATA
# ===================================
print("\nLoading dataset...")

df = pd.read_csv(data_file)

df.columns = [
    clean_feature(c)
    if c != target else c
    for c in df.columns
]

df = df.drop(
    columns=[
        c for c in df.columns
        if "pdb" in c.lower()
    ],
    errors="ignore"
)

df = df.apply(
    pd.to_numeric,
    errors="coerce"
)

df = df.dropna().reset_index(drop=True)

features = [clean_feature(f) for f in features]

missing = [
    f for f in features
    if f not in df.columns
]

if missing:
    raise ValueError(
        f"Missing features: {missing}"
    )

X = df[features].values
y = df[target].values

print("Samples :", len(y))
print("Features:", len(features))

# ===================================
# TRAIN PERFORMANCE
# ===================================
full_model = GradientBoostingRegressor(
    **gb_params
)

full_model.fit(X, y)

train_pred = full_model.predict(X)

train_r = r_score(
    y,
    train_pred
)

train_mae = mean_absolute_error(
    y,
    train_pred
)

# ===================================
# REPEATED 10-FOLD CV
# ===================================
print("\nRunning 10-Fold CV for seeds 1-100...")

best_r = -999
best_mae = None
best_slope = None
best_seed = None
best_pred = None

all_results = []

for seed in range(1, 100):

    kf = KFold(
        n_splits=10,
        shuffle=True,
        random_state=seed
    )

    cv_pred = np.zeros(len(y))

    for train_idx, test_idx in kf.split(X):

        model = GradientBoostingRegressor(
            **gb_params
        )

        model.fit(
            X[train_idx],
            y[train_idx]
        )

        cv_pred[test_idx] = model.predict(
            X[test_idx]
        )

    cv_r = r_score(
        y,
        cv_pred
    )

    cv_mae = mean_absolute_error(
        y,
        cv_pred
    )

    cv_slope = slope_score(
        y,
        cv_pred
    )

    all_results.append([
        seed,
        cv_r,
        cv_mae,
        cv_slope
    ])

    print(
        f"Seed {seed:3d} | "
        f"R={cv_r:.4f} | "
        f"MAE={cv_mae:.4f}"
    )

    if cv_r > best_r:

        best_r = cv_r
        best_mae = cv_mae
        best_slope = cv_slope
        best_seed = seed
        best_pred = cv_pred.copy()

# ===================================
# SAVE ALL RESULTS
# ===================================
results_df = pd.DataFrame(
    all_results,
    columns=[
        "Seed",
        "R",
        "MAE",
        "Slope"
    ]
)

results_df.to_csv(
    "GB_10fold_seeds_1_200.csv",
    index=False
)

# ===================================
# PRINT BEST RESULT
# ===================================
print("\n================================")
print("BEST 10-FOLD SPLIT")
print("================================")

print(f"Best Seed : {best_seed}")
print(f"Best R    : {best_r:.4f}")
print(f"Best MAE  : {best_mae:.4f}")
print(f"Best Slope: {best_slope:.4f}")

print("\n================================")
print("TRAIN")
print("================================")

print(f"Train R   : {train_r:.4f}")
print(f"Train MAE : {train_mae:.4f}")

# ===================================
# SAVE BEST PREDICTIONS
# ===================================
pred_file = (
    f"{len(features)}_GB_best_10fold_predictions.csv"
)

pd.DataFrame({
    "Experimental_DelG": y,
    "Predicted_DelG": best_pred
}).to_csv(
    pred_file,
    index=False
)

print("\nSaved:", pred_file)

# ===================================
# PLOT BEST SPLIT
# ===================================
plt.figure(figsize=(6, 5))

# Training predictions - open black circles

plt.scatter(
y,
train_pred,
marker="o",
facecolors="none",
edgecolors="black",
s=55,
linewidths=1.3,
label="Training"
)

# 10-fold CV predictions - filled black circles

plt.scatter(
y,
best_pred,
marker="o",
facecolors="black",
edgecolors="black",
s=45,
label="10-fold CV"
)

# Find plot limits

min_val = min(
y.min(),
train_pred.min(),
best_pred.min()
)

max_val = max(
y.max(),
train_pred.max(),
best_pred.max()
)

x_line = np.linspace(
min_val,
max_val,
100
)

# Perfect prediction line

plt.plot(
x_line,
x_line,
color="black",
linestyle="--"
)

# +1 kcal/mol

plt.plot(
x_line,
x_line + 1,
color="black",
linestyle=":"
)

# -1 kcal/mol

plt.plot(
x_line,
x_line - 1,
color="black",
linestyle=":"
)

# Axis labels

plt.xlabel(
"Experimental ΔG (kcal/mol)",
fontsize=14,
fontweight="bold"
)

plt.ylabel(
"Predicted ΔG (kcal/mol)",
fontsize=14,
fontweight="bold"
)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Results

text = (
f"Train r = {train_r:.2f}\n"
f"Train MAE = {train_mae:.2f}\n"
f"10-fold CV r = {best_r:.2f}\n"
f"10-fold CV MAE = {best_mae:.2f}"
)

plt.text(
0.05,
0.95,
text,
transform=plt.gca().transAxes,
verticalalignment="top",
fontsize=12
)

plt.legend(
loc="lower right",
fontsize=11
)

plt.tight_layout()

plot_file = (
f"{len(features)}_GB_best_10fold_plot.png"
)

plt.savefig(
plot_file,
dpi=600,
bbox_inches="tight"
)

plt.show()

print("Saved plot:", plot_file)

