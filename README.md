# Lexical Checker - XML Parser and Dictionary Validator

A comprehensive tool to extract, tokenize, and validate text content from XML files against an English dictionary. Perfect for historical text analysis, OCR validation, and linguistic research.

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Step-by-Step Usage](#step-by-step-usage)
- [Understanding the Output](#understanding-the-output)
- [Viewing Results in Excel](#viewing-results-in-excel)
- [Project Structure](#project-structure)
- [Statistics](#statistics)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **XML Parsing**: Extracts plain text from BITS (Book Interchange Tag Suite) XML files
- **Recursive Scanning**: Automatically finds all XML files in `docs/` and subdirectories
- **Smart Extraction**: Removes metadata while preserving article content
- **Date-Based Naming**: Output files named by date pattern (`yyyy-mm_article-id.txt`)
- **Text Tokenization**: Uses NLTK to break text into individual words
- **Dictionary Validation**: Checks 1M+ tokens against 111,573 English dictionary entries
- **Smart Categorization**: Classifies unknown words (misspellings, numbers, punctuation, etc.)
- **Excel Export**: Generates CSV files ready for spreadsheet analysis
- **Comprehensive Reports**: Detailed statistics and analysis at every step

## 🚀 Quick Start

**Complete workflow in 4 commands:**

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Extract text from XML files
python .\scripts\test_parse.py

# 3. Tokenize and validate against dictionary
python .\scripts\tokenize_files.py
python .\scripts\check_dictionary.py

# 4. Export to CSV for Excel
python .\scripts\export_to_csv.py
```

**That's it!** Your results will be in the `data/` folder as CSV files ready to open in Excel.

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Windows PowerShell (or Command Prompt)

### Step 1: Clone or Download

Download this project to your computer or clone it:

```powershell
git clone <repository-url>
cd lexical-checker
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you get an error about execution policies, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `lxml` - For XML parsing
- `nltk` - For text tokenization

## 📖 Step-by-Step Usage

### Step 1: Parse XML Files (Extract Text)

**What it does:** Finds all XML files in the `docs/` folder, extracts article text, and saves each article as a separate `.txt` file.

**Run this command:**

```powershell
python .\scripts\test_parse.py
```

**What you'll see:**

```
Processing 40282.xml...
  -> Created 1862 text files

Processed 1 XML file(s)
Total: 1862 article files written to 'c:\...\output'

Sample files created:
  - 1817-01_486376978.txt (2,874 bytes)
  - 1817-01_486382965.txt (10,271 bytes)
  ...
```

**Output:** Text files in `output/` folder (e.g., `1817-01_486376978.txt`)

---

### Step 2: Tokenize Text Files

**What it does:** Breaks down each text file into individual words (tokens) and saves statistics.

**Run this command:**

```powershell
python .\scripts\tokenize_files.py
```

**What you'll see:**

```
Tokenizing all text files in: c:\...\output

Tokenizing 1861 files...
  Processed 100/1861 files...
  Processed 200/1861 files...
  ...

============================================================
Tokenization Summary
============================================================
Total files processed: 1,861
Total tokens across all files: 1,131,086
Unique tokens across all files: 99,305
Average tokens per file: 607.8
```

**Output:** `data/tokenized_summary.json` (contains all tokens and statistics)

---

### Step 3: Check Tokens Against Dictionary

**What it does:** Compares every token against an English dictionary and identifies unknown words.

**Run this command:**

```powershell
python .\scripts\check_dictionary.py
```

**What you'll see:**

```
======================================================================
LEXICAL CHECKER - Dictionary Validation
======================================================================

Loading dictionary into memory...
Loaded 111,573 unique words
Processed 100/1861 files...
...

======================================================================
OVERALL SUMMARY
======================================================================
Files processed: 1,861
Total tokens: 1,131,086
Dictionary size: 111,573 words
Stemming method: SNOWBALL

Found (original): 818,837 (75.78%)
Found (via stem): 39,117 (3.46%)
Found (via hyphenated): 11,495 (1.02%)
TOTAL FOUND: 869,449 (76.87%)
Not found: 261,637

Stemming improvement: +3.46%
Hyphenated improvement: +1.02%
Unique words found via stem: 3,636
Unique words found via hyphenated: 5,001
Unique unknown: 60,364

======================================================================
UNKNOWN WORDS ANALYSIS
======================================================================

POTENTIAL MISSPELLINGS (50,356 unique):
  - aac
  - aacmuald
  - aacnibald
  ...

HYPHENATED (12,364 unique):
  - abbey-church
  - able-bodied
  ...
```

**Output:** 
- `data/dictionary_check_results.json` (detailed results)
- `data/unknown_words_analysis.json` (categorized unknowns)

---

### Step 4: Export to CSV for Excel

**What it does:** Converts JSON results into Excel-friendly CSV files.

**Run this command:**

```powershell
python .\scripts\export_to_csv.py
```

**What you'll see:**

```
======================================================================
CSV Export - Dictionary Check Results
======================================================================

Loading results from: ...dictionary_check_results.json
Exporting 1861 files to CSV...
✓ Main results exported to: ...dictionary_results.csv
  File size: 1,723,670 bytes
✓ Summary exported to: ...dictionary_results_summary.csv
  File size: 167 bytes

✓ Unknown words exported to: ...unknown_words.csv
  File size: 1,953,824 bytes

======================================================================
Export Complete!
======================================================================

Generated files:
  1. dictionary_results.csv
  2. dictionary_results_summary.csv
  3. unknown_words.csv
  4. unknown_words_categories.csv
```

**Output:** 4 CSV files in `data/` folder, ready to open in Excel!

## 📊 Understanding the Output

### Output Folder Structure

```
lexical-checker/
├── docs/              # Input: Your XML files go here
├── output/            # Generated text files (one per article)
├── data/              # Results and statistics
│   ├── dictionary_results.csv              ← Open this in Excel!
│   ├── dictionary_results_summary.csv      ← Quick overview
│   ├── unknown_words.csv                   ← List of unknown words
│   ├── unknown_words_categories.csv        ← Categories breakdown
│   ├── tokenized_summary.json              ← Token data (JSON)
│   ├── dictionary_check_results.json       ← Detailed results (JSON)
│   └── unknown_words_analysis.json         ← Analysis (JSON)
└── scripts/           # Run these scripts in order
```

### Generated Text Files (output/)

Each article from your XML becomes a separate text file:

- **Filename format:** `YYYY-MM_ArticleID.txt`
- **Example:** `1817-01_486376978.txt` = Article from January 1817
- **Content:** Plain text without XML tags or metadata

### CSV Files (for Excel)

#### 1. dictionary_results.csv

**Main results file** - one row per article with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `filename` | Text file name | `1817-01_486376978.txt` |
| `date` | Date (YYYY-MM) | `1817-01` |
| `article_id` | Unique article ID | `486376978` |
| `total_tokens` | Total words in article | `410` |
| `found_count` | Words found in dictionary | `259` |
| `not_found_count` | Words NOT in dictionary | `151` |
| `unique_found` | Unique valid words | `132` |
| `unique_not_found` | Unique unknown words | `133` |
| `found_percentage` | % of words found | `63.17` |
| `not_found_words` | List of unknown words | `(; ); --; 11; ad; ...` |

#### 2. dictionary_results_summary.csv

**Quick overview:**

```
Metric,Value
Total Files,1861
Total Tokens,1131086
Tokens Found in Dictionary,869449
Tokens Not Found,261637
Found Percentage,76.87%
Unique Unknown Words,60364
```

#### 3. unknown_words.csv

**Every unknown word with its category:**

| word | category |
|------|----------|
| aac | potential_misspellings |
| 1817 | numbers |
| ! | punctuation |
| abbey-church | hyphenated |

#### 4. unknown_words_categories.csv

**Summary by category:**

| Category | Count |
|----------|-------|
| Potential Misspellings | 50,356 |
| Hyphenated | 12,364 |
| Numbers | 1,747 |
| Mixed Alphanumeric | 549 |
| Punctuation | 11 |

## 📈 Viewing Results in Excel

### Option 1: Quick View

1. Navigate to the `data/` folder
2. Double-click `dictionary_results_summary.csv`
3. View overall statistics

### Option 2: Detailed Analysis

1. Open Excel
2. Go to **File → Open**
3. Navigate to `data/dictionary_results.csv`
4. Click **Open**

**Useful Excel features:**

- **Sort by found_percentage:** See which articles have most/least dictionary matches
- **Filter not_found_words:** Find specific unknown words
- **Create pivot tables:** Analyze by date, article quality, etc.
- **Search:** Press Ctrl+F to find specific articles or words

### Option 3: Unknown Words Analysis

1. Open `data/unknown_words.csv` in Excel
2. Use AutoFilter (Data → Filter) to:
   - Show only `potential_misspellings` category
   - Find specific word patterns
   - Sort alphabetically

## 🗂️ Project Structure

```
lexical-checker/
│
├── README.md                    ← You are here!
├── requirements.txt             ← Python dependencies
├── SANITY_CHECK_REPORT.md      ← Code quality report
│
├── docs/                        ← PUT YOUR XML FILES HERE
│   └── 40282.xml               ← Example XML file
│
├── data/                        ← Results appear here
│   ├── dictionary.db           ← English dictionary (SQLite)
│   ├── *.csv                   ← Excel-ready results
│   └── *.json                  ← Detailed JSON data
│
├── output/                      ← Extracted text files
│   ├── 1817-01_486376978.txt
│   ├── 1817-01_486382965.txt
│   └── ... (1,861 files)
│
├── scripts/                     ← RUN THESE SCRIPTS
│   ├── test_parse.py           ← Step 1: Parse XML
│   ├── tokenize_files.py       ← Step 2: Tokenize
│   ├── check_dictionary.py     ← Step 3: Validate
│   ├── export_to_csv.py        ← Step 4: Export to Excel
│   └── sanity_check.py         ← Verify everything works
│
└── src/                         ← Core modules (advanced users)
    ├── xml_parser.py           ← XML parsing logic
    ├── tokenizer.py            ← Tokenization logic
    └── dictionary_checker.py   ← Dictionary validation logic
```

## 📊 Statistics

Example processing results from sample dataset:

- **Input:** 1 XML file (40282.xml)
- **Output:** 1,861 text files
- **Total tokens:** 1,131,086 words
- **Unique tokens:** 99,305 different words
- **Dictionary matches:** 76.87% (869,449 tokens found)
- **Unknown words:** 60,364 unique unknown tokens
- **Processing time:** ~30 seconds total

### Unknown Word Breakdown

| Category | Count | Percentage |
|----------|-------|------------|
| Potential Misspellings | 46,720 | 77.4% |
| Hyphenated Words | 7,498 | 12.4% |
| Other Tokens | 3,972 | 6.6% |
| Numbers | 1,747 | 2.9% |
| Mixed Alphanumeric | 414 | 0.7% |
| Punctuation | 11 | 0.0% |
| Contractions | 2 | 0.0% |

## 🔧 Troubleshooting

### "No module named 'lxml'" or "No module named 'nltk'"

**Solution:** Install dependencies:

```powershell
pip install -r requirements.txt
```

### "No XML files found in docs directory"

**Solution:** Place your XML files in the `docs/` folder first.

### "Permission denied" when activating virtual environment

**Solution:** Run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### "Python is not recognized as a command"

**Solution:** 
1. Install Python from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"

### CSV files show weird characters in Excel

**Solution:** 
1. Open Excel first (don't double-click CSV)
2. Go to **Data → Get Data → From Text/CSV**
3. Select your CSV file
4. Choose **UTF-8** encoding
5. Click **Load**

### Script runs but no output files

**Solution:** Run the sanity check:

```powershell
python .\scripts\sanity_check.py
```

This will verify all files and show what's missing.

## 🤝 Need Help?

If you encounter issues:

1. Run the sanity check: `python .\scripts\sanity_check.py`
2. Check `SANITY_CHECK_REPORT.md` for system status
3. Verify your XML files are in `docs/` folder
4. Ensure all dependencies are installed

## 📝 License

This project is for academic and research purposes.
