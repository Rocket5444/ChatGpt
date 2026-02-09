"""Streamlit frontend for AI Document Analyzer phase 2."""

import requests
import streamlit as st

BACKEND_BASE_URL = "http://localhost:8000"

st.title("AI Document Analyzer")

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "xlsx", "xls", "docx"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        upload_response = requests.post(f"{BACKEND_BASE_URL}/upload", files=files, timeout=30)
        upload_response.raise_for_status()
        upload_payload = upload_response.json()
        uploaded_name = upload_payload.get("filename", uploaded_file.name)

        if uploaded_name not in st.session_state["uploaded_files"]:
            st.session_state["uploaded_files"].append(uploaded_name)

        st.session_state["uploaded_filename"] = uploaded_name
        st.success(f"Uploaded: {uploaded_name}")
    except requests.RequestException as exc:
        st.error(f"Upload failed: {exc}")

if st.button("Summarize Document"):
    filename = st.session_state.get("uploaded_filename")
    if not filename:
        st.warning("Please upload a file first.")
    else:
        try:
            summary_response = requests.get(
                f"{BACKEND_BASE_URL}/summary",
                params={"filename": filename},
                timeout=30,
            )
            summary_response.raise_for_status()
            summary_payload = summary_response.json()
            st.subheader("Summary")
            st.write(summary_payload.get("summary", "No summary available."))
        except requests.RequestException as exc:
            st.error(f"Failed to fetch summary: {exc}")

st.header("Phase-2: Extraction Verification")

available_files = st.session_state.get("uploaded_files", [])
selected_file = st.selectbox("Select uploaded file", options=available_files) if available_files else None
extraction_type = st.radio("Choose extraction type", options=["Text", "Tables", "Excel"], horizontal=True)

if st.button("Run Extraction Verification"):
    if not selected_file:
        st.warning("Please upload and select a file first.")
    else:
        try:
            endpoint_map = {
                "Text": "/extract/text",
                "Tables": "/extract/tables",
                "Excel": "/extract/excel",
            }
            response = requests.get(
                f"{BACKEND_BASE_URL}{endpoint_map[extraction_type]}",
                params={"filename": selected_file},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()

            if extraction_type == "Text":
                st.subheader("Text Preview")
                st.write(f"Character Count: {payload.get('character_count', 0)}")
                st.text_area("Extracted Text (first 1000 chars)", payload.get("preview", ""), height=300)
            elif extraction_type == "Tables":
                st.subheader("Table Metadata")
                st.write(f"Detected Tables: {payload.get('table_count', 0)}")
                st.json(payload.get("tables", []))
            else:
                st.subheader("Excel Sheet Structure")
                st.json(payload.get("sheets", {}))

        except requests.HTTPError:
            error_detail = "Unexpected server error."
            try:
                error_detail = response.json().get("detail", error_detail)
            except Exception:
                error_detail = response.text or error_detail
            st.error(f"Extraction failed: {error_detail}")
        except requests.RequestException as exc:
            st.error(f"Failed to connect to backend: {exc}")
