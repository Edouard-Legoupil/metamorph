from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    project_name: str = "Metamorph"
    api_v1_str: str = "/api/v1"
    allowed_hosts: List[str] = ["*"]
    secret_key: str = Field(os.getenv("SECRET_KEY", "devsecret"))
    mcp_api_keys: List[str] = Field(
        default_factory=lambda: os.getenv("MCP_API_KEY", "changeme").split(",")
    )
    
    # MinIO configuration (for file storage)
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "dev-access-key")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "dev-secret-key")
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_bucket: str = os.getenv("MINIO_BUCKET", "metamorph")
    
    # Cloudflare configuration (FR-001e)
    cf_access_client_id: str = os.getenv("cfAccessClientId", "")
    cf_access_client_secret: str = os.getenv("cfAccessClientSecret", "")
    cf_token_url: str = os.getenv("CF_TOKEN_URL", "https://www.cloudflare.com/cdn-cgi/access/cfaccess")
    
    # Frontend configuration
    frontend_build_dir: str = os.getenv("FRONTEND_BUILD_DIR", "../frontend/dist")
    allowed_origins: List[str] = Field(
        default_factory=lambda: [os.getenv("ALLOWED_ORIGINS", "*")]
    )
    
    # Database configuration
    sqlalchemy_database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/metamorph"
    )
    
    # Logging and rate limiting
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    # Preview service configuration
    preview_cache_dir: str = os.getenv("PREVIEW_CACHE_DIR", "/tmp/preview_cache")
    max_preview_length: int = int(os.getenv("MAX_PREVIEW_LENGTH", 1000))
    max_preview_file_size: int = int(os.getenv("MAX_PREVIEW_FILE_SIZE", 10485760))  # 10MB


settings = Settings()
