import boto3
import os

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "metamorph-documents")


def upload_to_s3(local_path: str, dest_key: str = None) -> str:
    session = boto3.session.Session()
    s3 = session.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    )
    dest_key = dest_key or os.path.basename(local_path)
    s3.upload_file(local_path, S3_BUCKET, dest_key)
    return f"s3://{S3_BUCKET}/{dest_key}"
