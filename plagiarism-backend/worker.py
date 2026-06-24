import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Celery requires a specific URL format to use PostgreSQL as a broker via SQLAlchemy
broker_url = f"sqla+postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
backend_url = f"db+postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="process_plagiarism_task", bind=True)
def process_plagiarism_task(self, submission_id: str, filename: str, raw_text: str, mode: str):
    print(f"[Celery] Started task for {submission_id} (mode: {mode})")
    
    # Import here to avoid heavy AI models loading before the worker actually needs them
    from detect import detect_plagiarism_with_web, detect_plagiarism
    from db import save_result, get_recent_texts
    from tribunal import run_tribunal
    
    if mode == "web":
        result = detect_plagiarism_with_web(raw_text)
    else:
        result = detect_plagiarism(raw_text)
        
    print(f"[Celery] Fetching history for {submission_id} tribunal...")
    historical_texts = get_recent_texts(limit=3)
    print(f"[Celery] Running LangGraph Tribunal for {submission_id}...")
    try:
        tribunal_result = run_tribunal(raw_text, historical_texts)
        result["tribunal"] = tribunal_result
    except Exception as e:
        print(f"[Celery] Tribunal failed: {e}")
        result["tribunal"] = None
        
    result["submission_id"] = submission_id
    result["filename"] = filename
    
    save_result(
        submission_id=submission_id,
        filename=filename,
        raw_text=raw_text,
        result_json=result
    )
    print(f"[Celery] Finished task for {submission_id}")
    return {"status": "done", "submission_id": submission_id}
