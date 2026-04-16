import pandas as pd
import re

# File paths
ejournal_file = "List_of_nononos.xlsx"  # Update if needed
asjc_file = "ASJC_Classification_Codes.xlsx"
output_file = "List_of_nononos_with_Subjects.xlsx"

# -------------------------------------------------
# Function to clean and standardize column names
# -------------------------------------------------
def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', ' ', regex=True)
    )
    return df

# -------------------------------------------------
# Function to normalize ASJC codes
# -------------------------------------------------
def extract_asjc_codes(codes):
    """
    Converts ASJC codes like '1705; 1706' or '1705,1706'
    into a list of clean 4-digit codes.
    """
    if pd.isna(codes):
        return []
    code_list = re.split(r'[;,]', str(codes))
    return [code.strip() for code in code_list if code.strip().isdigit()]

# -------------------------------------------------
# Function to remove duplicates while preserving order
# -------------------------------------------------
def unique_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if pd.notna(item) and item not in seen:
            seen.add(item)
            result.append(item)
    return result

# -------------------------------------------------
# Load Excel files
# -------------------------------------------------
ejournals = pd.read_excel(ejournal_file, dtype=str)
asjc = pd.read_excel(asjc_file, dtype=str)

# Clean column names
ejournals = clean_columns(ejournals)
asjc = clean_columns(asjc)

print("Ejournals columns:", ejournals.columns.tolist())
print("ASJC columns:", asjc.columns.tolist())

# -------------------------------------------------
# Identify required columns dynamically
# -------------------------------------------------
def find_column(columns, keyword):
    for col in columns:
        if keyword in col:
            return col
    return None

asjc_code_col = find_column(asjc.columns, 'asjc')
description_col = find_column(asjc.columns, 'description')
main_subject_col = find_column(asjc.columns, 'main')
supergroup_col = find_column(asjc.columns, 'super')

if not all([asjc_code_col, description_col, main_subject_col, supergroup_col]):
    raise ValueError(
        "❌ Required columns not found in ASJC_Classification_Codes.xlsx. "
        "Please ensure it contains 'ASJC Code', 'Description', 'Main Subject', and 'Supergroup'."
    )

# -------------------------------------------------
# Create mapping dictionaries
# -------------------------------------------------
asjc['asjc_code_clean'] = asjc[asjc_code_col].str.strip()

description_map = asjc.set_index('asjc_code_clean')[description_col].to_dict()
main_subject_map = asjc.set_index('asjc_code_clean')[main_subject_col].to_dict()
supergroup_map = asjc.set_index('asjc_code_clean')[supergroup_col].to_dict()

# -------------------------------------------------
# Function to map ASJC information
# -------------------------------------------------
def map_asjc_info(asjc_codes):
    codes = extract_asjc_codes(asjc_codes)
    
    descriptions = unique_preserve_order(
        [description_map.get(code) for code in codes if code in description_map]
    )
    main_subjects = unique_preserve_order(
        [main_subject_map.get(code) for code in codes if code in main_subject_map]
    )
    supergroups = unique_preserve_order(
        [supergroup_map.get(code) for code in codes if code in supergroup_map]
    )

    return pd.Series({
        'Subject Keywords': '; '.join(descriptions),
        'Main Subject': '; '.join(main_subjects),
        'Supergroup': '; '.join(supergroups)
    })

# -------------------------------------------------
# Ensure ASJC Codes column exists
# -------------------------------------------------
asjc_codes_col = find_column(ejournals.columns, 'asjc')

if asjc_codes_col is None:
    raise ValueError("❌ 'ASJC Codes' column not found in List_of_EJournals.xlsx")

# Apply mapping
ejournals[['Subject Keywords', 'Main Subject', 'Supergroup']] = \
    ejournals[asjc_codes_col].apply(map_asjc_info)

# -------------------------------------------------
# Save the final enriched dataset
# -------------------------------------------------
ejournals.to_excel(output_file, index=False)

print("\n✅ ASJC subject enrichment completed successfully!")
print(f"📁 Output file: {output_file}")