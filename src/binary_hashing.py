import csv
import os
import re
import hashlib
from collections import defaultdict
from pathlib import Path
import unicodedata

# Library imports
from pdfminer.high_level import extract_text as pdf_text
from docx import Document
from pdfminer.pdfdocument import PDFNoValidXRef
from pdfminer.pdfparser import PDFSyntaxError


def extract_text(path):
    """
    Determines file type by extension and extracts text content.
    Returns None if the file is not a supported text format or fails to read.
    """
    path_str = str(path)
    try:
        if path_str.endswith(".txt"):
            with open(path_str, "r", errors="ignore", encoding="utf-8") as f:
                return f.read()
        if path_str.endswith(".pdf"):
            try:
                # Disable logging/print inside pdfminer to keep console clean
                return pdf_text(path_str)
            except (PDFSyntaxError, PDFNoValidXRef, Exception):
                # Fail silently or log to a file in production
                return None
        if path_str.endswith(".docx"):
            doc = Document(path_str)
            return "\n".join(p.text for p in doc.paragraphs)

        return None
    except Exception as e:
        print(f"[WARN] Failed to extract {path_str}: {e}")
        return None


def text_clean(text_data: str) -> str:
    if not text_data:
        return ""
    # Normalize unicode characters
    text_data = unicodedata.normalize("NFKD", text_data)
    text_data = text_data.lower()
    # Replace all whitespace (tabs, newlines) with single space
    text_data = re.sub(r"\s+", " ", text_data)
    return text_data.strip()


def hash_text(text):
    """Hashes the cleaned text content."""
    clean = text_clean(text)
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


def hash_binary(path, block_size=65536):
    """Hashes the file bit-for-bit (fallback for non-text files)."""
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                sha.update(block)
    except Exception as e:
        print(f"[WARN] Could not read binary file {path}: {e}")
        return None
    return sha.hexdigest()


def hash_file(path):
    """
    Main hashing logic:
    1. Try to extract text.
    2. If text exists, hash the cleaned text (fuzzy match).
    3. If no text (image/zip/unknown), hash the binary content (exact match).
    """
    print(f"Scanning: {path}")  # Moved print here to see progress
    text = extract_text(path)

    if text is not None:
        # It's a supported text document (PDF/DOCX/TXT)
        return hash_text(text)

    # Fallback: It's a binary file or an unreadable PDF
    return hash_binary(path)


def crawl_directory(root_path):
    root = Path(root_path)
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            yield Path(dirpath) / name


def find_duplicates(root_path):
    hash_map = defaultdict(list)

    for file_path in crawl_directory(root_path):
        # FIX IS HERE: Pass the path, not the extracted text
        file_hash = hash_file(str(file_path))

        if file_hash:
            hash_map[file_hash].append(str(file_path))

    # Filter for hashes that appear more than once
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def save_to_csv(data :dict, filename="duplicate_report.csv"):
    """Exports the list of tuples to a CSV file."""
    try:
        with open("../output.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["key", "value"])
            for key, value in data.items():
                writer.writerow([key, value])

        print(f"\n[SUCCESS] Report saved to: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"\n[ERROR] Could not save CSV: {e}")


def main():
    # Update this path to your target directory
    mounted_drive = "C:/Users/janko/Downloads"

    if not os.path.exists(mounted_drive):
        print(f"Error: Path {mounted_drive} does not exist.")
        return

    print(f"Starting scan in: {mounted_drive}...")
    duplicates = find_duplicates(mounted_drive)

    if not duplicates:
        print("\nNo duplicates found.")
        return

    print(f"\nFound {len(duplicates)} sets of duplicates:")
    for h, paths in duplicates.items():
        print(f"\nHash: {h}")
        for p in paths:
            print(f"  - {p}")
    save_to_csv(duplicates)


if __name__ == "__main__":
    main()