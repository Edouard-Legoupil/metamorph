"""
Production-specific configuration for Metamorph
Overrides default settings for production environment
"""

from pydantic_settings import BaseSettings
from pydantic import Field
import os


class ProductionSettings(BaseSettings):
    """Production environment settings"""
    
    # Security settings
    secret_key: str = Field(..., env="SECRET_KEY")
    mcp_api_keys: list[str] = Field(..., env="MCP_API_KEYS")
    
    # CORS settings - more restrictive in production
    allowed_origins: list[str] = Field(
        default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "https://metamorph.example.com").split(",")
    )
    
    # Database - use connection pooling in production
    sqlalchemy_database_url: str = Field(
        ..., 
        env="DATABASE_URL"
    )
    sqlalchemy_pool_size: int = 20
    sqlalchemy_max_overflow: int = 10
    sqlalchemy_pool_timeout: int = 30
    sqlalchemy_pool_recycle: int = 3600
    
    # Rate limiting - more restrictive in production
    rate_limit_per_minute: int = 30
    rate_limit_burst: int = 50
    
    # File upload limits
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_preview_length: int = 5000  # Shorter previews in production
    
    # Cache settings
    cache_ttl: int = 3600  # 1 hour cache TTL
    cache_size_limit: int = 10000  # Max cache entries
    
    # Logging - more verbose in production
    log_level: str = "INFO"
    log_file: str = "/var/log/metamorph/app.log"
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # Security headers
    csp_policy: str = """
        default-src 'self';
        script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
        style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
        img-src 'self' data: https://*.googleapis.com;
        font-src 'self' https://fonts.gstatic.com;
        connect-src 'self' http://backend:8000;
        frame-src 'none';
        object-src 'none';
        base-uri 'self';
        form-action 'self';
    """
    
    # Feature flags
    maintenance_mode: bool = False
    read_only_mode: bool = False
    debug_mode: bool = False
    
    # External service timeouts
    external_service_timeout: int = 30
    
    # Health check endpoints
    health_check_interval: int = 60
    
    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # Tracing
    opentelemetry_enabled: bool = True
    opentelemetry_endpoint: str = "http://jaeger:4318/v1/traces"
    
    # Metrics
    metrics_enabled: bool = True
    
    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"


# Production settings instance
production_settings = ProductionSettings()
