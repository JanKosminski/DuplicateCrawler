
# Content-Aware Duplicate File Detector

This project provides a suite of tools to detect duplicate files within a directory tree. Unlike standard duplicate finders that only look for exact bit-for-bit matches, this toolkit includes **Natural Language Processing (NLP)** techniques to find documents that are similar in content (e.g., drafts, minor edits) even if the file sizes or formats differ.

## Project Structure

This repository contains distinct scripts to handle different duplicate detection needs, now accessible via a Graphical User Interface (GUI).

1.  **`main.py` (Main Entry Point)**
    * **Description:** A user-friendly Tkinter interface.
    * **Features:** Allows you to select multiple directories to scan simultaneously and choose between the processing modes below without modifying code.

2.  **`mixed.py` (Recommended Backend)**
    * **Logic:** Combines both methods below. It automatically detects file types.
    * **Text files (.txt, .pdf, .docx):** Analyzed via TF-IDF to find content similarity (e.g., "90% similar").
    * **Binary files (Images, Zips, Exes, etc.):** Analyzed via SHA256 Hashing for exact matches.
    * **Best for:** General cleanup of download folders or mixed archives.

3.  **`tfidf.py`**
    * **Logic:** Purely text analysis. Ignores non-text files.
    * **Best for:** Cleaning up document libraries, finding plagiarized text, or consolidating versioned drafts of papers.

4.  **`binary_hashing.py`**
    * **Logic:** Purely cryptographic hashing (SHA256).
    * **Best for:** Finding exact duplicates of images, videos, installers, or backups. Fast and 100% accurate for exact copies.

5.  **`text_utils.py`**
    * **Description:** Helper module handling text extraction (PDF/DOCX/TXT) and text cleaning/normalization.

---

## Prerequisites

You need Python 3.8+ and the following external libraries.

### Installation

Run the following command to install the required dependencies:

```bash
pip install -r requirements.txt
# or manually:
pip install scikit-learn numpy pdfminer.six python-docx

```

* **tkinter:** Usually included with Python, required for the GUI.
* **scikit-learn:** For TfidfVectorizer and Cosine Similarity.
* **pdfminer.six:** For extracting text from `.pdf` files.
* **python-docx:** For extracting text from `.docx` files.
* **numpy:** For matrix operations.

---

## Usage

You can run the tool using the new GUI or via the command line.

### Method 1: Using the GUI (Recommended)

1. Run the interface script:
```bash
python gui.py

```


2. **Add Directories:** Click "Add Directories" to select one or multiple folders you want to scan.
3. **Select Mode:** Choose your scan strategy:
* *Pure Hashing:* Exact duplicates only.
* *Text analysis (NLP) + Binary Hashing:* The hybrid approach (Recommended).
* *Text analysis (NLP text only):* Ignores images/binaries, focuses on documents.


4. **Process:** Click "Process Directories".
5. **Results:** A popup will confirm completion. Check the console for a summary and the generated CSV for details.

### Method 2: Command Line (Headless)

If you prefer running the scripts directly or integrating them into a pipeline, you can still run the individual scripts.

1. Open the specific script (e.g., `mixed.py`) and locate the `main()` function.
2. Update the `mounted_drive` variable to your target path:
```python
#def main(mounted_drive = "C:/path/to/your/folder"):

```


3. Run the script:
```bash
python mixed.py

```



---

## How It Works

### Text Analysis (TF-IDF)

*Used for `.txt`, `.pdf`, and `.docx`.*

1. **Extraction:** Text is pulled from files using `text_utils.py`.
2. **Normalization:** Formatting, capitalization, and whitespace are normalized.
3. **Vectorization:** The code converts text into numerical vectors using **TF-IDF** (Term Frequency-Inverse Document Frequency).
4. **Similarity:** It calculates the **Cosine Similarity** between vectors.
* *Score 1.0:* Identical text.
* *Score 0.9:* Highly similar (likely a minor revision).



### Binary Analysis (Hashing)

*Used for all other file extensions or when text extraction fails.*

1. **Read:** Reads the file in binary mode (64KB chunks).
2. **Hash:** Generates a **SHA256** signature.
3. **Compare:** If two files have the same hash, they are 100% identical byte-for-byte.

---

## ⚙ Configuration

You can tweak the sensitivity of the text matching in `mixed.py` or `tfidf.py`:

```python
# In main() or find_duplicates_tfidf():
# threshold=0.90 means files must be 90% similar to be reported.
# Lower this to 0.80 to find looser matches.
#text_results = find_duplicates_tfidf(text_paths, docs, threshold=0.90)

```

---

## Output Format

The `duplicate_report.csv` contains the following columns:

| Similarity Score | File A | File B |
| --- | --- | --- |
| 1.0000 | `C:/.../image_copy.png` | `C:/.../image_original.png` |
| 0.9452 | `C:/.../Draft_v1.docx` | `C:/.../Final_Report.docx` |

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this code as you wish.

```