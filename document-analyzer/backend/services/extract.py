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
    """Extract cleaned text from a PDF file page by page.

    Args:
        file_path: Path to a PDF file.

    Returns:
        A single cleaned string containing extracted text from all pages.

    Raises:
        FileNotFoundError: If the target file does not exist.
        ValueError: If the input is not a PDF file.
        RuntimeError: If the PDF cannot be opened or parsed.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Unsupported file type. Expected a PDF file.")

    try:
        pages_text: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                cleaned = _clean_text(page.extract_text() or "")
                if cleaned:
                    pages_text.append(f"--- Page {page_number} ---\n{cleaned}")
        return "\n\n".join(pages_text)
    except Exception as exc:
        raise RuntimeError(f"Unable to extract text from '{path.name}': {exc}") from exc


def extract_tables_from_pdf(file_path: str) -> list[pd.DataFrame]:
    """Extract non-empty tables from a PDF file.

    Args:
        file_path: Path to a PDF file.

    Returns:
        A list of pandas DataFrames. Returns an empty list if no tables are found.

    Raises:
        FileNotFoundError: If the target file does not exist.
        ValueError: If the input is not a PDF file.
        RuntimeError: If the PDF cannot be opened or parsed.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Unsupported file type. Expected a PDF file.")

    tables: list[pd.DataFrame] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for raw_table in page.extract_tables() or []:
                    if not raw_table:
                        continue

                    header = raw_table[0] if raw_table else []
                    rows = raw_table[1:] if len(raw_table) > 1 else []

                    if header and any(cell is not None and str(cell).strip() for cell in header):
                        columns = [
                            str(cell).strip() if cell is not None and str(cell).strip() else f"column_{i + 1}"
                            for i, cell in enumerate(header)
                        ]
                        df = pd.DataFrame(rows, columns=columns)
                    else:
                        df = pd.DataFrame(raw_table)

                    df = df.replace({r"^\s*$": None}, regex=True)
                    df = df.dropna(how="all").dropna(axis=1, how="all")
                    if not df.empty:
                        tables.append(df)

        return tables
    except Exception as exc:
        raise RuntimeError(f"Unable to extract tables from '{path.name}': {exc}") from exc


def extract_data_from_excel(file_path: str) -> dict[str, dict[str, Any]]:
    """Extract all sheets from an Excel workbook with verification metadata.

    Args:
        file_path: Path to an Excel file.

    Returns:
        A dictionary keyed by sheet name containing:
        - rows: number of rows
        - columns: list of column names
        - preview: first 5 rows as list of dictionaries

    Raises:
        FileNotFoundError: If the target file does not exist.
        ValueError: If the input is not an Excel file.
        RuntimeError: If the workbook cannot be opened or parsed.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError("Unsupported file type. Expected .xlsx or .xls.")

    try:
        workbook = pd.read_excel(path, sheet_name=None)
        output: dict[str, dict[str, Any]] = {}

        for sheet_name, dataframe in workbook.items():
            output[sheet_name] = {
                "rows": int(len(dataframe)),
                "columns": [str(column) for column in dataframe.columns.tolist()],
                "preview": dataframe.head(5).where(dataframe.notna(), None).to_dict(orient="records"),
            }

        return output
    except Exception as exc:
        raise RuntimeError(f"Unable to extract Excel data from '{path.name}': {exc}") from exc
