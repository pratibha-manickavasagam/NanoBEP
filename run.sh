
#!/bin/bash

# Initialize conda
source ~/anaconda3/etc/profile.d/conda.sh
# or source ~/miniconda3/etc/profile.d/conda.sh

conda activate nanobep || exit 1

cd Feature_generation || exit 1

python3 part1.py
python3 part2.py
python3 part3.py
python3 part4.py
python3 part5.py
python3 part6.py
python3 part7.py

cd ../Model_Testing || exit 1

python3 Test_your_data.py

# ==========================
# Move feature files to output
# ==========================

cd ..

mkdir -p output

# Get PDB ID from first data row of input.csv
PDB_ID=$(awk -F',' 'NR==2 {gsub(/^[ \t]+|[ \t]+$/, "", $1); print $1}' input/input.csv)

echo "PDB ID: $PDB_ID"

# Move and rename files
[ -f Feature_generation/49_aa_featuret.csv ]        && mv Feature_generation/49_aa_featuret.csv        output/${PDB_ID}_49_aa_featuret.csv

[ -f Feature_generation/AAPP.csv ]                  && mv Feature_generation/AAPP.csv                  output/${PDB_ID}_AAPP.csv

[ -f Feature_generation/Combined_Features.csv ]     && mv Feature_generation/Combined_Features.csv     output/${PDB_ID}_Combined_Features.csv

[ -f Feature_generation/contact_details_Nbcase.txt ] && mv Feature_generation/contact_details_Nbcase.txt output/${PDB_ID}_contact_details_Nbcase.txt

[ -f Feature_generation/features_final.csv ]        && mv Feature_generation/features_final.csv        output/${PDB_ID}_features_final.csv

[ -f Feature_generation/Zhange_energy_feature_Ab.csv ] && mv Feature_generation/Zhange_energy_feature_Ab.csv output/${PDB_ID}_Zhange_energy_feature_Nb.csv

echo "Feature files moved to output/"
