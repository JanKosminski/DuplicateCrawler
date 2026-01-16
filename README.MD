# Content-Aware Duplicate File Detector

This project provides a suite of tools to detect duplicate files within a directory tree. Unlike standard duplicate finders that only look for exact bit-for-bit matches, this toolkit includes **Natural Language Processing (NLP)** techniques to find documents that are similar in content (e.g., drafts, minor edits) even if the file sizes or formats differ.

##  Project Structure

This repository contains three distinct scripts to handle different duplicate detection needs:

1. **`main.py` (Recommended)**
* **Logic:** Combines both methods below. It automatically detects file types.
* **Text files (.txt, .pdf, .docx):** Analyzed via TF-IDF to find content similarity (e.g., "90% similar").
* **Binary files (Images, Zips, Exes, etc.):** Analyzed via SHA256 Hashing for exact matches.
* **Best for:** General cleanup of download folders or mixed archives.


2. **`tfidf.py`**
* **Logic:** Purely text analysis. Ignores non-text files.
* **Best for:** Cleaning up document libraries, finding plagiarized text, or consolidating versioned drafts of papers.


3. **`binary_hashing.py`**
* **Logic:** Purely cryptographic hashing (SHA256).
* **Best for:** Finding exact duplicates of images, videos, installers, or backups. Fast and 100% accurate for exact copies.



---

##  Prerequisites

You need Python 3.8+ and the following external libraries.

### Installation

Run the following command to install the required dependencies:

```bash
pip install -r requirements.txt
or
pip install scikit-learn numpy pdfminer.six python-docx

```

* **scikit-learn:** For TfidfVectorizer and Cosine Similarity.
* **pdfminer.six:** For extracting text from `.pdf` files.
* **python-docx:** For extracting text from `.docx` files.
* **numpy:** For matrix operations.

---

##  Usage

### 1. Configure the Target Directory

Open the script you wish to run (e.g., `main_hybrid.py`) and locate the `main()` function at the bottom. Change the `mounted_drive` variable to the folder you want to scan:

```python
def main():
    # Update this path to your actual directory
    mounted_drive = "C:/Users/YourName/Documents/TargetFolder"

```

### 2. Run the Script

Execute the script via your terminal:

```bash
python main.py

```

### 3. Review Results

* **Console:** The script will print the top 5 duplicate pairs found.
* **CSV Report:** A file named `duplicate_report.csv` will be generated in the same folder as the script.

---

##  How It Works

### Text Analysis (TF-IDF)

Used for `.txt`, `.pdf`, and `.docx`.

1. **Extraction:** text is pulled from files; formatting and whitespace are normalized.
2. **Vectorization:** The code converts text into numerical vectors using **TF-IDF** (Term Frequency-Inverse Document Frequency). This highlights unique words while filtering out common words (like "the", "and").
3. **Similarity:** It calculates the **Cosine Similarity** between vectors.
* *Score 1.0:* Identical text.
* *Score 0.9:* Highly similar (likely a minor revision).



### Binary Analysis (Hashing)

Used for all other file extensions.

1. **Read:** Reads the file in binary mode.
2. **Hash:** Generates a **SHA256** signature.
3. **Compare:** If two files have the same hash, they are 100% identical byte-for-byte.

---

## ⚙ Configuration

You can tweak the sensitivity of the text matching in the `main_hybrid.py` or `tfidf_only.py` scripts:

```python
# In main():
# threshold=0.90 means files must be 90% similar to be reported.
# Lower this to 0.80 to find looser matches.
# text_results = find_duplicates_tfidf(text_paths, docs, threshold=0.90)

```

---

##  Output Format

The `duplicate_report.csv` contains the following columns:

| Similarity Score | File A | File B |
| --- | --- | --- |
| 1.0000 | `C:/.../image_copy.png` | `C:/.../image_original.png` |
| 0.9452 | `C:/.../Draft_v1.docx` | `C:/.../Final_Report.docx` |

##  License
This project is licensed under the MIT License.
You are free to use, modify, and distribute this code as you wish, provided you include the original license and attribution. Feel free to reach out or open a pull request!

