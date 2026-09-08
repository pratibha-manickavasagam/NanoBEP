#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
import pandas as pd

# ==========================================================
# PATHS (EDIT IF NEEDED)
# ==========================================================
input_csv = "pdb/input.csv"

feature1_csv = "49_aa_featuret.csv"
feature2_csv = "AAPP.csv"
feature3_csv = "Zhange_energy_feature_Ab.csv"

ppdx_folder = "ppdxclean_folder"

output_csv = "Combined_Features.csv"

# ==========================================================
# READ PDB IDs
# ==========================================================
pdb_ids = []

with open(input_csv, "r") as f:
    reader = csv.reader(f)
    next(reader)  # Skip header

    for row in reader:
        pdb_ids.append(row[0].strip())

print(f"Found {len(pdb_ids)} PDB IDs")

# ==========================================================
# READ FEATURE CSV FILES
# ==========================================================
df49 = pd.read_csv(feature1_csv)
dfaapp = pd.read_csv(feature2_csv)
dfzhang = pd.read_csv(feature3_csv)

# ----------------------------------------------------------
# Rename first column to pdb_id if necessary
# ----------------------------------------------------------
for df in [df49, dfaapp, dfzhang]:
    df.rename(columns={df.columns[0]: "pdb_id"}, inplace=True)

# Keep only required PDB IDs
df49 = df49[df49["pdb_id"].isin(pdb_ids)]
dfaapp = dfaapp[dfaapp["pdb_id"].isin(pdb_ids)]
dfzhang = dfzhang[dfzhang["pdb_id"].isin(pdb_ids)]

# ==========================================================
# READ JSON FEATURES
# ==========================================================

json_rows = []

for pdb_id in pdb_ids:

    json_file = os.path.join(
        ppdx_folder,
        pdb_id,
        "descriptors-all.json"
    )

    if not os.path.exists(json_file):
        print(f"Missing JSON: {json_file}")
        continue

    with open(json_file) as f:
        data = json.load(f)

    row = {"pdb_id": pdb_id}

    # Remove outer key (e.g. 1kxq.pdb)
    data = data[f"{pdb_id}.pdb"]

    for section_name, section in data.items():

        for feature_name, feature_value in section.items():

            if isinstance(feature_value, dict):

                for idx, value in feature_value.items():

                    column = f"{section_name}_{feature_name}_{idx}"

                    row[column] = value

            else:

                row[f"{section_name}_{feature_name}"] = feature_value

    json_rows.append(row)

json_df = pd.DataFrame(json_rows)

# ==========================================================
# MERGE ALL FEATURES
# ==========================================================
combined = df49.merge(
    dfaapp,
    on="pdb_id",
    how="outer",
    suffixes=("", "_aapp")
)

combined = combined.merge(
    dfzhang,
    on="pdb_id",
    how="outer",
    suffixes=("", "_zhang")
)

combined = combined.merge(
    json_df,
    on="pdb_id",
    how="outer"
)

# ==========================================================
# SORT BY INPUT ORDER
# ==========================================================
combined["pdb_id"] = pd.Categorical(
    combined["pdb_id"],
    categories=pdb_ids,
    ordered=True
)

combined = combined.sort_values("pdb_id")

# ==========================================================
# SAVE
# ==========================================================
combined.to_csv(output_csv, index=False)

print(f"\nCombined feature file written to:\n{output_csv}")
