"""Shared backend utility helpers."""

from pathlib import Path

from fastapi import HTTPException

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def resolve_data_file(filename: str) -> Path:
    """Resolve and validate a file path inside the project's data directory.

    Args:
        filename: Name of the file saved in the data directory.

    Returns:
        A validated absolute path to the file.

    Raises:
        HTTPException: If filename is invalid or file does not exist.
    """
    cleaned_name = Path(filename).name
    if not cleaned_name:
        raise HTTPException(status_code=400, detail="Filename is required.")

    file_path = DATA_DIR / cleaned_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {cleaned_name}")

    return file_path


def extract_extension(filename: str) -> str:
    """Return lower-cased file extension including leading dot."""
    return Path(filename).suffix.lower()
