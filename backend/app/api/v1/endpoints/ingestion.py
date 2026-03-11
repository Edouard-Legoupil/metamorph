from fastapi import UploadFile, File, APIRouter, BackgroundTasks
from typing import List
from app.services.ingestion.ingestion_pipeline import process_document
import shutil

router = APIRouter()


from fastapi import Depends
from app.core.security import get_api_key

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None, api_key: str = Depends(get_api_key)
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)
    if background_tasks:
        background_tasks.add_task(process_document, temp_path)
        return {"status": "queued", "filename": file.filename}
    else:
        result = process_document(temp_path)
        return {"status": "processed", "result": result}


@router.post("/batch-ingest")
async def batch_ingest(
    files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = None, api_key: str = Depends(get_api_key)
    files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = None
):
    for file in files:
        tmp = f"/tmp/{file.filename}"
        with open(tmp, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
        if background_tasks:
            background_tasks.add_task(process_document, tmp)
        else:
            process_document(tmp)
    return {"status": "queued", "files": [f.filename for f in files]}
