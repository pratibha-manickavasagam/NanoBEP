#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor

script_dir = Path(__file__).resolve().parent
train_file = "Train_data.csv"
feature_file = "../Feature_generation/features_final.csv"
input_csv = "../input/input.csv"
output_dir = Path("../output")
output_dir.mkdir(exist_ok=True)

target = "Del_G"
features = [
    '126',  '137', '17','171','192','200', '4', '43', '44', '50', '62', '8', '83','90', 'Zg_Nb'
]


gb_params = {
    "n_estimators":150,
    "learning_rate":0.05,
    "max_depth":3,
    "subsample":1,
    "min_samples_split":2,
    "random_state":42
}

def clean_feature(x):
    try:
        return str(int(float(x)))
    except Exception:
        return str(x)

def load_train(path):
    df = pd.read_csv(path)
    df.columns=[clean_feature(c) if c!=target else c for c in df.columns]
    df=df.loc[:,~df.columns.duplicated()]
    df=df.drop(columns=[c for c in df.columns if "pdb" in c.lower()],errors="ignore")
    need=features+[target]
    miss=[c for c in need if c not in df.columns]
    if miss:
        raise ValueError(f"Missing columns: {miss}")
    df=df.apply(pd.to_numeric,errors="coerce").dropna(subset=need)
    return df[features].values, df[target].values

def load_predict(path):
    df = pd.read_csv(path)
    df.columns=[clean_feature(c) for c in df.columns]
    df=df.loc[:,~df.columns.duplicated()]
    df=df.drop(columns=[c for c in df.columns if "pdb" in c.lower()],errors="ignore")
    miss=[c for c in features if c not in df.columns]
    if miss:
        raise ValueError(f"Missing columns: {miss}")
    df=df.apply(pd.to_numeric,errors="coerce").dropna(subset=features)
    return df[features].values

print("Loading training data...")
X_train,y_train=load_train(train_file)

print("Loading prediction features...")
X_pred=load_predict(feature_file)

print("Training model...")
model=GradientBoostingRegressor(**gb_params)
model.fit(X_train,y_train)

pred=model.predict(X_pred)

inp=pd.read_csv(input_csv)
if len(inp)!=len(pred):
    raise ValueError("Number of rows in input.csv and features_final.csv do not match.")

inp["ΔG (kcal/mol)"]=np.round(pred,2)

out=output_dir/"results.csv"
inp.to_csv(out,index=False)

print("\nPredicted Binding Energies")
for _,row in inp.iterrows():
    print(f"{row.iloc[0]} : {row['ΔG (kcal/mol)']:.2f} kcal/mol")

print(f"\nResults written to {out}")
