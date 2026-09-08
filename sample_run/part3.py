import pandas as pd

# -----------------------------
# Files
# -----------------------------
input_csv = "pdb/input.csv"
property_csv = "49aaprope.csv"
output_csv = "49_aa_featuret.csv"

# -----------------------------
# Mapping (1-letter → 3-letter)
# -----------------------------
aa_map = {
    'A': 'Ala', 'R': 'Arg', 'N': 'Asn', 'D': 'Asp',
    'C': 'Cys', 'Q': 'Gln', 'E': 'Glu', 'G': 'Gly',
    'H': 'His', 'I': 'Ile', 'L': 'Leu', 'K': 'Lys',
    'M': 'Met', 'F': 'Phe', 'P': 'Pro', 'S': 'Ser',
    'T': 'Thr', 'W': 'Trp', 'Y': 'Tyr', 'V': 'Val'
}

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(input_csv)

# IMPORTANT: skip serial number column, use Property as index
prop_df = pd.read_csv(property_csv)
prop_df = prop_df.set_index("Property")

# Drop serial number column if present
if prop_df.columns[0].lower().startswith("unnamed") or prop_df.columns[0] == "S.No":
    prop_df = prop_df.iloc[:, 1:]

properties = prop_df.index.tolist()

results = []

# -----------------------------
# Process each row
# -----------------------------
for _, row in df.iterrows():

    pdb_id = row.iloc[0]
    col2 = str(row.iloc[1])
    col3 = str(row.iloc[2])

    residues = col2.split(",") + col3.split(",")

    total_count = 0
    prop_sums = {p: 0.0 for p in properties}

    for res in residues:
        res = res.strip()
        if not res:
            continue

        aa1 = res[0]

        if aa1 not in aa_map:
            continue

        aa3 = aa_map[aa1]

        if aa3 not in prop_df.columns:
            continue

        # Add values for each property
        for p in properties:
            prop_sums[p] += prop_df.loc[p, aa3]

        total_count += 1

    # Average
    if total_count == 0:
        avg_props = {p: None for p in properties}
    else:
        avg_props = {p: prop_sums[p] / total_count for p in properties}

    result_row = {"pdb_id": pdb_id}
    result_row.update(avg_props)

    results.append(result_row)

# -----------------------------
# Save
# -----------------------------
out_df = pd.DataFrame(results)
out_df.to_csv(output_csv, index=False)

print("Done! Saved to:", output_csv)
