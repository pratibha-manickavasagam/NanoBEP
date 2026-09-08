import pandas as pd

# -----------------------------
# Files
# -----------------------------
txt_file = "contact_details_Nbcase.txt"
matrix_file = "Zhang_energy_matrix_nb.csv"
output_csv = "Zhange_energy_feature_Ab.csv"

# -----------------------------
# 1-letter → 3-letter (UPPERCASE)
# -----------------------------
aa_map = {
    'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP',
    'C': 'CYS', 'Q': 'GLN', 'E': 'GLU', 'G': 'GLY',
    'H': 'HIS', 'I': 'ILE', 'L': 'LEU', 'K': 'LYS',
    'M': 'MET', 'F': 'PHE', 'P': 'PRO', 'S': 'SER',
    'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL'
}

# -----------------------------
# Load energy matrix
# -----------------------------
matrix = pd.read_csv(matrix_file, index_col=0)

# Clean column names (remove spaces if any)
matrix.columns = matrix.columns.str.strip()
matrix.index = matrix.index.str.strip()

# -----------------------------
# Energy lookup function
# -----------------------------
def get_energy(aa1, aa2):
    if aa1 in matrix.index and aa2 in matrix.columns:
        return matrix.loc[aa1, aa2]
    elif aa2 in matrix.index and aa1 in matrix.columns:
        return matrix.loc[aa2, aa1]  # symmetric
    else:
        return None

# -----------------------------
# Read TXT
# -----------------------------
results = []

with open(txt_file, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

i = 0
while i < len(lines):

    if lines[i].startswith("PDB ID"):
        pdb_id = lines[i].split(":")[1].strip()
        i += 1

        pairs = []

        while i < len(lines) and not lines[i].startswith("PDB ID"):
            pairs.extend(lines[i].split(","))
            i += 1

        total_energy = 0.0
        count = 0

        for pair in pairs:
            pair = pair.strip()

            if len(pair) != 2:
                continue

            aa1_1 = pair[0]
            aa2_1 = pair[1]

            if aa1_1 not in aa_map or aa2_1 not in aa_map:
                continue

            aa1 = aa_map[aa1_1]
            aa2 = aa_map[aa2_1]

            energy = get_energy(aa1, aa2)

            if energy is None:
                continue

            total_energy += energy
            count += 1

        avg_energy = total_energy / count if count > 0 else None

        results.append({
            "pdb_id": pdb_id,
            "E_sum": total_energy,
            "E_avg": avg_energy,
            "N_contacts": count
        })

    else:
        i += 1

# -----------------------------
# Save output
# -----------------------------
df = pd.DataFrame(results)
df.to_csv(output_csv, index=False)

print("Done! Saved to:", output_csv)
