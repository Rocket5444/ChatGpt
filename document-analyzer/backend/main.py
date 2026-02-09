"""Main FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.documents import router as documents_router
from backend.api.upload import router as upload_router

app = FastAPI(title="Document Analyzer API", version="0.1.0")

# Allow all origins for local development in phase 1.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, tags=["upload"])
app.include_router(documents_router, tags=["documents"])


@app.get("/health")
def health() -> dict[str, str]:
    """Health-check endpoint."""
    return {"status": "ok"}
