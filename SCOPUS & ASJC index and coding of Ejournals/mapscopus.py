import pandas as pd
import re

# File paths
ejournal_file = "nononos.xlsx"
scopus_file = "Scopus_source_list.xlsx"
output_file = "List_of_Ejournals_updated.xlsx"

# Function to normalize ISSN/E-ISSN
def normalize_issn(issn):
    """
    Standardizes ISSN/E-ISSN to the format ####-####.
    Handles values with spaces, missing hyphens, or lowercase 'x'.
    """
    if pd.isna(issn):
        return None
    issn = str(issn).strip().upper()
    issn = re.sub(r'[^0-9X]', '', issn)  # Keep digits and 'X'
    if len(issn) == 8:
        return issn[:4] + '-' + issn[4:]
    return None

# Function to clean column names
def clean_columns(df):
    """
    Standardizes column names by removing extra spaces and converting to lowercase.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r'\s+', '', regex=True)  # Remove spaces within names
        .str.lower()
    )
    return df

# Load Excel files
ejournals = pd.read_excel(ejournal_file, dtype=str)
scopus = pd.read_excel(scopus_file, dtype=str)

# Clean column names
ejournals = clean_columns(ejournals)
scopus = clean_columns(scopus)

# Display column names for verification (optional)
print("Ejournals columns:", ejournals.columns.tolist())
print("Scopus columns:", scopus.columns.tolist())

# Identify the E-ISSN column in each file
eissn_candidates = ['eissn', 'electronicissn', 'e_issn']
ej_eissn_col = next((col for col in eissn_candidates if col in ejournals.columns), None)
scopus_eissn_col = next((col for col in eissn_candidates if col in scopus.columns), None)

if not ej_eissn_col:
    raise ValueError("❌ E-ISSN column not found in List_of_Ejournals.xlsx")
if not scopus_eissn_col:
    raise ValueError("❌ E-ISSN column not found in Scopus_source_list.xlsx")

# Ensure the SourcerecordID column exists
if 'sourcerecordid' not in scopus.columns:
    raise ValueError("❌ 'SourcerecordID' column not found in Scopus_source_list.xlsx")

# Normalize E-ISSN values
ejournals['eissn_norm'] = ejournals[ej_eissn_col].apply(normalize_issn)
scopus['eissn_norm'] = scopus[scopus_eissn_col].apply(normalize_issn)

# Prepare Scopus mapping table
scopus_map = (
    scopus[['eissn_norm', 'sourcerecordid']]
    .dropna(subset=['eissn_norm'])
    .drop_duplicates(subset=['eissn_norm'])
)

# Merge with the ejournals dataset
merged = ejournals.merge(
    scopus_map,
    on='eissn_norm',
    how='left'
)

# Rename the mapped column to 'scopusid'
merged.rename(columns={'sourcerecordid': 'scopusid'}, inplace=True)

# Remove helper column
merged.drop(columns=['eissn_norm'], inplace=True)

# Save the updated Excel file
merged.to_excel(output_file, index=False)

# Generate summary statistics
total_records = len(merged)
matched_records = merged['scopusid'].notna().sum()

print("\n✅ Merge completed successfully!")
print(f"📁 Output file: {output_file}")
print(f"📊 Total records: {total_records}")
print(f"✅ Matched records: {matched_records}")
print(f"❌ Unmatched records: {total_records - matched_records}")