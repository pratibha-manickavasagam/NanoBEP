#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import shutil
import subprocess
import warnings
from Bio.PDB import PDBParser, PPBuilder
from Bio import BiopythonDeprecationWarning

warnings.simplefilter("ignore", BiopythonDeprecationWarning)

# =========================
# PATHS (EDIT IF NEEDED)
# =========================
cleaned_pdb_dir = "pdb"
output_dir = "ppdxclean_folder"
additional_files_dir = "additional_files"
csv_file = "pdb/input.csv"

NUM_THREADS = "4"

# =========================
# SET THREAD ENVIRONMENT
# =========================
env = os.environ.copy()
env["OMP_NUM_THREADS"] = NUM_THREADS
env["OPENBLAS_NUM_THREADS"] = NUM_THREADS
env["MKL_NUM_THREADS"] = NUM_THREADS
env["NUMEXPR_NUM_THREADS"] = NUM_THREADS

# =========================
# CREATE OUTPUT DIRECTORY
# =========================
os.makedirs(output_dir, exist_ok=True)


# =========================
# FUNCTION: EXTRACT SEQUENCE
# =========================
def get_sequence_from_pdb(pdb_id, pdb_path):

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_id, pdb_path)
    ppb = PPBuilder()

    sequences = []

    for model in structure:
        for chain in model:

            seq = ""

            for peptide in ppb.build_peptides(chain):
                seq += str(peptide.get_sequence())

            if seq:
                sequences.append(seq)

    return "/".join(sequences)


# =========================
# STEP 1: PREPARE PPDX FOLDERS
# =========================
print("\nCreating PPDX folders...\n")

with open(csv_file, "r") as f:

    reader = csv.reader(f)
    next(reader)

    for row in reader:

        pdb_id = row[0].strip()

        pdb_file = os.path.join(cleaned_pdb_dir, f"{pdb_id}.pdb")

        if not os.path.exists(pdb_file):
            print(f"Missing PDB: {pdb_file}")
            continue

        pdb_folder = os.path.join(output_dir, pdb_id)
        ppdb_folder = os.path.join(pdb_folder, "ppdb")

        os.makedirs(ppdb_folder, exist_ok=True)

        # Copy PDB
        shutil.copy2(
            pdb_file,
            os.path.join(ppdb_folder, f"{pdb_id}.pdb")
        )

        # Extract sequence
        try:
            sequence = get_sequence_from_pdb(pdb_id, pdb_file)

        except Exception as e:
            print(f"Sequence extraction failed for {pdb_id}")
            print(e)
            continue

        # Write ppdb.seq
        with open(os.path.join(ppdb_folder, "ppdb.seq"), "w") as fseq:
            fseq.write(f">{pdb_id}.pdb\n")
            fseq.write(sequence + "\n")

        # Write ppdb.txt
        with open(os.path.join(ppdb_folder, "ppdb.txt"), "w") as ftxt:
            ftxt.write("#Name\tRecN LigN\t\tdGexp\tTemplate\n")
            ftxt.write(f"{pdb_id}.pdb\t1 1\t0.0\t{pdb_id}.pdb\n")

        # Copy compute_descriptors.py
        shutil.copy2(
            os.path.join(additional_files_dir, "compute_descriptors.py"),
            os.path.join(pdb_folder, "compute_descriptors.py")
        )

        # Copy config file
        shutil.copy2(
            os.path.join(additional_files_dir, "config-ppdx.ini"),
            os.path.join(pdb_folder, "config-ppdx.ini")
        )

        print(f"Prepared {pdb_id}")


# =========================
# STEP 2: RUN PPDX
# =========================
print("\nRunning PPDX...\n")

with open(csv_file, "r") as f:

    reader = csv.reader(f)
    next(reader)

    for row in reader:

        pdb_id = row[0].strip()

        pdb_folder = os.path.join(output_dir, pdb_id)

        compute_script = os.path.join(
            pdb_folder,
            "compute_descriptors.py"
        )

        if not os.path.exists(compute_script):
            print(f"Missing compute_descriptors.py for {pdb_id}")
            continue

        if not os.path.exists(os.path.join(pdb_folder, "config-ppdx.ini")):
            print(f"Missing config-ppdx.ini for {pdb_id}")
            continue

        print(f"Running {pdb_id}")

        try:

            subprocess.run(
                ["python3", "compute_descriptors.py"],
                cwd=pdb_folder,
                env=env,
                check=True
            )

            print(f"Completed {pdb_id}")

        except subprocess.CalledProcessError as e:

            print(f"Failed {pdb_id}")
            print(e)

print("\nFinished.\n")
