from pydantic import BaseSettings, Field
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
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "dev-access-key")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "dev-secret-key")
    cf_access_client_id: str = os.getenv("cfAccessClientId", "")
    cf_access_client_secret: str = os.getenv("cfAccessClientSecret", "")
    frontend_build_dir: str = os.getenv("FRONTEND_BUILD_DIR", "../frontend/dist")
    allowed_origins: List[str] = Field(
        default_factory=lambda: [os.getenv("ALLOWED_ORIGINS", "*")]
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))


settings = Settings()
