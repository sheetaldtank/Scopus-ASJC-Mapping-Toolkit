import pandas as pd
from rapidfuzz import process, fuzz

# ==========================
# File Paths (Modify as needed)
# ==========================
ASJC_FILE = "ASJC_classification_codes.xlsx"
INPUT_FILE = "without_asjc.xlsx"
OUTPUT_FILE = "mapped_ASJC_output.xlsx"
UNMATCHED_FILE = "unmatched_subjects.xlsx"  # Optional

# ==========================
# Load ASJC Classification Data
# ==========================
try:
    asjc_df = pd.read_excel(ASJC_FILE)
except FileNotFoundError:
    raise FileNotFoundError(f"ASJC file not found: {ASJC_FILE}")

# Standardize column names
asjc_df.columns = asjc_df.columns.str.strip()

required_columns = ["ASJC Code", "Description", "Main Subject", "Supergroup"]
for col in required_columns:
    if col not in asjc_df.columns:
        raise ValueError(f"Missing required column in ASJC file: {col}")

# Clean description column for better matching
asjc_df["Description_clean"] = (
    asjc_df["Description"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# List of descriptions for fuzzy matching
asjc_descriptions = asjc_df["Description_clean"].tolist()

# ==========================
# Function to Find Best Match
# ==========================
def find_best_asjc(subject, threshold=80):
    """
    Returns the best matching ASJC row for a given subject.
    If the similarity score is below the threshold, returns None.
    """
    subject_clean = str(subject).strip().lower()
    if not subject_clean:
        return None

    match = process.extractOne(
        subject_clean,
        asjc_descriptions,
        scorer=fuzz.token_sort_ratio
    )

    if match and match[1] >= threshold:
        matched_index = match[2]
        return asjc_df.iloc[matched_index]

    return None

# ==========================
# Load Input Subjects File
# ==========================
try:
    input_df = pd.read_excel(INPUT_FILE)
except FileNotFoundError:
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

input_df.columns = input_df.columns.str.strip()

if "subjectname" not in input_df.columns:
    raise ValueError("The input file must contain a 'subjectname' column.")

# Optional: store unmatched subjects for review
unmatched_subjects = set()

# ==========================
# Function to Map Subjects
# ==========================
def map_subjects(subject_string):
    """
    Maps semicolon-separated subjects to ASJC classifications.
    Only matched subjects are included in the output.
    """
    if pd.isna(subject_string) or not str(subject_string).strip():
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
            code = str(result["ASJC Code"]).strip()
            desc = str(result["Description"]).strip()
            main_sub = str(result["Main Subject"]).strip()
            supergroup = str(result["Supergroup"]).strip()

            # Avoid duplicates while preserving order
            if code not in codes:
                codes.append(code)
                descriptions.append(desc)
                if main_sub not in main_subjects:
                    main_subjects.append(main_sub)
                if supergroup not in supergroups:
                    supergroups.append(supergroup)
        else:
            unmatched_subjects.add(subject)

    return pd.Series({
        "ASJC Code": "; ".join(codes),
        "ASJC Description": "; ".join(descriptions),
        "Main Subject": "; ".join(main_subjects),
        "Supergroup": "; ".join(supergroups)
    })

# ==========================
# Apply Mapping
# ==========================
mapped_columns = input_df["subjectname"].apply(map_subjects)
output_df = pd.concat([input_df, mapped_columns], axis=1)

# ==========================
# Save Output File
# ==========================
output_df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Mapping completed successfully! Output saved as '{OUTPUT_FILE}'.")

# ==========================
# Save Unmatched Subjects (Optional)
# ==========================
if unmatched_subjects:
    pd.DataFrame(sorted(unmatched_subjects), columns=["Unmatched Subjects"]) \
        .to_excel(UNMATCHED_FILE, index=False)
    print(f"📄 Unmatched subjects saved to '{UNMATCHED_FILE}'.")
else:
    print("🎉 All subjects were successfully matched.")