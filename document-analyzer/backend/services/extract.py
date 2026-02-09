"""Document extraction utilities for PDFs and Excel files."""

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber


def _clean_text(value: str) -> str:
    """Normalize whitespace while preserving line breaks."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text page-by-page from a PDF file and return cleaned text."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Unsupported file type. Expected a PDF file.")

    try:
        pages_text: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                raw_text = page.extract_text() or ""
                cleaned_text = _clean_text(raw_text)
                if cleaned_text:
                    pages_text.append(f"--- Page {page_number} ---\n{cleaned_text}")

        return "\n\n".join(pages_text)
    except Exception as exc:
        raise RuntimeError(f"Unable to extract PDF text: {exc}") from exc


def extract_tables_from_pdf(file_path: str) -> list[pd.DataFrame]:
    """Extract tables from a PDF file and return them as DataFrames."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Unsupported file type. Expected a PDF file.")

    tables: list[pd.DataFrame] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables() or []
                for table in page_tables:
                    if not table:
                        continue

                    header = table[0] if table else []
                    rows = table[1:] if len(table) > 1 else []

                    if header and any(cell is not None and str(cell).strip() for cell in header):
                        normalized_columns = [
                            str(cell).strip() if cell is not None and str(cell).strip() else f"column_{index + 1}"
                            for index, cell in enumerate(header)
                        ]
                        frame = pd.DataFrame(rows, columns=normalized_columns)
                    else:
                        frame = pd.DataFrame(rows)

                    frame = frame.replace({r"^\s*$": None}, regex=True)
                    if not frame.empty:
                        tables.append(frame)

        return tables
    except Exception as exc:
        raise RuntimeError(f"Unable to extract PDF tables: {exc}") from exc


def extract_data_from_excel(file_path: str) -> dict[str, dict[str, Any]]:
    """Extract workbook sheets and return a verified summary per sheet."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError("Unsupported file type. Expected .xlsx or .xls.")

    try:
        sheets = pd.read_excel(path, sheet_name=None)
        results: dict[str, dict[str, Any]] = {}

        for sheet_name, frame in sheets.items():
            numeric_columns = frame.select_dtypes(include=["number"]).columns.tolist()
            categorical_columns = [column for column in frame.columns.tolist() if column not in numeric_columns]

            results[sheet_name] = {
                "rows": int(len(frame)),
                "columns": frame.columns.tolist(),
                "preview": frame.head(5).where(frame.notna(), None).to_dict(orient="records"),
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
            }

        return results
    except Exception as exc:
        raise RuntimeError(f"Unable to extract Excel data: {exc}") from exc
