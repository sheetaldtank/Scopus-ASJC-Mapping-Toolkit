import pandas as pd
import re

# File paths
ejournal_file = "List_of_Ejournals.xlsx"
scopus_file = "Scopus_source_list.xlsx"
output_file = "List_of_Ejournals_with_ScopusID.xlsx"

# -------------------------------
# Function to clean column names
# -------------------------------
def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r'\s+', '', regex=True)
        .str.lower()
    )
    return df

# -----------------------------------------
# Function to normalize ISSN / E-ISSN values
# -----------------------------------------
def normalize_issn(value):
    if pd.isna(value):
        return None
    value = str(value).upper().strip()
    # Remove prefix like 'ISSN'
    value = re.sub(r'ISSN', '', value)
    # Keep only digits and 'X'
    value = re.sub(r'[^0-9X]', '', value)
    # Valid ISSN should have 8 characters
    return value if len(value) == 8 else None

# -------------------------------
# Load Excel files
# -------------------------------
ejournals = pd.read_excel(ejournal_file, dtype=str)
scopus = pd.read_excel(scopus_file, dtype=str)

# Clean column names
ejournals = clean_columns(ejournals)
scopus = clean_columns(scopus)

# -------------------------------
# Identify relevant columns
# -------------------------------
# Possible variations for ISSN and E-ISSN
issn_cols = ['issn']
eissn_cols = ['eissn', 'electronicissn', 'e-issn']

# Find columns in ejournals
ej_issn_col = next((col for col in issn_cols if col in ejournals.columns), None)
ej_eissn_col = next((col for col in eissn_cols if col in ejournals.columns), None)

# Find columns in scopus
sc_issn_col = next((col for col in issn_cols if col in scopus.columns), None)
sc_eissn_col = next((col for col in eissn_cols if col in scopus.columns), None)

# Validate presence of required columns
if 'sourcerecordid' not in scopus.columns:
    raise ValueError("❌ 'SourcerecordID' column not found in Scopus_source_list.xlsx")

if not ej_issn_col and not ej_eissn_col:
    raise ValueError("❌ No ISSN or E-ISSN column found in List_of_Ejournals.xlsx")

if not sc_issn_col and not sc_eissn_col:
    raise ValueError("❌ No ISSN or E-ISSN column found in Scopus_source_list.xlsx")

# Ensure scopusid column exists
if 'scopusid' not in ejournals.columns:
    ejournals['scopusid'] = pd.NA

# -------------------------------
# Normalize ISSN values
# -------------------------------
if ej_issn_col:
    ejournals['issn_norm'] = ejournals[ej_issn_col].apply(normalize_issn)
if ej_eissn_col:
    ejournals['eissn_norm'] = ejournals[ej_eissn_col].apply(normalize_issn)

if sc_issn_col:
    scopus['issn_norm'] = scopus[sc_issn_col].apply(normalize_issn)
if sc_eissn_col:
    scopus['eissn_norm'] = scopus[sc_eissn_col].apply(normalize_issn)

# -------------------------------
# Create a unified Scopus mapping
# -------------------------------
mapping_df_list = []

if 'issn_norm' in scopus.columns:
    mapping_df_list.append(
        scopus[['issn_norm', 'sourcerecordid']]
        .rename(columns={'issn_norm': 'issn_key'})
    )

if 'eissn_norm' in scopus.columns:
    mapping_df_list.append(
        scopus[['eissn_norm', 'sourcerecordid']]
        .rename(columns={'eissn_norm': 'issn_key'})
    )

scopus_map_df = pd.concat(mapping_df_list, ignore_index=True)
scopus_map_df = scopus_map_df.dropna(subset=['issn_key'])
scopus_map_df = scopus_map_df.drop_duplicates(subset=['issn_key'])

# Convert to dictionary for fast lookup
scopus_map = scopus_map_df.set_index('issn_key')['sourcerecordid'].to_dict()

# -------------------------------
# Function to fetch Scopus ID
# -------------------------------
def fetch_scopus_id(row):
    if 'issn_norm' in row and pd.notna(row['issn_norm']):
        if row['issn_norm'] in scopus_map:
            return scopus_map[row['issn_norm']]
    if 'eissn_norm' in row and pd.notna(row['eissn_norm']):
        if row['eissn_norm'] in scopus_map:
            return scopus_map[row['eissn_norm']]
    return pd.NA

# -------------------------------
# Update scopusid (overwrite existing values)
# -------------------------------
ejournals['scopusid'] = ejournals.apply(fetch_scopus_id, axis=1)

# Remove helper columns
cols_to_drop = [col for col in ['issn_norm', 'eissn_norm'] if col in ejournals.columns]
ejournals.drop(columns=cols_to_drop, inplace=True)

# -------------------------------
# Save the updated file
# -------------------------------
ejournals.to_excel(output_file, index=False)

# -------------------------------
# Summary Report
# -------------------------------
total_records = len(ejournals)
matched_records = ejournals['scopusid'].notna().sum()

print("\n✅ Scopus ID mapping completed successfully!")
print(f"📁 Output file: {output_file}")
print(f"📊 Total records: {total_records}")
print(f"✅ Records with Scopus ID: {matched_records}")
print(f"❌ Unmatched records: {total_records - matched_records}")