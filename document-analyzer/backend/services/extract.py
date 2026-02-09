"""Document extraction utilities for PDFs and Excel files."""

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber


def _clean_text(value: str) -> str:
    """Normalize whitespace while preserving logical line breaks."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract and clean page-by-page text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        A single cleaned text string containing all page text joined with separators.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If file extension is not PDF.
        RuntimeError: If the PDF is unreadable or extraction fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Unsupported file type. Expected a PDF file.")

    try:
        pages_text: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = _clean_text(page.extract_text() or "")
                if page_text:
                    pages_text.append(f"--- Page {page_number} ---\n{page_text}")

        return "\n\n".join(pages_text)
    except Exception as exc:
        raise RuntimeError(f"Unable to read PDF text from '{path.name}': {exc}") from exc


def extract_tables_from_pdf(file_path: str) -> list[pd.DataFrame]:
    """Extract tables from a PDF and return non-empty DataFrames.

    Args:
        file_path: Path to the PDF file.

    Returns:
        List of table DataFrames. Returns an empty list when no tables are detected.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If file extension is not PDF.
        RuntimeError: If PDF parsing fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Unsupported file type. Expected a PDF file.")

    output: list[pd.DataFrame] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    if not table:
                        continue

                    dataframe = pd.DataFrame(table)
                    dataframe = dataframe.replace({r"^\s*$": None}, regex=True)
                    dataframe = dataframe.dropna(how="all").dropna(axis=1, how="all")

                    if not dataframe.empty:
                        output.append(dataframe)
        return output
    except Exception as exc:
        raise RuntimeError(f"Unable to read PDF tables from '{path.name}': {exc}") from exc


def extract_data_from_excel(file_path: str) -> dict[str, dict[str, Any]]:
    """Extract all Excel sheets and return verification metadata.

    Args:
        file_path: Path to the Excel workbook.

    Returns:
        Structured dictionary with per-sheet rows, columns, and first-5-row preview.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If file extension is not .xlsx or .xls.
        RuntimeError: If workbook parsing fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError("Unsupported file type. Expected .xlsx or .xls.")

    try:
        workbook = pd.read_excel(path, sheet_name=None)
        extracted: dict[str, dict[str, Any]] = {}

        for sheet_name, dataframe in workbook.items():
            extracted[sheet_name] = {
                "rows": int(len(dataframe)),
                "columns": [str(column) for column in dataframe.columns.tolist()],
                "preview": dataframe.head(5).where(dataframe.notna(), None).to_dict(orient="records"),
            }

        return extracted
    except Exception as exc:
        raise RuntimeError(f"Unable to read Excel data from '{path.name}': {exc}") from exc
