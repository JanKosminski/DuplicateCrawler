import hashlib
import os
import csv
from collections import defaultdict
import numpy as np
from pathlib import Path

# Scikit-learn imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Utils imports
from text_utils import extract_text, text_clean

def hash_binary(path, block_size=65536):
    """Hashes the file bit-for-bit."""
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                sha.update(block)
    except Exception as e:
        print(f"[WARNING] Could not read binary file {path}: {e}")
        return None
    return sha.hexdigest()


def scan_paths(root_paths):
    """
    Generator that recursively walks through one or multiple root directories.

    Args:
        root_paths (str | Path | list): A single path or a list of paths to scan.

    Yields:
        Path: Path objects for every file found.
    """
    # Encapsulate single item to list.
    if isinstance(root_paths, (str, Path)):
        root_paths = [root_paths]

    for root in root_paths:
        print(f"Scanning directory: {root}")
        path_obj = Path(root)

        # Check if path exists to avoid crashing on invalid drives
        if not path_obj.exists():
            print(f"[WARNING] Path not found: {root}")
            continue

        for dirpath, _, filenames in os.walk(path_obj):
            for name in filenames:
                yield Path(dirpath) / name


def load_documents(root_paths):
    """
    Aggregates files from multiple locations and separates them into
    text-processable and binary categories.

    Args:
        root_paths (str | list): The directory or directories to process.

    Returns:
        tuple: (text_file_paths, documents, binary_file_paths)
    """
    text_file_paths = []
    documents = []
    binary_file_paths = []

    # Iterating over the generator function to get a flat stream of files
    for path in scan_paths(root_paths):
        print(f"Attempting to load {path}")
        if path.suffix.lower() in ['.txt', '.pdf', '.docx']:
            raw_text = extract_text(str(path))
            if raw_text:
                cleaned = text_clean(raw_text)
                # Filter out empty or very short files (likely not meaningful content)
                if len(cleaned) > 50:
                    text_file_paths.append(str(path))
                    documents.append(cleaned)
                else:
                    pass
            else:
                #fallback in case text is corrupted
                binary_file_paths.append(str(path))
        else:
            # Add non-text files to binary list for standard hashing
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


def main(mounted_drive = "C:/Users"):
    # Update this path to your actual directory or list of directories


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