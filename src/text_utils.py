from pdfminer.high_level import extract_text as pdf_text
from docx import Document
from pdfminer.pdfdocument import PDFNoValidXRef
from pdfminer.pdfparser import PDFSyntaxError
import unicodedata
import re


def extract_text(path):
    """
    Identifies the file type by extension and attempts to extract its raw text content.

    This function acts as a wrapper for specific file handlers (PDFMiner, python-docx).
    It is designed to fail silently for corrupt files to allow the scanning process
    to continue uninterrupted.

    Args:
        path (str | Path): The file path to process.

    Returns:
        str | None: The extracted text string if successful. Returns None if:
            - The file extension is not supported (.txt, .pdf, .docx).
            - The file is corrupt or unreadable.
            - An exception occurs during parsing.
    """
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
    except Exception as e:
        print(f"[WARNING] Failed to extract {path_str}: {e}")
        return None


def text_clean(text_data: str) -> str:
    """
        Normalizes raw text data to facilitate fuzzy matching.

        This removes formatting differences that shouldn't count as "unique" content,
        such as capitalization, variable whitespace, or specific Unicode representations.

        Args:
            text_data (str): The raw input string.

        Returns:
            str: The normalized string. Returns an empty string if input is None or empty.

        Transformations:
            1. Unicode Normalization (NFKD): Decomposes characters (e.g., splits accented
               characters into base char + combining diacritic).
            2. Lowercasing: Converts all characters to lowercase.
            3. Whitespace Collapsing: Converts tabs, newlines, and multi-spaces into
               a single space character.
        """
    if not text_data:
        return ""
    text_data = unicodedata.normalize("NFKD", text_data)
    text_data = text_data.lower()
    text_data = re.sub(r"\s+", " ", text_data)
    return text_data.strip()