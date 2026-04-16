import pandas as pd

# File paths
ejournal_file = "nononosupdated.xlsx"
scopus_file = "Scopus_source_list.xlsx"
output_file = "List_of_nononos.xlsx"

# -----------------------------------
# Function to standardize column names
# -----------------------------------
def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', ' ', regex=True)
    )
    return df

# -----------------------------------
# Function to find a column by keywords
# -----------------------------------
def find_column(columns, keywords):
    for col in columns:
        if all(keyword in col for keyword in keywords):
            return col
    return None

# -----------------------------------
# Load Excel files
# -----------------------------------
ejournals = pd.read_excel(ejournal_file, dtype=str)
scopus = pd.read_excel(scopus_file, dtype=str)

# Clean column names
ejournals = clean_columns(ejournals)
scopus = clean_columns(scopus)

print("Ejournals columns:", ejournals.columns.tolist())
print("Scopus columns:", scopus.columns.tolist())

# -----------------------------------
# Identify required columns dynamically
# -----------------------------------
scopus_id_col = find_column(scopus.columns, ['sourcerecordid']) \
                 or find_column(scopus.columns, ['source', 'record', 'id'])

asjc_col = find_column(scopus.columns, ['asjc'])
active_col = find_column(scopus.columns, ['active'])
coverage_col = find_column(scopus.columns, ['coverage'])

if scopus_id_col is None:
    raise ValueError("❌ 'SourcerecordID' column not found in Scopus file.")

if 'scopusid' not in ejournals.columns:
    raise ValueError("❌ 'scopusid' column not found in List_of_EJournals file.")

print(f"Detected columns:")
print(f"  SourcerecordID -> {scopus_id_col}")
print(f"  ASJC Codes     -> {asjc_col}")
print(f"  Active Status  -> {active_col}")
print(f"  Coverage       -> {coverage_col}")

# -----------------------------------
# Prepare Scopus subset for merging
# -----------------------------------
columns_to_use = [scopus_id_col]
if asjc_col:
    columns_to_use.append(asjc_col)
if active_col:
    columns_to_use.append(active_col)
if coverage_col:
    columns_to_use.append(coverage_col)

scopus_subset = (
    scopus[columns_to_use]
    .drop_duplicates(subset=[scopus_id_col])
)

# -----------------------------------
# Merge with ejournals on scopusid
# -----------------------------------
merged = ejournals.merge(
    scopus_subset,
    left_on='scopusid',
    right_on=scopus_id_col,
    how='left'
)

# -----------------------------------
# Rename columns to desired output names
# -----------------------------------
rename_dict = {}
if asjc_col:
    rename_dict[asjc_col] = 'ASJC Codes'
if active_col:
    rename_dict[active_col] = 'Active or Inactive'
if coverage_col:
    rename_dict[coverage_col] = 'Coverage'

merged.rename(columns=rename_dict, inplace=True)

# Drop redundant key column
merged.drop(columns=[scopus_id_col], inplace=True)

# -----------------------------------
# Save the enriched file
# -----------------------------------
merged.to_excel(output_file, index=False)

# -----------------------------------
# Summary statistics
# -----------------------------------
if 'ASJC Codes' in merged.columns:
    enriched_records = merged['ASJC Codes'].notna().sum()
else:
    enriched_records = 0

total_records = len(merged)

print("\n✅ Metadata enrichment completed successfully!")
print(f"📁 Output file: {output_file}")
print(f"📊 Total records: {total_records}")
print(f"✅ Records enriched with Scopus metadata: {enriched_records}")
print(f"❌ Records without Scopus metadata: {total_records - enriched_records}")