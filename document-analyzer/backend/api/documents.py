"""Document API routes."""

from fastapi import APIRouter, HTTPException, Query

from backend.services.extract import (
    extract_data_from_excel,
    extract_tables_from_pdf,
    extract_text_from_pdf,
)
from backend.utils import extract_extension, resolve_data_file

router = APIRouter()


@router.get("/summary")
def get_document_summary(filename: str = Query(..., min_length=1)) -> dict[str, str]:
    """Return a placeholder summary response for the given filename."""
    _ = filename
    return {"summary": "Document summary will be generated here."}


def _raise_http_from_exception(exc: Exception) -> None:
    """Translate extraction exceptions into user-friendly HTTP errors."""
    if isinstance(exc, (FileNotFoundError, ValueError)):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/extract/text")
def extract_text(filename: str = Query(..., min_length=1)) -> dict[str, str | int]:
    """Return extracted text metadata for a PDF file."""
    file_path = resolve_data_file(filename)
    if extract_extension(file_path.name) != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type for text extraction. Please provide a PDF file.",
        )

    try:
        extracted_text = extract_text_from_pdf(str(file_path))
    except Exception as exc:
        _raise_http_from_exception(exc)

    return {
        "filename": file_path.name,
        "character_count": len(extracted_text),
        "preview": extracted_text[:1000],
    }


@router.get("/extract/tables")
def extract_tables(filename: str = Query(..., min_length=1)) -> dict[str, object]:
    """Return extracted table metadata for a PDF file."""
    file_path = resolve_data_file(filename)
    if extract_extension(file_path.name) != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type for table extraction. Please provide a PDF file.",
        )

    try:
        tables = extract_tables_from_pdf(str(file_path))
    except Exception as exc:
        _raise_http_from_exception(exc)

    return {
        "table_count": len(tables),
        "tables": [
            {
                "rows": int(table.shape[0]),
                "columns": [str(column) for column in table.columns.tolist()],
            }
            for table in tables
        ],
    }


@router.get("/extract/excel")
def extract_excel(filename: str = Query(..., min_length=1)) -> dict[str, dict[str, object]]:
    """Return extracted sheet metadata for an Excel file."""
    file_path = resolve_data_file(filename)
    if extract_extension(file_path.name) not in {".xlsx", ".xls"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type for Excel extraction. Please provide .xlsx or .xls.",
        )

    try:
        sheets = extract_data_from_excel(str(file_path))
    except Exception as exc:
        _raise_http_from_exception(exc)

    return {
        "sheets": {
            sheet_name: {
                "rows": details["rows"],
                "columns": details["columns"],
                "preview": details["preview"],
            }
            for sheet_name, details in sheets.items()
        }
    }
