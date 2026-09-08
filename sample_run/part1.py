#!/usr/bin/env python3

import csv
import numpy as np
from pathlib import Path
from Bio.PDB import PDBParser


# ---------------------------
# Distance function
# ---------------------------
def euclidean_distance(atom1, atom2):
    return np.linalg.norm(atom1.coord - atom2.coord)


# ---------------------------
# Extract contacts
# ---------------------------
def extract_contacts_for_pdb(pdb_id, pdb_directory):

    pdb_file = Path(pdb_directory) / f"{pdb_id}.pdb"

    if not pdb_file.exists():
        print(f"File not found: {pdb_file}")
        return {}

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_id, str(pdb_file))
    model = structure[0]

    if "A" not in model or "B" not in model:
        print(f"Chains A/B missing in {pdb_id}")
        return {}

    chain1 = model["A"]
    chain2 = model["B"]

    residue_short_forms = {
        "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D",
        "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
        "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
        "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
        "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"
    }

    contacts_dict = {}

    for res1 in chain1:
        if res1.id[0] != " ":
            continue

        for res2 in chain2:
            if res2.id[0] != " ":
                continue

            min_dist = min(
                euclidean_distance(atom1, atom2)
                for atom1 in res1
                for atom2 in res2
            )

            if min_dist < 5.0:

                aa1 = residue_short_forms.get(res1.resname, res1.resname)
                aa2 = residue_short_forms.get(res2.resname, res2.resname)

                pair = aa1 + aa2

                contacts_dict.setdefault(aa2, set()).add(pair)

    return contacts_dict


def main():

    pdb_directory = Path("pdb")
    csv_file = pdb_directory / "input.csv"

    output_file = Path("contact_details_Nbcase.txt")

    pdb_ids = []

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            if row:
                pdb_ids.append(row[0].strip())

    with open(output_file, "w") as out:

        for pdb_id in pdb_ids:

            contacts = extract_contacts_for_pdb(pdb_id, pdb_directory)

            out.write(f"PDB ID: {pdb_id}\n")

            for residue, pairs in sorted(contacts.items()):
                out.write(",".join(sorted(pairs)) + "\n")

            out.write("\n")

    print(f"Contact details written to {output_file}")


if __name__ == "__main__":
    main()
