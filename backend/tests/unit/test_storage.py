from backend.app.services.ingestion.storage import upload_to_s3
import os


def test_upload_to_minio():
    fp = "/tmp/test-upload.txt"
    with open(fp, "w") as f:
        f.write("ok")
    s3_url = upload_to_s3(fp, "test-unit/test-upload.txt")
    assert s3_url.startswith("s3://")
