import os
import csv
import re
import unicodedata
import numpy as np
from pathlib import Path

# Scikit-learn imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Extraction imports
from pdfminer.high_level import extract_text as pdf_text
from docx import Document
from pdfminer.pdfdocument import PDFNoValidXRef
from pdfminer.pdfparser import PDFSyntaxError


def extract_text(path):
    path_str = str(path)
    try:
        if path_str.endswith(".txt"):
            with open(path_str, "r", errors="ignore", encoding="utf-8") as f:
                return f.read()
        if path_str.endswith(".pdf"):
            try:
                return pdf_text(path_str)
            except (PDFSyntaxError, PDFNoValidXRef, Exception):
                return None
        if path_str.endswith(".docx"):
            doc = Document(path_str)
            return "\n".join(p.text for p in doc.paragraphs)
        return None
    except Exception:
        return None


def text_clean(text_data: str) -> str:
    if not text_data:
        return ""
    text_data = unicodedata.normalize("NFKD", text_data)
    text_data = text_data.lower()
    text_data = re.sub(r"\s+", " ", text_data)
    return text_data.strip()


def load_documents(root_path):
    file_paths = []
    documents = []

    print(f"Scanning directory: {root_path}")
    root = Path(root_path)

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix not in ['.txt', '.pdf', '.docx']:
                continue

            raw_text = extract_text(str(path))
            if raw_text:
                cleaned = text_clean(raw_text)
                if len(cleaned) > 50:
                    file_paths.append(str(path))
                    documents.append(cleaned)

    return file_paths, documents


def find_duplicates_tfidf(root_path, threshold=0.90):
    paths, documents = load_documents(root_path)
    n_files = len(documents)

    if n_files < 2:
        print("Not enough text files found to compare.")
        return []

    print(f"Vectorizing {n_files} documents...")
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    print("Calculating Cosine Similarity...")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    print(f"Filtering results > {threshold * 100}%...")
    duplicates = []
    rows, cols = np.where(cosine_sim > threshold)

    for r, c in zip(rows, cols):
        if r < c:
            sim_score = cosine_sim[r, c]
            duplicates.append((paths[r], paths[c], sim_score))

    return duplicates


def save_to_csv(results, filename="duplicate_report.csv"):
    """Exports the list of tuples to a CSV file."""
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(["Similarity Score", "File A", "File B"])

            # Data
            for file_a, file_b, score in results:
                writer.writerow([f"{score:.4f}", file_a, file_b])

        print(f"\n[SUCCESS] Report saved to: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"\n[ERROR] Could not save CSV: {e}")


def main():
    mounted_drive = "C:/Users/janko/Downloads"

    # 1. Run the scan
    results = find_duplicates_tfidf(mounted_drive, threshold=0.90)

    if not results:
        print("\nNo duplicates found.")
        return

    # 2. Sort by score (Highest first)
    results.sort(key=lambda x: x[2], reverse=True)

    # 3. Print to console
    print(f"\nFound {len(results)} pairs. Showing top 5:")
    for file_a, file_b, score in results[:5]:
        print(f"[{score:.1%}] {os.path.basename(file_a)} <-> {os.path.basename(file_b)}")

    # 4. Save to CSV
    save_to_csv(results)


main()