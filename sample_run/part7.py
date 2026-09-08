#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# =====================================
# INPUT / OUTPUT
# =====================================
input_file = "Combined_Features.csv"
output_file = "features_final.csv"

# =====================================
# READ CSV
# =====================================
df = pd.read_csv(input_file)

# =====================================
# CREATE NEW FEATURES
# =====================================

# Sum of dH, dHc and dHh -> Feature 210
df["210"] = (
    df["dH"].fillna(0) +
    df["dHc"].fillna(0) +
    df["dHh"].fillna(0)
)

# Sum of Feature 6, Feature 7 and Feature 8 -> Feature 200
df["200"] = (
    df["Feature 6"].fillna(0) +
    df["Feature 7"].fillna(0) +
    df["Feature 8"].fillna(0)
)

# =====================================
# SELECT REQUIRED FEATURES
# =====================================
selected = pd.DataFrame()

selected["pdb_id"] = df["pdb_id"]

selected["4"] = df["P"]
selected["8"] = df["Feature 5"]
selected["62"] = df["Ra"]
selected["43"] = df["dGh"]
selected["50"] = df["f"]
selected["164"] = df["Feature 8"]
selected["210"] = df["210"]
selected["200"] = df["200"]
selected["Zg_Nb"] = df["E_avg"]
selected["90"] = df["modeller_fast_NRES_0"]
selected["40"] = df["modeller_fast_pyDock_0"]
selected["126"] = df["modeller_fast_FoldX_elec_0"]
selected["192"] = df["modeller_fast_FireDock_laElec_0"]

# =====================================
# WRITE OUTPUT
# =====================================
selected.to_csv(output_file, index=False)

print(f"Final feature file written to: {output_file}")
