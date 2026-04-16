# 📚 Scopus ASJC Mapping Toolkit

## 📖 Overview
The **Scopus ASJC Mapping Toolkit** is a collection of Python scripts designed to enrich journal metadata by mapping **Scopus Source Record IDs**, **ASJC (All Science Journal Classification) codes**, and **subject hierarchies**. The toolkit also supports the classification of **non-Scopus indexed e-journals** using **KBART subject keywords** with intelligent matching techniques.

This project is particularly useful for **academic and research libraries**, bibliometric studies, and collection development activities.

---

## 🧰 Key Features

- 🔍 Map **Scopus Source Record IDs** using ISSN/EISSN.
- 📥 Import **ASJC codes** for Scopus-indexed journals.
- 📚 Retrieve **ASJC subject descriptions**, **main subjects**, and **supergroup details**.
- 🔗 Classify **non-Scopus indexed journals** using **KBART subject keywords**.
- 🧠 Intelligent keyword matching to determine the **best ASJC classification**.
- 🧹 Resolve **“No Match”** scenarios through enhanced matching techniques.
- 🗄️ Store enriched metadata in database tables or structured files.

---

## 📂 Project Structure
scopus-asjc-mapping-toolkit/
│
├── Mapscopus.py # Maps ISSN/EISSN to Scopus Source Record IDs
├── Importof.py # Imports ASJC codes using Source Record IDs
├── Mapasjc.py # Maps ASJC codes to subject descriptions and hierarchy
├── Withoutasjc.py # Maps KBART subject keywords for non-Scopus journals
├── Nomatchissue.py # Resolves "No Match" cases using improved matching
├── data/ # Input datasets (Scopus, ASJC, KBART)
├── output/ # Generated output files
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## 📝 Script Descriptions

### 1. `Mapscopus.py`
**Purpose:**  
Maps the **Scopus Source Record ID (`sourcerecordID`)** using **ISSN** or **EISSN**.

**Inputs:**
- Scopus Source List (CSV/XLSX)
- Journal dataset containing ISSN/EISSN

**Outputs:**
- Dataset with mapped `sourcerecordID`.

---

### 2. `Importof.py`
**Purpose:**  
Imports **ASJC codes** from the Scopus Source List using the mapped `sourcerecordID` and stores them in database tables.

**Inputs:**
- Output from `Mapscopus.py`
- Scopus Source List

**Outputs:**
- Database or file containing ASJC codes for each journal.

---

### 3. `Mapasjc.py`
**Purpose:**  
Maps **ASJC codes** to their hierarchical subject information.

**Enriched Fields:**
- Subject Description
- Main Subject
- Supergroup

**Inputs:**
- ASJC codes
- ASJC reference dataset

**Outputs:**
- Enriched dataset with hierarchical subject classifications.

---

### 4. `Withoutasjc.py`
**Purpose:**  
Handles **non-Scopus indexed e-journals** by mapping **KBART subject keywords** to the most relevant **ASJC codes**.

**Inputs:**
- KBART files
- ASJC reference dataset

**Outputs:**
- ASJC codes and subject details for non-indexed journals.

---

### 5. `Nomatchissue.py`
**Purpose:**  
Improves classification when ASJC subject descriptions initially return a **“No Match”**.

**Functionality:**
- Removes "No Match" labels.
- Applies enhanced or fuzzy keyword matching.
- Assigns the best possible ASJC classification.

**Inputs:**
- Records with "No Match"
- ASJC reference dataset

**Outputs:**
- Updated dataset with refined ASJC mappings.

### 6. 'nonasjcmapping.py'
**This Python script maps journal subject names from `List_of_EJournals.xlsx` to standardized Scopus ASJC classifications using a lookup table. It handles multiple semicolon-separated subjects, performs case-insensitive matching, removes duplicates, and enriches the dataset with **ASJC Codes**, **Subject Keywords**, **Main Subject**, and **Supergroup** fields.
---**

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/scopus-asjc-mapping-toolkit.git
cd scopus-asjc-mapping-toolkit

### ASJC Subject Mapping Script

