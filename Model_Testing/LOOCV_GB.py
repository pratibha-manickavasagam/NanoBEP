#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_absolute_error


# Input file
data_file = "Train_data.csv"
target = "Del_G"

# Features used in the model
features = [
    '126',  '137', '17','171','192','200', '4', '43', '44', '50', '62', '8', '83','90', 'Zg_Nb'
]

# Features to log transform
log_features = []

# Gradient Boosting parameters
gb_params = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 3,
    "subsample": 1,
    "min_samples_split": 2,
    "random_state": 42
}


# Convert column names such as 4.0 to 4
def clean_feature(x):
    try:
        return str(int(float(x)))
    except:
        return str(x)


# Calculate correlation
def correlation(y_true, y_pred):
    r = np.corrcoef(y_true, y_pred)[0, 1]

    if np.isnan(r):
        return 0

    return r


# Read data
df = pd.read_csv(data_file)

df.columns = [
    clean_feature(c) if c != target else c
    for c in df.columns
]

# Remove PDB columns
df = df.drop(
    columns=[c for c in df.columns if "pdb" in c.lower()],
    errors="ignore"
)

# Convert data to numeric and remove missing values
df = df.apply(pd.to_numeric, errors="coerce")
df = df.dropna().reset_index(drop=True)

# Clean feature names
features = [clean_feature(f) for f in features]
log_features = [clean_feature(f) for f in log_features]

# Check that all features are present
missing = [f for f in features if f not in df.columns]

if missing:
    print("Missing features:", missing)
    raise SystemExit


# Prepare X and y
X = df[features].copy()
y = df[target].values


# Apply log transformation if required
for f in log_features:
    X[f] = X[f].apply(
        lambda x: np.sign(x) * np.log1p(abs(x))
    )

X = X.values


print("\nFeatures used:", features)



# ==============================
# JACK-KNIFE / LOOCV
# ==============================

loo = LeaveOneOut()
cv_pred = np.zeros(len(y))



for i, (train_index, test_index) in enumerate(
    loo.split(X), start=1
):

    model = GradientBoostingRegressor(**gb_params)

    model.fit(
        X[train_index],
        y[train_index]
    )

    cv_pred[test_index] = model.predict(
        X[test_index]
    )

# Jack-knife results
cv_r = correlation(y, cv_pred)
cv_mae = mean_absolute_error(y, cv_pred)


# ==============================
# FINAL MODEL
# ==============================

model = GradientBoostingRegressor(**gb_params)

model.fit(X, y)

# Training predictions
train_pred = model.predict(X)

train_r = correlation(y, train_pred)
train_mae = mean_absolute_error(y, train_pred)


# ==============================
# PRINT RESULTS
# ==============================

print("\n==============================")
print("RESULTS")
print("==============================")

print("\nTRAIN")
print(f"R   : {train_r:.4f}")
print(f"MAE : {train_mae:.4f}")

print("\nJACK-KNIFE")
print(f"R   : {cv_r:.4f}")
print(f"MAE : {cv_mae:.4f}")


# ==============================
# SAVE PREDICTIONS
# ==============================

n_features = len(features)

prediction_file = (
    f"{n_features}_GB_LOOCV_predictions.csv"
)

pd.DataFrame({
    "Experimental": y,
    "Training_Fitted": train_pred,
    "Jackknife": cv_pred
}).to_csv(
    prediction_file,
    index=False
)

print("\nSaved:", prediction_file)


# ==============================
# PLOT
# ==============================

plt.figure(figsize=(7, 6))

# Training: open circles
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

# Jack-knife: filled circles
plt.scatter(
    y,
    cv_pred,
    marker="o",
    facecolors="black",
    edgecolors="black",
    s=45,
    label="Jack-knife"
)


# Same axis range for both datasets
all_values = np.concatenate([y,train_pred,cv_pred])

min_val = all_values.min()
max_val = all_values.max()

margin = (max_val - min_val) * 0.05

plot_min = min_val - margin
plot_max = max_val + margin

x = np.linspace(plot_min,plot_max,200)


# Perfect prediction line
plt.plot(x,x,color="black",linewidth=1.5)

# ±1 kcal/mol lines
plt.plot(
    x,
    x + 1,
    color="black",
    linestyle=":",
    linewidth=1
)

plt.plot(x,x - 1,color="black",linestyle=":",linewidth=1)


# Axis limits
plt.xlim(plot_min, plot_max)
plt.ylim(plot_min, plot_max)


# Labels
plt.xlabel(
    "Experimental ΔG (kcal/mol)",
    fontsize=15,
    fontweight="bold"
)

plt.ylabel(
    "Predicted ΔG (kcal/mol)",
    fontsize=15,
    fontweight="bold"
)

plt.xticks(fontsize=13)
plt.yticks(fontsize=13)


# Results on the plot
text = (
    f"Train r = {train_r:.2f}\n"
    f"Train MAE = {train_mae:.2f}\n"
    f"Jack-knife r = {cv_r:.2f}\n"
    f"Jack-knife MAE = {cv_mae:.2f}"
)

plt.text(
    0.05,
    0.95,
    text,
    transform=plt.gca().transAxes,
    verticalalignment="top",
    fontsize=13
)


plt.legend(
    loc="lower right",
    fontsize=11
)

plt.tight_layout()


# Save figure
plot_file = f"{n_features}_GB_plot.png"

plt.savefig(
    plot_file,
    dpi=600,
    bbox_inches="tight"
)

plt.show()

print("Saved:", plot_file)
