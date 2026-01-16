import hashlib
import os
import csv
import re
from collections import defaultdict
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


def hash_binary(path, block_size=65536):
    """Hashes the file bit-for-bit."""
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                sha.update(block)
    except Exception as e:
        print(f"[WARN] Could not read binary file {path}: {e}")
        return None
    return sha.hexdigest()


def load_documents(root_path):
    """Separates files into text-processable and binary paths."""
    text_file_paths = []
    documents = []
    binary_file_paths = []

    print(f"Scanning directory: {root_path}")
    root = Path(root_path)

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name

            # Check extension to decide handling
            if path.suffix.lower() in ['.txt', '.pdf', '.docx']:
                raw_text = extract_text(str(path))
                if raw_text:
                    cleaned = text_clean(raw_text)
                    if len(cleaned) > 50:
                        text_file_paths.append(str(path))
                        documents.append(cleaned)
                    else:
                        # Text was too short or empty, treat as binary/ignore or log
                        pass
            else:
                # Add to binary list for hashing
                binary_file_paths.append(str(path))

    return text_file_paths, documents, binary_file_paths


def find_duplicates_tfidf(paths, documents, threshold=0.90):
    """Compares text content using TF-IDF."""
    n_files = len(documents)
    if n_files < 2:
        print("Not enough text files found to compare via TF-IDF.")
        return []

    print(f"Vectorizing {n_files} text documents...")
    vectorizer = TfidfVectorizer(stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(documents)

    print("Calculating Cosine Similarity...")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    print(f"Filtering text results > {threshold * 100}%...")
    duplicates = []
    rows, cols = np.where(cosine_sim > threshold)

    for r, c in zip(rows, cols):
        if r < c:
            sim_score = cosine_sim[r, c]
            duplicates.append((paths[r], paths[c], sim_score))

    return duplicates


def find_duplicates_binary(paths):
    """Compares non-text files using SHA256 hashing."""
    if not paths:
        print("No binary files to hash.")
        return []

    print(f"Hashing {len(paths)} binary files...")
    hash_map = defaultdict(list)
    results = []

    for p in paths:
        file_hash = hash_binary(p)
        if file_hash:
            hash_map[file_hash].append(p)

    # Find collisions (identical hashes)
    for _, files in hash_map.items():
        if len(files) > 1:
            # Generate pairs for all identical files
            for i in range(len(files)):
                for j in range(i + 1, len(files)):
                    # Score is 1.0 because hashes are identical
                    results.append((files[i], files[j], 1.0))

    return results


def save_to_csv(results, filename="duplicate_report.csv"):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Similarity Score", "File A", "File B"])
            for file_a, file_b, score in results:
                writer.writerow([f"{score:.4f}", file_a, file_b])
        print(f"\n[SUCCESS] Report saved to: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"\n[ERROR] Could not save CSV: {e}")


def main():
    # Update this path to your actual directory
    mounted_drive = "C:/Users/janko/Downloads"

    # 1. Load and sort files
    text_paths, docs, binary_paths = load_documents(mounted_drive)

    all_results = []

    # 2. Process Text Files (TF-IDF)
    if text_paths:
        text_results = find_duplicates_tfidf(text_paths, docs, threshold=0.90)
        all_results.extend(text_results)

    # 3. Process Binary Files (Hashing)
    if binary_paths:
        binary_results = find_duplicates_binary(binary_paths)
        all_results.extend(binary_results)

    if not all_results:
        print("\nNo duplicates found.")
        return

    # 4. Sort by score (Highest first)
    all_results.sort(key=lambda x: x[2], reverse=True)

    # 5. Print to console
    print(f"\nFound {len(all_results)} pairs. Showing top 5:")
    for file_a, file_b, score in all_results[:5]:
        print(f"[{score:.1%}] {os.path.basename(file_a)} <-> {os.path.basename(file_b)}")

    # 6. Save to CSV
    save_to_csv(all_results)


if __name__ == "__main__":
    main()