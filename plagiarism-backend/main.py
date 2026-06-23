from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import uuid
import fitz

from detect import detect_plagiarism, detect_plagiarism_with_web
from db import save_result, get_history, get_result_by_id

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    mode: str = Query(default="web", description="Detection mode: 'web' for live internet scraping, 'offline' for local-only")
):
    file_bytes = await file.read()
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
    if not text.strip():
        return {"status": "error", "message": "Could not extract text from file"}

    print(f"\n[Info] Running plagiarism detection on: {file.filename} (mode: {mode})")

    # Use web-enhanced or offline detection based on mode
    if mode == "web":
        result = detect_plagiarism_with_web(text)
    else:
        result = detect_plagiarism(text)

    submission_id = str(uuid.uuid4())[:8]
    result["submission_id"] = submission_id
    result["filename"] = file.filename
    save_result(
        submission_id=submission_id,
        filename=file.filename,
        raw_text=text,
        result_json=result
    )
    print(f"[Success] Done! Score: {result['overall_score']}%")
    return {"submission_id": submission_id, "status": "done"}

@app.get("/api/results/{submission_id}")
async def get_results(submission_id: str):
    row = get_result_by_id(submission_id)
    if row is None:
        return {"status": "error", "message": "Result not found"}
    return row["result_json"]

@app.get("/api/history")
async def get_history_endpoint():
    return get_history()

@app.get("/api/health")
async def health():
    return {"status": "running"}