🧰 Features
🔍 Map Scopus Source Record IDs using ISSN/EISSN.
📥 Import ASJC codes associated with Scopus-indexed journals.
📚 Retrieve ASJC subject descriptions, main subjects, and supergroup details.
🔗 Map non-Scopus indexed journals using KBART subject keywords.
🧠 Intelligent keyword matching to identify the best ASJC classification.
🧹 Handle and resolve “No Match” scenarios effectively.

📂 Project Structure
scopus-asjc-mapping-toolkit/
│
├── Mapscopus.py
├── Importof.py
├── Mapasjc.py
├── Withoutasjc.py
├── Nomatchissue.py
├── data/                # Input files (Scopus source list, KBART files, etc.)
├── output/              # Generated outputs
├── requirements.txt
└── README.md
📝 Script Descriptions
1. Mapscopus.py

Purpose:
Maps the Scopus Source Record ID (sourcerecordID) using the ISSN or EISSN from the Scopus source list.

Key Functions:

Reads journal ISSN/EISSN from input data.
Matches them with the Scopus source list.
Outputs the corresponding sourcerecordID.

Input:

Scopus Source List (CSV/XLSX)
ISSN/EISSN dataset

Output:

Dataset with mapped sourcerecordID.
2. Importof.py

Purpose:
Imports ASJC codes from the Scopus source list using the mapped sourcerecordID and stores them in database tables.

Key Functions:

Extracts ASJC codes associated with each source.
Inserts or updates records in the database.

Input:

Output from Mapscopus.py
Scopus Source List

Output:

Database table populated with ASJC codes.
3. Mapasjc.py

Purpose:
Retrieves detailed ASJC metadata, including:

Subject Description
Main Subject
Supergroup

Key Functions:

Maps ASJC codes to their hierarchical subject structure.
Enriches journal records with standardized subject information.

Input:

ASJC Codes
ASJC reference dataset

Output:

Dataset or database table with enriched ASJC metadata.
4. Withoutasjc.py

Purpose:
Handles non-Scopus indexed e-journals by mapping KBART subject keywords to the closest ASJC codes.

Key Functions:

Extracts subject keywords from KBART files.
Performs keyword-based matching with ASJC descriptions.
Assigns the most relevant ASJC code and associated metadata.

Input:

KBART files of e-journals
ASJC reference dataset

Output:

Mapped ASJC codes and subject details for non-indexed journals.
5. Nomatchissue.py

Purpose:
Resolves cases where ASJC subject descriptions return a “No Match”.

Key Functions:

Removes “No Match” results.
Applies improved or fuzzy keyword matching.
Suggests the best possible ASJC classification.

Input:

Records with “No Match” results
ASJC reference dataset

Output:

Updated dataset with the best matching ASJC classifications.
