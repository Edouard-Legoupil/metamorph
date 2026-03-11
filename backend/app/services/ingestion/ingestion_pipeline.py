import os
import time
import uuid
from typing import Dict, Any, Literal
from pathlib import Path
from datetime import datetime
from .graph_db import upsert_document_txn
from .storage import upload_to_s3

SUPPORTED_EXTS = {".pdf", ".docx", ".md", ".markdown", ".html", ".htm"}


def extract_metadata(file_path: str) -> Dict[str, Any]:
    name = Path(file_path).name
    ext = Path(file_path).suffix.lower()
    return {
        "title": name,
        "author": None,
        "publication_date": None,
        "source_url": None,
        "filetype": ext,
        "created_at": datetime.utcnow().isoformat(),
    }


def store_original_file(file_path: str, dest_dir: str = "originals") -> str:
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"{uuid.uuid4()}_{os.path.basename(file_path)}")
    os.rename(file_path, dest_path)
    return dest_path


def create_document_record(metadata: Dict[str, Any], path: str) -> Dict[str, Any]:
    doc_id = upsert_document_txn(metadata, path)
    return {
        "doc_id": doc_id,
        **metadata,
        "file_path": path,
        "version": 1,
        "status": "IMPORTED",
    }


def analyze_layout(file_path: str) -> Dict[str, Any]:
    analysis = {
        "table_density": 0.1,
        "column_count": 1,
        "complex_layout_score": 0.2,
        "embedded_charts": 0,
        "pages_sampled": 10,
    }
    return analysis


def route_parser(
    analysis: Dict[str, Any], threshold: float = 0.7
) -> Literal["docling", "mineru"]:
    if (
        analysis["table_density"] > 0.3
        or analysis["column_count"] > 1
        or analysis["complex_layout_score"] > threshold
    ):
        return "mineru"
    return "docling"


def run_docling(file_path: str, out_md_path: str) -> Dict[str, Any]:
    with open(out_md_path, "w") as out_md:
        out_md.write(f"# Simulated markdown extraction by Docling for {file_path}\n")
    return {"markdown_path": out_md_path, "parser_used": "docling"}


def run_mineru(file_path: str, out_md_path: str) -> Dict[str, Any]:
    with open(out_md_path, "w") as out_md:
        out_md.write(f"# Simulated markdown extraction by MinerU for {file_path}\n")
    return {"markdown_path": out_md_path, "parser_used": "mineru"}


def process_document(file_path: str) -> Dict[str, Any]:
    assert Path(file_path).suffix.lower() in SUPPORTED_EXTS
    metadata = extract_metadata(file_path)
    stored_path = store_original_file(file_path)
    s3_url = upload_to_s3(stored_path)
    record = create_document_record(metadata, s3_url)
    start = time.time()
    analysis = analyze_layout(stored_path)
    parser = route_parser(analysis)
    out_md_path = stored_path + ".md"
    if parser == "docling":
        extraction = run_docling(stored_path, out_md_path)
    else:
        extraction = run_mineru(stored_path, out_md_path)
    elapsed = time.time() - start
    record.update(
        {
            "markdown_path": extraction["markdown_path"],
            "status": "EXTRACTED",
            "parser_used": extraction["parser_used"],
            "processing_time": elapsed,
        }
    )
    print(f"Queued {record['doc_id']} for triplet extraction.")
    return record
