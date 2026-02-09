"""Upload API routes."""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.utils import DATA_DIR

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    """Accept a multipart file and save it into the local data directory."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file: missing filename")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = DATA_DIR / Path(file.filename).name

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Invalid file: file is empty")
        destination.write_bytes(content)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}") from exc

    return {
        "filename": destination.name,
        "file_path": str(destination),
        "status": "uploaded",
    }
