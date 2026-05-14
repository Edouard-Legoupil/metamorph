"""
Website and File Discovery Models (FR-001, FR-002, FR-003)

SQL models for website crawling and file discovery.
Corresponds to the v3.0 data model in spec.md.
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
from enum import Enum as PyEnum

from .base import Base


class WebsiteStatus(PyEnum):
    """Status of a website scraping configuration"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    DELETED = "deleted"


class FileStatus(PyEnum):
    """Status of a discovered file"""
    PENDING = "pending"
    DISCOVERED = "discovered"
    SELECTED = "selected"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    PARSING = "parsing"
    PARSED = "parsed"
    INGESTED = "ingested"
    ERROR = "error"
    SKIPPED = "skipped"


class ScrapeSessionStatus(PyEnum):
    """Status of a scrape session"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionJobStatus(PyEnum):
    """Status of an ingestion job"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileType(PyEnum):
    """Supported file types for scraping"""
    PDF = "pdf"
    WORD = "doc"
    DOCX = "docx"
    EXCEL = "xls"
    XLSX = "xlsx"
    POWERPOINT = "ppt"
    PPTX = "pptx"
    TEXT = "txt"
    CSV = "csv"
    RTF = "rtf"
    HTML = "html"
    HTM = "htm"
    MARKDOWN = "md"
    JSON = "json"
    XML = "xml"
    EPUB = "epub"
    ODT = "odt"
    ODS = "ods"
    ODP = "odp"
    UNKNOWN = "unknown"


class Website(Base):
    """
    Website entity for crawling and scraping.
    
    Represents a website that has been configured for scraping.
    
    Acceptance Criteria (FR-001):
    - Store website URL and configuration
    - Track scraping status and history
    - Support rate limiting and robots.txt respect
    """
    
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    domain = Column(String(500), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Scraping configuration
    scrape_frequency = Column(String(50), nullable=True)  # daily, weekly, monthly, manual
    max_pages = Column(Integer, default=100)
    max_depth = Column(Integer, default=5)
    respect_robots = Column(Boolean, default=True)
    crawl_delay = Column(Float, default=0.5)  # seconds between requests
    same_domain_only = Column(Boolean, default=True)
    
    # Cloudflare authentication (FR-001e)
    cf_access_client_id = Column(String(500), nullable=True)
    cf_access_client_secret = Column(String(500), nullable=True)
    cf_token_url = Column(String(1000), nullable=True)
    
    # Status tracking
    status = Column(Enum(WebsiteStatus), default=WebsiteStatus.PENDING)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    next_scrape_at = Column(DateTime(timezone=True), nullable=True)
    total_files_discovered = Column(Integer, default=0)
    total_files_ingested = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scrape_sessions = relationship("ScrapeSession", back_populates="website", cascade="all, delete-orphan")
    discovered_files = relationship("DiscoveredFile", back_populates="website", cascade="all, delete-orphan")
    topics = relationship("WebsiteTopic", back_populates="website", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Website(id={self.id}, url='{self.url}', status={self.status.value})>"


class DiscoveredFile(Base):
    """
    Discovered file from website crawling.
    
    Represents a file that was discovered during website crawling.
    
    Acceptance Criteria (FR-001a, FR-002):
    - Store file metadata and URL
    - Track file type and status
    - Support selection for ingestion
    """
    
    __tablename__ = "discovered_files"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    url = Column(String(1000), nullable=False, index=True)
    file_name = Column(String(500), nullable=True)
    file_type = Column(Enum(FileType), default=FileType.UNKNOWN)
    file_extension = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    content_hash = Column(String(128), nullable=True)  # MD5/SHA256 hash
    last_modified = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    path = Column(String(1000), nullable=True)
    title = Column(String(500), nullable=True)
    author = Column(String(500), nullable=True)
    language = Column(String(50), nullable=True)
    
    # Status and selection
    status = Column(Enum(FileStatus), default=FileStatus.DISCOVERED)
    is_selected = Column(Boolean, default=False)
    selected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Provenance tracking
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    scrape_session_id = Column(Integer, ForeignKey("scrape_sessions.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    website = relationship("Website", back_populates="discovered_files")
    scrape_session = relationship("ScrapeSession", back_populates="discovered_files")
    ingestion_jobs = relationship("IngestionJob", back_populates="discovered_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DiscoveredFile(id={self.id}, url='{self.url}', type={self.file_type.value})>"


class ScrapeSession(Base):
    """
    Scrape session for tracking crawling operations.
    
    Represents a single crawling session for a website.
    
    Acceptance Criteria (FR-001c):
    - Track crawl progress and results
    - Store configuration for each session
    - Record errors and statistics
    """
    
    __tablename__ = "scrape_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    
    # Session configuration
    session_name = Column(String(500), nullable=True)
    max_pages = Column(Integer, nullable=True)
    max_depth = Column(Integer, nullable=True)
    crawl_delay = Column(Float, nullable=True)
    
    # Status
    status = Column(Enum(ScrapeSessionStatus), default=ScrapeSessionStatus.PENDING)
    
    # Statistics
    pages_crawled = Column(Integer, default=0)
    files_discovered = Column(Integer, default=0)
    files_selected = Column(Integer, default=0)
    files_ingested = Column(Integer, default=0)
    errors = Column(Text, nullable=True)  # JSON array of error messages
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    website = relationship("Website", back_populates="scrape_sessions")
    discovered_files = relationship("DiscoveredFile", back_populates="scrape_session")
    
    def __repr__(self):
        return f"<ScrapeSession(id={self.id}, website_id={self.website_id}, status={self.status.value})>"


class IngestionJob(Base):
    """
    Ingestion job for tracking file processing.
    
    Represents the ingestion process for a discovered file.
    
    Acceptance Criteria (FR-003):
    - Track file ingestion progress
    - Store parsing and extraction results
    - Record errors and retries
    """
    
    __tablename__ = "ingestion_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    discovered_file_id = Column(Integer, ForeignKey("discovered_files.id", ondelete="CASCADE"), nullable=False)
    scrape_session_id = Column(Integer, ForeignKey("scrape_sessions.id", ondelete="SET NULL"), nullable=True)
    
    # Job configuration
    job_type = Column(String(100), default="full")  # full, text_only, metadata_only
    priority = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Status
    status = Column(Enum(IngestionJobStatus), default=IngestionJobStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Processing information
    parsing_tool = Column(String(100), nullable=True)  # docling, mineru, custom
    parsing_version = Column(String(100), nullable=True)
    extracted_text_length = Column(Integer, nullable=True)
    extracted_entities_count = Column(Integer, default=0)
    extracted_relationships_count = Column(Integer, default=0)
    
    # File information
    downloaded_path = Column(String(1000), nullable=True)
    parsed_path = Column(String(1000), nullable=True)
    
    # Timing
    queued_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    discovered_file = relationship("DiscoveredFile", back_populates="ingestion_jobs")
    scrape_session = relationship("ScrapeSession")
    
    def __repr__(self):
        return f"<IngestionJob(id={self.id}, file_id={self.discovered_file_id}, status={self.status.value})>"


class WebsiteTopic(Base):
    """
    Many-to-many relationship between websites and topics.
    
    Allows categorizing websites by topic for organization.
    """
    
    __tablename__ = "website_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("Website", back_populates="topics")
    topic = relationship("Topic", back_populates="websites")
    
    def __repr__(self):
        return f"<WebsiteTopic(website_id={self.website_id}, topic_id={self.topic_id})>"
