import pandas as pd
from rapidfuzz import process, fuzz

# File paths
asjc_file = "ASJC_classification_codes.xlsx"
input_file = "without_asjc.xlsx"
output_file = "mapped_ASJC_output.xlsx"

# Load ASJC classification data
asjc_df = pd.read_excel(asjc_file)

# Standardize column names
asjc_df.columns = asjc_df.columns.str.strip()

# Create a list of ASJC descriptions for matching
asjc_descriptions = asjc_df["Description"].astype(str).tolist()

# Function to find the best ASJC match for a subject
def find_best_asjc(subject, threshold=80):
    subject = str(subject).strip()
    if not subject:
        return None

    match, score, idx = process.extractOne(
        subject,
        asjc_descriptions,
        scorer=fuzz.token_sort_ratio
    )

    if score >= threshold:
        return asjc_df.iloc[idx]
    return None

# Load the input file containing subjects
input_df = pd.read_excel(input_file)
input_df.columns = input_df.columns.str.strip()

# Function to map semicolon-separated subjects
def map_subjects(subject_string):
    if pd.isna(subject_string):
        return pd.Series({
            "ASJC Code": "",
            "ASJC Description": "",
            "Main Subject": "",
            "Supergroup": ""
        })

    subjects = [s.strip() for s in str(subject_string).split(";") if s.strip()]

    codes = []
    descriptions = []
    main_subjects = []
    supergroups = []

    for subject in subjects:
        result = find_best_asjc(subject)
        if result is not None:
            code = str(result["ASJC Code"])
            desc = result["Description"]
            main_sub = result["Main Subject"]
            supergroup = result["Supergroup"]

            # Avoid duplicates while preserving order
            if code not in codes:
                codes.append(code)
                descriptions.append(desc)
                main_subjects.append(main_sub)
                supergroups.append(supergroup)
        else:
            descriptions.append(f"No match: {subject}")

    return pd.Series({
        "ASJC Code": "; ".join(codes),
        "ASJC Description": "; ".join(descriptions),
        "Main Subject": "; ".join(dict.fromkeys(main_subjects)),
        "Supergroup": "; ".join(dict.fromkeys(supergroups))
    })

# Apply the mapping
mapped_columns = input_df["subjectname"].apply(map_subjects)
output_df = pd.concat([input_df, mapped_columns], axis=1)

# Save the output
output_df.to_excel(output_file, index=False)

print(f"✅ Mapping completed successfully! Output saved as '{output_file}'.")