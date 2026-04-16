import pandas as pd
import re

# -------------------------------------------------
# File paths
# -------------------------------------------------
ejournal_file = "List_of_nonasjc_EJournals.xlsx"
lookup_file = "Unmatched_Subjects_ASJC_Mapping.xlsx"
output_file = "List_of_EJournals_Mapped.xlsx"

# -------------------------------------------------
# Function to clean column names
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
# Function to normalize subject text
# -------------------------------------------------
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = text.replace('&', 'and')
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)      # Normalize spaces
    return text.strip()

# -------------------------------------------------
# Function to split semicolon-separated subjects
# -------------------------------------------------
def split_subjects(text):
    if pd.isna(text):
        return []
    return [item.strip() for item in str(text).split(';') if item.strip()]

# -------------------------------------------------
# Function to remove duplicates while preserving order
# -------------------------------------------------
def unique_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result

# -------------------------------------------------
# Load Excel files
# -------------------------------------------------
ejournals = pd.read_excel(ejournal_file, dtype=str)
lookup = pd.read_excel(lookup_file, dtype=str)

# Clean column names
ejournals = clean_columns(ejournals)
lookup = clean_columns(lookup)

# Validate required columns
if 'subjectname' not in ejournals.columns:
    raise ValueError("❌ 'subjectname' column not found in List_of_EJournals.xlsx")

required_lookup_cols = [
    'unmatched subject',
    'mapped asjc description',
    'asjc code',
    'main subject',
    'supergroup'
]
for col in required_lookup_cols:
    if col not in lookup.columns:
        raise ValueError(f"❌ Column '{col}' not found in the lookup table")

# Normalize lookup keys
lookup['subject_key'] = lookup['unmatched subject'].apply(normalize_text)

# Create mapping dictionaries
description_map = lookup.set_index('subject_key')['mapped asjc description'].to_dict()
asjc_map = lookup.set_index('subject_key')['asjc code'].to_dict()
main_map = lookup.set_index('subject_key')['main subject'].to_dict()
supergroup_map = lookup.set_index('subject_key')['supergroup'].to_dict()

# -------------------------------------------------
# Function to map subjects
# -------------------------------------------------
def map_subjects(subject_text):
    subjects = split_subjects(subject_text)

    descriptions = []
    asjc_codes = []
    main_subjects = []
    supergroups = []

    for subj in subjects:
        key = normalize_text(subj)
        if key in description_map:
            descriptions.append(description_map[key])
            asjc_codes.append(asjc_map[key])
            main_subjects.append(main_map[key])
            supergroups.append(supergroup_map[key])

    return pd.Series({
        'ASJC Codes': '; '.join(unique_preserve_order(asjc_codes)),
        'Subject Keywords': '; '.join(unique_preserve_order(descriptions)),
        'Main Subject': '; '.join(unique_preserve_order(main_subjects)),
        'Supergroup': '; '.join(unique_preserve_order(supergroups))
    })

# Apply mapping
mapped_columns = ejournals['subjectname'].apply(map_subjects)
ejournals = pd.concat([ejournals, mapped_columns], axis=1)

# Save the output
ejournals.to_excel(output_file, index=False)

# Summary
total_records = len(ejournals)
matched_records = ejournals['ASJC Codes'].astype(bool).sum()

print("\n✅ Subject mapping completed successfully!")
print(f"📁 Output file: {output_file}")
print(f"📊 Total records: {total_records}")
print(f"✅ Matched records: {matched_records}")
print(f"❌ Unmatched records: {total_records - matched_records}")