import csv
import os
import re
import hashlib
from collections import defaultdict
from pathlib import Path
from text_utils import text_clean, extract_text


def hash_text(text):
    """
    Generates a SHA256 hash based on the content of a text string.

    This is used for 'semantic' deduplication, where the text content matters
    more than the file container (e.g., a .docx and .pdf with the same words).

    Args:
        text (str): The text content to hash.

    Returns:
        str: A hexadecimal string representing the SHA256 hash.
    """
    clean = text_clean(text)
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


def hash_binary(path, block_size=65536):
    """
    Generates a SHA256 hash based on the binary file content (bit-for-bit).

    Used as a fallback when text extraction fails or is not applicable
    (e.g., images, executables, or scanned PDFs without OCR).

    Args:
        path (str): The file path to read.
        block_size (int, optional): The chunk size in bytes for reading the file.
                                    Defaults to 64KB (65536).

    Returns:
        str | None: The hex digest of the hash, or None if the file could not be read.
    """
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
    Orchestrates the hashing strategy for a single file.

    Implements a hybrid strategy:
    1. Attempt Semantic Hashing: Try to extract text. If successful, hash the
       cleaned text. This allows detecting duplicates across different formats
       (e.g., PDF vs DOCX).
    2. Fallback to Binary Hashing: If text extraction fails (unsupported format
       or parse error), hash the raw file bytes.

    Args:
        path (str): The location of the file to hash.

    Returns:
        str: The computed hash digest.
    """
    print(f"Scanning: {path}")  # Moved print here to see progress
    text = extract_text(path)

    if text is not None:
        # It's a supported text document (PDF/DOCX/TXT)
        return hash_text(text)

    # Fallback: It's a binary file or an unreadable PDF
    return hash_binary(path)


def crawl_directory(root_path):
    """
    Recursively iterates over a directory tree yielding file paths.

    Args:
        root_path (str): The starting directory path.

    Yields:
        Path: A Path object for every file found within the root_path
              and its subdirectories.
    """
    root = Path(root_path)
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            yield Path(dirpath) / name


def find_duplicates(root_paths):
    """
    Scans directories and identifies files that share the same hash.

    Args:
        root_paths (str | list): A single directory path or a list of directory paths
                                 to scan.

    Returns:
        dict: A dictionary where:
            - Key: The file hash (str).
            - Value: A list of file paths (list[str]) associated with that hash.
            Only entries with >1 file path (duplicates) are returned.
    """
    hash_map = defaultdict(list)
    # if single path is supplied
    if isinstance(root_paths, (str, Path)):
        root_paths = [root_paths]

    for rpath in root_paths:
        for file_path in crawl_directory(rpath):
            file_hash = hash_file(str(file_path))
            if file_hash:
                hash_map[file_hash].append(str(file_path))

    # Filter for hashes that appear more than once
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def save_to_csv(data: dict, filename="duplicate_report.csv"):
    """
    Exports the identified duplicates to a CSV file.

    Args:
        data (dict): The dictionary of duplicates returned by find_duplicates.
        filename (str, optional): The intended filename for the report.
                                  Note: Current implementation writes to '../output.csv'.

    Side Effects:
        Writes a file to the disk at '../output.csv'.
        Prints success or error messages to stdout.
    """
    try:
        with open("../output.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["key", "value"])
            for key, value in data.items():
                writer.writerow([key, value])

        print(f"\n[SUCCESS] Report saved to: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"\n[ERROR] Could not save CSV: {e}")


def main(mounted_drive):
    """
    Main entry point for the script.

    Sets the target directory, initiates the scan, prints results to console,
    and saves the CSV report.
    """
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
