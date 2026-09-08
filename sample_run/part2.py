#!/usr/bin/env python3

import csv


def read_values_matrices(values_file_path):
    with open(values_file_path, 'r') as file:
        values_text = file.read()

    return [matrix.strip() for matrix in values_text.split('"""\n') if matrix.strip()]


def create_amino_acid_interactions_dicts(values_matrices, amino_acid_pairs_lines):
    amino_acid_interactions_dicts_list = []

    for values_matrix_text in values_matrices:
        values_lines = values_matrix_text.strip().split('\n')
        amino_acid_interactions_dict = {}

        for i, pairs_line in enumerate(amino_acid_pairs_lines):
            pairs = pairs_line.split()
            values = values_lines[i].split()

            for j, pair in enumerate(pairs):
                if values[j] == 'NA':
                    interaction_value = 0.00
                else:
                    interaction_value = float(values[j])
                amino_acid_interactions_dict[pair] = interaction_value

        amino_acid_interactions_dicts_list.append(amino_acid_interactions_dict)

    return amino_acid_interactions_dicts_list


def calculate_amino_acid_potential_sums(amino_acid_interactions_dicts_list, pdb_id_to_pairs):
    result = {}

    for pdb_id, pairs_lines in pdb_id_to_pairs.items():
        potential_sums = [0.0] * len(amino_acid_interactions_dicts_list)

        for i, amino_acid_interactions_dict in enumerate(amino_acid_interactions_dicts_list):
            total_sum = 0.0
            for pairs_line in pairs_lines:
                pairs = pairs_line.split(',')
                for pair in pairs:
                    total_sum += amino_acid_interactions_dict.get(pair, 0.0)
            potential_sums[i] = total_sum

        result[pdb_id] = potential_sums

    return result


# Load amino acid interactions dictionaries using your previous code
values_file_path = 'aapp_matrices_all40.txt'

amino_acid_pairs_matrix = """
AA
AR RR
AN RN NN
AD RD ND DD
AC RC NC DC CC
AQ RQ NQ DQ CQ QQ
AE RE NE DE CE QE EE
AG RG NG DG CG QG EG GG
AH RH NH DH CH QH EH GH HH
AI RI NI DI CI QI EI GI HI II
AL RL NL DL CL QL EL GL HL IL LL
AK RK NK DK CK QK EK GK HK IK LK KK
AM RM NM DM CM QM EM GM HM IM LM KM MM
AF RF NF DF CF QF EF GF HF IF LF KF MF FF
AP RP NP DP CP QP EP GP HP IP LP KP MP FP PP
AS RS NS DS CS QS ES GS HS IS LS KS MS FS PS SS
AT RT NT DT CT QT ET GT HT IT LT KT MT FT PT ST TT
AW RW NW DW CW QW EW GW HW IW LW KW MW FW PW SW TW WW
AY RY NY DY CY QY EY GY HY IY LY KY MY FY PY SY TY WY YY
AV RV NV DV CV QV EV GV HV IV LV KV MV FV PV SV TV WV YV VV
"""

amino_acid_pairs_lines = amino_acid_pairs_matrix.strip().split('\n')

values_matrices = read_values_matrices(values_file_path)

amino_acid_interactions_dicts_list = create_amino_acid_interactions_dicts(
    values_matrices,
    amino_acid_pairs_lines
)

# Read the second text file containing PDB IDs and pairs
second_text_file_path = 'contact_details_Nbcase.txt'
csv_file = "pdb/input.csv"

with open(second_text_file_path, 'r') as file:
    second_text_file = file.read()

# Split the second text file into lines
second_text_lines = second_text_file.strip().split('\n')

# Parse PDB IDs and pairs
pdb_id_to_pairs = {}
current_pdb_id = None

for line in second_text_lines:
    if line.startswith("PDB ID:"):
        current_pdb_id = line.split(":")[1].strip()
        pdb_id_to_pairs[current_pdb_id] = []
    else:
        pdb_id_to_pairs[current_pdb_id].append(line)

result = calculate_amino_acid_potential_sums(
    amino_acid_interactions_dicts_list,
    pdb_id_to_pairs
)

# Read the log(Kd) values from the Kd data CSV file
log_kd_values = {}

with open(csv_file, mode='r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)

    for row in csv_reader:
        pdb_id = row[0].split("_")[0]
        log_kd = row[1]
        log_kd_values[pdb_id] = log_kd

# Add the log(Kd) values to the result
for pdb_id, potential_sums in result.items():
    if pdb_id in log_kd_values:
        potential_sums.append(log_kd_values[pdb_id])
    else:
        potential_sums.append("")

# Create a list to store the data in CSV format
csv_data = [["PDB ID"] +
            [f"Feature {i+1}" for i in range(len(amino_acid_interactions_dicts_list))] +
            ["log(Kd)"]]

for pdb_id, potential_sums in result.items():
    csv_data.append([pdb_id] + potential_sums)

# Specify the CSV file path where you want to save the data
csv_file_path = 'AAPP.csv'

# Write the data to the CSV file
with open(csv_file_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(csv_data)

print(f"Data with log(Kd) values saved to {csv_file_path}")
