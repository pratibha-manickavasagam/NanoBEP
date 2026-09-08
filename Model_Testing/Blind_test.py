#!/usr/bin/env python
# coding: utf-8

# ===================================
# IMPORTS
# ===================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

# ===================================
# SETTINGS
# ===================================

train_file = "Train_data.csv"
test_file  = "Test_data.csv"

target = "Del_G"

features = ['126',  '137', '17','171','192','200', '4', '43', '44', '50', '62', '8', '83','90', 'Zg_Nb']


# Optional log transform
log_features = []

gb_params = {
    "n_estimators": 150,
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

def load_data(filepath, features, target):

    df = pd.read_csv(filepath)

    df.columns = [
        clean_feature(c)
        if c != target else c
        for c in df.columns
    ]

    df = df.loc[:, ~df.columns.duplicated()]

    df = df.drop(
        columns=[
            c for c in df.columns
            if "pdb" in c.lower()
        ],
        errors="ignore"
    )

    needed = features + [target]

    missing = [
        c for c in needed
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in {filepath}: {missing}"
        )

    df = df.apply(
        pd.to_numeric,
        errors="coerce"
    )

    df = df.dropna(
        subset=needed
    ).reset_index(drop=True)

    X = df[features].copy()

    for f in log_features:

        if f in X.columns:

            X[f] = X[f].apply(
                lambda x:
                np.sign(x) * np.log1p(abs(x))
            )

    y = df[target].values

    return X.values, y


# ===================================
# CLEAN FEATURE LIST
# ===================================

features = [
    clean_feature(f)
    for f in features
]

log_features = [
    clean_feature(f)
    for f in log_features
]

# ===================================
# LOAD TRAIN DATA
# ===================================

print("\nLoading training data...")

X_train, y_train = load_data(train_file,features,target)

# ===================================
# LOAD TEST DATA
# ===================================

print("\nLoading blind test data...")

X_test, y_test = load_data(
    test_file,
    features,
    target
)

print("\nTraining samples :", len(y_train))
print("Blind test samples :", len(y_test))
print("Features used :", len(features))

# ===================================
# TRAIN FINAL MODEL
# ===================================

print("\nTraining model...")

model = GradientBoostingRegressor( **gb_params)

model.fit(X_train,y_train)

# ===================================
# TRAIN PERFORMANCE
# ===================================

train_pred = model.predict(X_train)

train_r = r_score(y_train,train_pred)

train_mae = mean_absolute_error(y_train,train_pred)

# ===================================
# BLIND TEST PERFORMANCE
# ===================================

test_pred = model.predict(X_test)

test_r = r_score(
    y_test,
    test_pred
)

test_mae = mean_absolute_error(
    y_test,
    test_pred
)

test_slope = slope_score(
    y_test,
    test_pred
)

# ===================================
# RESULTS
# ===================================

print("\n==============================")
print("TRAIN")
print("==============================")

print(f"R     : {train_r:.4f}")
print(f"MAE   : {train_mae:.4f}")

print("\n==============================")
print("BLIND TEST")
print("==============================")

print(f"R     : {test_r:.4f}")
print(f"MAE   : {test_mae:.4f}")
#print(f"Slope : {test_slope:.4f}")

# ===================================
# SAVE PREDICTIONS
# ===================================

n_feat = len(features)

pred_file = (
    f"{n_feat}_GB_blind_test_predictions.csv"
)

pd.DataFrame({
    "Experimental_DelG": y_test,
    "Predicted_DelG": test_pred
}).to_csv(
    pred_file,
    index=False
)

print("\nSaved:", pred_file)

# ===================================
# BLIND TEST PLOT
# ===================================

plt.figure(figsize=(6,5))

plt.scatter(
    y_test,
    test_pred,
    alpha=0.7,marker="o",
    facecolors="black",
    edgecolors="black",
    s=45
)

min_val = min(y_test.min(),test_pred.min())

max_val = max(y_test.max(),test_pred.max())

x_line = np.linspace(min_val,max_val,100)

# Ideal line
plt.plot(x_line, x_line, color="black", linestyle="--")

# ±1 kcal/mol
plt.plot(x_line, x_line + 1, color="black",linestyle=":")

plt.plot(x_line, x_line - 1, color="black",linestyle=":")

# Regression line
m, b = np.polyfit(y_test,test_pred,1)



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



plt.xticks(
    fontsize=14
    
)

plt.yticks(
    fontsize=14)
    

text = (
    f"r = {test_r:.2f}\n"
    f"MAE = {test_mae:.2f}\n"
   
)

plt.text(
    0.05,
    0.95,
    text,
    transform=plt.gca().transAxes,
    verticalalignment="top",
    fontsize=12
)

plt.tight_layout()

plot_file = (
    f"{n_feat}_GB_blind_test_plot.png"
)

plt.savefig(
    plot_file,
    dpi=600,
    bbox_inches="tight"
)

plt.show()

print("Saved plot:", plot_file)

# ===================================
# SAVE TRAIN PREDICTIONS
# ===================================

train_pred_file = f"{n_feat}_GB_train_predictions.csv"

pd.DataFrame({
    "Experimental_DelG": y_train,
    "Predicted_DelG": train_pred
}).to_csv(
    train_pred_file,
    index=False
)

print("Saved:", train_pred_file)
