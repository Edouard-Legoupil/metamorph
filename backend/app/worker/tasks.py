from celery import Celery
from app.services.ingestion.ingestion_pipeline import process_document
from app.services.extraction.triplet_extractor import extract_triplets_from_markdown
import os

celery_app = Celery("worker", broker=os.getenv("REDIS_URL", "redis://redis:6379/0"))


@celery_app.task
def async_process_document(file_path: str, doc_type: str, doc_id: str, metadata: dict):
    result = process_document(file_path)
    with open(result["markdown_path"], "r") as md:
        markdown = md.read()
    extract_triplets_from_markdown(markdown, doc_type, doc_id, metadata)
    # You could push output to a dashboard/notify here
    return {"status": "completed", "doc_id": doc_id}
