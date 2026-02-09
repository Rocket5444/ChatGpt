# AI Document Analyzer (Phase 1)

## Project description
This project is a zero-budget, locally deployable AI Document Analyzer foundation.
Phase 1 includes:
- FastAPI backend with upload and summary placeholder endpoints
- Document extraction utilities for PDF text/tables and Excel data
- Streamlit frontend for upload and summary interaction
- Local-only setup with open-source dependencies

## Installation steps
1. Ensure Python 3.10+ is installed.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to run backend
From the `document-analyzer` directory:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## How to run frontend
From the `document-analyzer` directory (in a second terminal):
```bash
streamlit run frontend/app.py
```

## Sample usage steps
1. Start the backend server.
2. Start the Streamlit frontend.
3. Open the Streamlit URL shown in terminal (typically `http://localhost:8501`).
4. Upload a document (`.pdf`, `.xlsx`, `.xls`, or `.docx`).
5. Click **Summarize Document**.
6. View the placeholder summary response.
