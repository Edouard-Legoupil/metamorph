"""
Website Management API Endpoints

API endpoints for managing websites, crawling, and file discovery.
Corresponds to API endpoints defined in spec.md v3.0.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.core.config import settings
from app.database import get_db
from app.models.sql.website import (
    Website, WebsiteStatus, DiscoveredFile, FileStatus, 
    ScrapeSession, ScrapeSessionStatus, IngestionJob, IngestionJobStatus, FileType
)
from app.models.sql.user import User
from app.models.sql.settings import Topic, AppSettings
from app.services.website_crawler.crawler import WebsiteCrawler, CloudflareConfig, CrawlConfig
from app.services.preview_service import preview_service
from app.services.ingestion_manager import ingestion_manager
from app.services.scheduling_service import scheduling_service

router = APIRouter(prefix="/websites", tags=["websites"])


# Pydantic models for request/response

class WebsiteCreate(BaseModel):
    """Request model for creating a website"""
    url: HttpUrl = Field(..., description="URL of the website to scrape")
    title: Optional[str] = Field(None, description="Website title")
    description: Optional[str] = Field(None, description="Website description")
    
    # Scraping configuration
    scrape_frequency: Optional[str] = Field("manual", description="Scraping frequency: daily, weekly, monthly, manual")
    max_pages: Optional[int] = Field(100, description="Maximum pages to crawl")
    max_depth: Optional[int] = Field(5, description="Maximum crawl depth")
    respect_robots: Optional[bool] = Field(True, description="Respect robots.txt")
    crawl_delay: Optional[float] = Field(0.5, description="Delay between requests in seconds")
    same_domain_only: Optional[bool] = Field(True, description="Only crawl same domain")
    
    # Cloudflare authentication (FR-001e)
    cf_access_client_id: Optional[str] = Field(None, description="Cloudflare Access Client ID")
    cf_access_client_secret: Optional[str] = Field(None, description="Cloudflare Access Client Secret")
    cf_token_url: Optional[str] = Field(None, description="Cloudflare token URL")
    
    # Topic associations
    topic_ids: Optional[List[int]] = Field([], description="List of topic IDs to associate")


class WebsiteUpdate(BaseModel):
    """Request model for updating a website"""
    url: Optional[HttpUrl] = Field(None, description="URL of the website")
    title: Optional[str] = Field(None, description="Website title")
    description: Optional[str] = Field(None, description="Website description")
    
    scrape_frequency: Optional[str] = Field(None, description="Scraping frequency")
    max_pages: Optional[int] = Field(None, description="Maximum pages to crawl")
    max_depth: Optional[int] = Field(None, description="Maximum crawl depth")
    respect_robots: Optional[bool] = Field(None, description="Respect robots.txt")
    crawl_delay: Optional[float] = Field(None, description="Delay between requests")
    same_domain_only: Optional[bool] = Field(None, description="Only crawl same domain")
    
    cf_access_client_id: Optional[str] = Field(None, description="Cloudflare Access Client ID")
    cf_access_client_secret: Optional[str] = Field(None, description="Cloudflare Access Client Secret")
    cf_token_url: Optional[str] = Field(None, description="Cloudflare token URL")
    
    status: Optional[WebsiteStatus] = Field(None, description="Website status")


class WebsiteResponse(BaseModel):
    """Response model for website"""
    id: int
    url: str
    domain: str
    title: Optional[str]
    description: Optional[str]
    status: WebsiteStatus
    
    scrape_frequency: Optional[str]
    max_pages: int
    max_depth: int
    respect_robots: bool
    crawl_delay: float
    same_domain_only: bool
    
    cf_access_client_id: Optional[str]
    cf_token_url: Optional[str]
    
    last_scraped_at: Optional[datetime]
    next_scrape_at: Optional[datetime]
    total_files_discovered: int
    total_files_ingested: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DiscoveredFileResponse(BaseModel):
    """Response model for discovered file"""
    id: int
    website_id: int
    url: str
    file_name: Optional[str]
    file_type: FileType
    file_extension: Optional[str]
    file_size: Optional[int]
    path: Optional[str]
    title: Optional[str]
    author: Optional[str]
    language: Optional[str]
    
    status: FileStatus
    is_selected: bool
    
    discovered_at: datetime
    scrape_session_id: Optional[int]
    
    class Config:
        from_attributes = True


class ScrapeSessionResponse(BaseModel):
    """Response model for scrape session"""
    id: int
    website_id: int
    session_name: Optional[str]
    status: ScrapeSessionStatus
    
    pages_crawled: int
    files_discovered: int
    files_selected: int
    files_ingested: int
    
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class IngestionJobResponse(BaseModel):
    """Response model for ingestion job"""
    id: int
    discovered_file_id: int
    scrape_session_id: Optional[int]
    
    job_type: str
    status: IngestionJobStatus
    priority: int
    retry_count: int
    
    parsing_tool: Optional[str]
    parsing_version: Optional[str]
    extracted_text_length: Optional[int]
    extracted_entities_count: int
    extracted_relationships_count: int
    
    error_message: Optional[str]
    
    queued_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CrawlRequest(BaseModel):
    """Request model for triggering a crawl"""
    max_pages: Optional[int] = Field(100, description="Maximum pages to crawl")
    max_depth: Optional[int] = Field(5, description="Maximum crawl depth")
    crawl_delay: Optional[float] = Field(0.5, description="Delay between requests")
    respect_robots: Optional[bool] = Field(True, description="Respect robots.txt")
    same_domain_only: Optional[bool] = Field(True, description="Only crawl same domain")
    
    # Cloudflare auth override
    cf_access_client_id: Optional[str] = Field(None)
    cf_access_client_secret: Optional[str] = Field(None)


class FileSelectionRequest(BaseModel):
    """Request model for selecting/deselecting files"""
    file_ids: List[int] = Field(..., description="List of file IDs to select/deselect")
    select: bool = Field(True, description="True to select, False to deselect")


class IngestionRequest(BaseModel):
    """Request model for triggering ingestion"""
    file_ids: Optional[List[int]] = Field(None, description="Specific file IDs to ingest (all selected if None)")
    job_type: Optional[str] = Field("full", description="Type of ingestion: full, text_only, metadata_only")
    priority: Optional[int] = Field(0, description="Priority level")


# Helper functions

def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    parsed = urlparse(str(url))
    domain = parsed.netloc
    # Remove port if present
    if ':' in domain:
        domain = domain.split(':')[0]
    return domain


def map_file_type(extension: Optional[str]) -> FileType:
    """Map file extension to FileType enum"""
    if not extension:
        return FileType.UNKNOWN
    
    extension = extension.lower().strip('.')
    
    file_type_map = {
        'pdf': FileType.PDF,
        'doc': FileType.WORD,
        'docx': FileType.DOCX,
        'xls': FileType.EXCEL,
        'xlsx': FileType.XLSX,
        'ppt': FileType.POWERPOINT,
        'pptx': FileType.PPTX,
        'txt': FileType.TEXT,
        'csv': FileType.CSV,
        'rtf': FileType.RTF,
        'html': FileType.HTML,
        'htm': FileType.HTM,
        'md': FileType.MARKDOWN,
        'json': FileType.JSON,
        'xml': FileType.XML,
        'epub': FileType.EPUB,
        'odt': FileType.ODT,
        'ods': FileType.ODS,
        'odp': FileType.ODP,
    }
    
    return file_type_map.get(extension, FileType.UNKNOWN)


# API Endpoints

@router.post("/", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    website_data: WebsiteCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Website:
    """
    Create a new website for scraping.
    
    Acceptance Criteria (FR-001):
    - Create website with URL and configuration
    - Validate URL format
    - Store Cloudflare credentials if provided
    """
    # Extract domain
    domain = extract_domain_from_url(str(website_data.url))
    
    # Create website
    db_website = Website(
        url=str(website_data.url),
        domain=domain,
        title=website_data.title,
        description=website_data.description,
        
        scrape_frequency=website_data.scrape_frequency,
        max_pages=website_data.max_pages,
        max_depth=website_data.max_depth,
        respect_robots=website_data.respect_robots,
        crawl_delay=website_data.crawl_delay,
        same_domain_only=website_data.same_domain_only,
        
        cf_access_client_id=website_data.cf_access_client_id,
        cf_access_client_secret=website_data.cf_access_client_secret,
        cf_token_url=website_data.cf_token_url or settings.cf_token_url,
        
        status=WebsiteStatus.PENDING,
    )
    
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    
    # Associate topics if provided
    if website_data.topic_ids:
        from app.models.sql.website import WebsiteTopic
        for topic_id in website_data.topic_ids:
            db_topic_association = WebsiteTopic(
                website_id=db_website.id,
                topic_id=topic_id,
            )
            db.add(db_topic_association)
        db.commit()
    
    return db_website


@router.get("/", response_model=List[WebsiteResponse])
async def list_websites(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    status_filter: Optional[WebsiteStatus] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Website]:
    """
    List all websites.
    
    Acceptance Criteria:
    - List websites with pagination
    - Filter by status
    """
    query = db.query(Website)
    
    if status_filter:
        query = query.filter(Website.status == status_filter)
    
    query = query.offset(offset).limit(limit)
    
    return query.all()


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Website:
    """
    Get website details by ID.
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    return db_website


@router.put("/{website_id}", response_model=WebsiteResponse)
async def update_website(
    website_id: int,
    website_data: WebsiteUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Website:
    """
    Update website configuration.
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Update fields
    if website_data.url:
        db_website.url = str(website_data.url)
        db_website.domain = extract_domain_from_url(str(website_data.url))
    
    if website_data.title:
        db_website.title = website_data.title
    if website_data.description:
        db_website.description = website_data.description
    
    if website_data.scrape_frequency:
        db_website.scrape_frequency = website_data.scrape_frequency
    if website_data.max_pages:
        db_website.max_pages = website_data.max_pages
    if website_data.max_depth:
        db_website.max_depth = website_data.max_depth
    if website_data.respect_robots is not None:
        db_website.respect_robots = website_data.respect_robots
    if website_data.crawl_delay:
        db_website.crawl_delay = website_data.crawl_delay
    if website_data.same_domain_only is not None:
        db_website.same_domain_only = website_data.same_domain_only
    
    if website_data.cf_access_client_id:
        db_website.cf_access_client_id = website_data.cf_access_client_id
    if website_data.cf_access_client_secret:
        db_website.cf_access_client_secret = website_data.cf_access_client_secret
    if website_data.cf_token_url:
        db_website.cf_token_url = website_data.cf_token_url
    
    if website_data.status:
        db_website.status = website_data.status
    
    db_website.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_website)
    
    return db_website


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Delete a website and all associated data.
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    db.delete(db_website)
    db.commit()


@router.post("/{website_id}/scrape", response_model=ScrapeSessionResponse)
async def trigger_scrape(
    website_id: int,
    crawl_request: Optional[CrawlRequest] = None,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(get_api_key),
) -> ScrapeSession:
    """
    Trigger a crawl/scrape of a website.
    
    Acceptance Criteria (FR-001c):
    - Start BFS crawl of website
    - Store discovered files
    - Track crawl progress
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Create scrape session
    db_session = ScrapeSession(
        website_id=website_id,
        session_name=f"Scrape {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        max_pages=crawl_request.max_pages if crawl_request else db_website.max_pages,
        max_depth=crawl_request.max_depth if crawl_request else db_website.max_depth,
        crawl_delay=crawl_request.crawl_delay if crawl_request else db_website.crawl_delay,
        status=ScrapeSessionStatus.RUNNING,
        started_at=datetime.now(),
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Update website status
    db_website.status = WebsiteStatus.ACTIVE
    db_website.last_scraped_at = datetime.now()
    db.commit()
    
    # Run scrape in background if background_tasks is available
    if background_tasks:
        background_tasks.add_task(
            run_scrape_session,
            website_id=website_id,
            session_id=db_session.id,
            crawl_config=crawl_request,
        )
        db_session.status = ScrapeSessionStatus.QUEUED
        db.commit()
        return db_session
    
    # Otherwise run synchronously (for testing)
    await run_scrape_session(
        website_id=website_id,
        session_id=db_session.id,
        crawl_config=crawl_request,
    )
    
    # Refresh session to get updated data
    db.refresh(db_session)
    return db_session


@router.get("/{website_id}/files", response_model=List[DiscoveredFileResponse])
async def list_discovered_files(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    status_filter: Optional[FileStatus] = None,
    is_selected: Optional[bool] = None,
    file_type: Optional[FileType] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[DiscoveredFile]:
    """
    List discovered files for a website.
    
    Acceptance Criteria (FR-002b):
    - List all discovered files
    - Filter by status, selection, type
    - Support pagination
    """
    query = db.query(DiscoveredFile).filter(DiscoveredFile.website_id == website_id)
    
    if status_filter:
        query = query.filter(DiscoveredFile.status == status_filter)
    if is_selected is not None:
        query = query.filter(DiscoveredFile.is_selected == is_selected)
    if file_type:
        query = query.filter(DiscoveredFile.file_type == file_type)
    
    query = query.offset(offset).limit(limit).order_by(DiscoveredFile.discovered_at.desc())
    
    return query.all()


@router.get("/{website_id}/sessions", response_model=List[ScrapeSessionResponse])
async def list_scrape_sessions(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    limit: int = 50,
    offset: int = 0,
) -> List[ScrapeSession]:
    """
    List scrape sessions for a website.
    """
    query = db.query(ScrapeSession).filter(ScrapeSession.website_id == website_id)
    query = query.offset(offset).limit(limit).order_by(ScrapeSession.created_at.desc())
    return query.all()


@router.post("/{website_id}/files/select", response_model=List[DiscoveredFileResponse])
async def select_files(
    website_id: int,
    selection: FileSelectionRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[DiscoveredFile]:
    """
    Select or deselect files for ingestion.
    
    Acceptance Criteria (FR-002d):
    - Select multiple files at once
    - Track selection status
    - Support bulk operations
    """
    # Verify website exists
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Update file selection
    for file_id in selection.file_ids:
        db_file = db.query(DiscoveredFile).filter(
            DiscoveredFile.id == file_id,
            DiscoveredFile.website_id == website_id,
        ).first()
        
        if db_file:
            db_file.is_selected = selection.select
            db_file.selected_at = datetime.now() if selection.select else None
            db_file.status = FileStatus.SELECTED if selection.select else FileStatus.DISCOVERED
            db_file.updated_at = datetime.now()
    
    db.commit()
    
    # Return updated files
    updated_files = db.query(DiscoveredFile).filter(
        DiscoveredFile.id.in_(selection.file_ids),
        DiscoveredFile.website_id == website_id,
    ).all()
    
    return updated_files


@router.post("/{website_id}/files/deselect", response_model=List[DiscoveredFileResponse])
async def deselect_files(
    website_id: int,
    selection: FileSelectionRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[DiscoveredFile]:
    """Deselect files for ingestion."""
    selection.select = False
    return await select_files(website_id, selection, db, api_key)


@router.post("/{website_id}/ingest", response_model=Dict[str, Any])
async def trigger_ingestion(
    website_id: int,
    ingestion_request: Optional[IngestionRequest] = None,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Trigger ingestion of selected files.
    
    Acceptance Criteria (FR-003):
    - Ingest selected files
    - Track ingestion progress
    - Queue files for processing
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Get selected files
    query = db.query(DiscoveredFile).filter(
        DiscoveredFile.website_id == website_id,
        DiscoveredFile.is_selected == True,
    )
    
    if ingestion_request and ingestion_request.file_ids:
        query = query.filter(DiscoveredFile.id.in_(ingestion_request.file_ids))
    
    selected_files = query.all()
    
    if not selected_files:
        raise HTTPException(status_code=400, detail="No files selected for ingestion")
    
    # Create ingestion jobs
    ingestion_jobs = []
    for file in selected_files:
        db_job = IngestionJob(
            discovered_file_id=file.id,
            job_type=ingestion_request.job_type if ingestion_request else "full",
            priority=ingestion_request.priority if ingestion_request else 0,
            status=IngestionJobStatus.PENDING,
        )
        db.add(db_job)
        ingestion_jobs.append(db_job)
    
    db.commit()
    
    # Update website stats
    db_website.total_files_ingested += len(ingestion_jobs)
    db.commit()
    
    # Run ingestion in background
    if background_tasks:
        for job in ingestion_jobs:
            background_tasks.add_task(
                process_ingestion_job,
                job_id=job.id,
            )
    else:
        # Synchronous processing (for testing)
        for job in ingestion_jobs:
            await process_ingestion_job(job_id=job.id)
    
    return {
        "status": "queued",
        "jobs_created": len(ingestion_jobs),
        "job_ids": [job.id for job in ingestion_jobs],
    }


@router.get("/ingestion/jobs/{job_id}/status")
async def get_ingestion_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get status of an ingestion job.
    """
    return ingestion_manager.get_job_status(db, job_id)


@router.post("/ingestion/jobs/{job_id}/retry")
async def retry_ingestion_job(
    job_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Retry a failed ingestion job.
    """
    return ingestion_manager.retry_failed_job(db, job_id)


@router.get("/ingestion/stats")
async def get_ingestion_statistics(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get overall ingestion statistics.
    """
    return ingestion_manager.get_ingestion_stats(db)


# Scheduled Scraping Endpoints

@router.post("/{website_id}/schedule")
async def schedule_website(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Schedule a website for regular scraping.
    """
    return scheduling_service.schedule_website(db, website_id)


@router.put("/{website_id}/schedule")
async def update_website_schedule(
    website_id: int,
    frequency: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Update the schedule frequency for a website.
    """
    return scheduling_service.update_website_schedule(db, website_id, frequency)


@router.delete("/{website_id}/schedule")
async def cancel_website_schedule(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Cancel scheduled scraping for a website.
    """
    return scheduling_service.cancel_website_schedule(website_id)


@router.get("/{website_id}/schedule")
async def get_website_schedule(
    website_id: int,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get schedule information for a website.
    """
    return scheduling_service.get_website_schedule(website_id)


@router.post("/{website_id}/scrape-now")
async def trigger_immediate_scrape(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Trigger an immediate scrape of a website (outside of schedule).
    """
    return await scheduling_service.trigger_immediate_scrape(db, website_id)


@router.get("/scheduling/schedules")
async def get_all_schedules(
    api_key: str = Depends(get_api_key),
) -> List[Dict[str, Any]]:
    """
    Get all scheduled scraping jobs.
    """
    return scheduling_service.get_all_schedules()


@router.post("/scheduling/pause")
async def pause_all_schedules(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Pause all scheduled scraping jobs.
    """
    return scheduling_service.pause_all_schedules()


@router.post("/scheduling/resume")
async def resume_all_schedules(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Resume all scheduled scraping jobs.
    """
    return scheduling_service.resume_all_schedules()


@router.get("/scheduling/stats")
async def get_scheduling_statistics(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get statistics about scheduled scraping.
    """
    return scheduling_service.get_scheduling_stats(db)


@router.get("/{website_id}/scrape-status")
async def get_scrape_status(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get current scrape status for a website.
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Get latest session
    latest_session = db.query(ScrapeSession).filter(
        ScrapeSession.website_id == website_id,
    ).order_by(ScrapeSession.created_at.desc()).first()
    
    # Get counts
    file_counts = {
        "total": db.query(DiscoveredFile).filter(
            DiscoveredFile.website_id == website_id,
        ).count(),
        "selected": db.query(DiscoveredFile).filter(
            DiscoveredFile.website_id == website_id,
            DiscoveredFile.is_selected == True,
        ).count(),
        "by_type": {},
    }
    
    # Count by file type
    for file_type in FileType:
        count = db.query(DiscoveredFile).filter(
            DiscoveredFile.website_id == website_id,
            DiscoveredFile.file_type == file_type,
        ).count()
        if count > 0:
            file_counts["by_type"][file_type.value] = count
    
    return {
        "website": {
            "id": db_website.id,
            "url": db_website.url,
            "status": db_website.status.value,
        },
        "latest_session": {
            "id": latest_session.id if latest_session else None,
            "status": latest_session.status.value if latest_session else None,
            "started_at": latest_session.started_at.isoformat() if latest_session and latest_session.started_at else None,
            "completed_at": latest_session.completed_at.isoformat() if latest_session and latest_session.completed_at else None,
        } if latest_session else None,
        "file_counts": file_counts,
    }


@router.get("/files/{file_id}", response_model=DiscoveredFileResponse)
async def get_file_details(
    file_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> DiscoveredFile:
    """
    Get details for a specific discovered file.
    """
    db_file = db.query(DiscoveredFile).filter(DiscoveredFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@router.get("/files/{file_id}/preview")
async def get_file_preview(
    file_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get preview of a discovered file (FR-002c).
    
    Acceptance Criteria:
    - Generate preview of file content
    - Support various file types
    - Cache previews for performance
    """
    db_file = db.query(DiscoveredFile).filter(DiscoveredFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Generate preview using the preview service
    try:
        preview_result = preview_service.generate_preview(db_file)
        return preview_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate file preview: {str(e)}"
        )


# Background task functions

async def run_scrape_session(
    website_id: int,
    session_id: int,
    crawl_config: Optional[CrawlRequest] = None,
) -> None:
    """
    Run a scrape session in the background.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    
    # Create a new session for background task
    engine = create_engine(settings.sqlalchemy_database_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Get website and session
        db_website = db.query(Website).filter(Website.id == website_id).first()
        db_session = db.query(ScrapeSession).filter(ScrapeSession.id == session_id).first()
        
        if not db_website or not db_session:
            return
        
        # Configure crawler
        cloudflare_config = CloudflareConfig(
            enabled=bool(db_website.cf_access_client_id and db_website.cf_access_client_secret),
            cf_access_client_id=db_website.cf_access_client_id or "",
            cf_access_client_secret=db_website.cf_access_client_secret or "",
            token_url=db_website.cf_token_url or "",
        )
        
        crawler = WebsiteCrawler(
            base_url=db_website.url,
            max_pages=crawl_config.max_pages if crawl_config else db_website.max_pages,
            max_depth=crawl_config.max_depth if crawl_config else db_website.max_depth,
            crawl_delay=crawl_config.crawl_delay if crawl_config else db_website.crawl_delay,
            respect_robots=db_website.respect_robots,
            same_domain_only=db_website.same_domain_only,
            cloudflare=cloudflare_config,
        )
        
        # Run crawl
        db_session.status = ScrapeSessionStatus.RUNNING
        db_session.started_at = datetime.now()
        db.commit()
        
        try:
            result = crawler.crawl()
            
            # Store discovered files
            for file_meta in result.discovered_files:
                # Check if file already exists
                existing_file = db.query(DiscoveredFile).filter(
                    DiscoveredFile.website_id == website_id,
                    DiscoveredFile.url == file_meta["url"],
                ).first()
                
                if not existing_file:
                    db_file = DiscoveredFile(
                        website_id=website_id,
                        url=file_meta["url"],
                        file_name=file_meta["file_name"],
                        file_type=map_file_type(file_meta.get("file_type")),
                        file_extension=file_meta.get("file_type"),
                        path=file_meta.get("path"),
                        scrape_session_id=session_id,
                        status=FileStatus.DISCOVERED,
                        discovered_at=datetime.now(),
                    )
                    db.add(db_file)
            
            # Update session stats
            db_session.pages_crawled = result.pages_crawled
            db_session.files_discovered = result.files_discovered
            db_session.status = ScrapeSessionStatus.COMPLETED
            db_session.completed_at = datetime.now()
            db_session.duration_seconds = result.duration
            
            # Update website stats
            db_website.total_files_discovered += result.files_discovered
            db_website.last_scraped_at = datetime.now()
            db_website.status = WebsiteStatus.ACTIVE
            
            db.commit()
            
        except Exception as e:
            db_session.status = ScrapeSessionStatus.FAILED
            db_session.completed_at = datetime.now()
            db_website.status = WebsiteStatus.ERROR
            db.commit()
            
    finally:
        db.close()


async def process_ingestion_job(job_id: int) -> None:
    """
    Process an ingestion job in the background.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    
    # Create a new session for background task
    engine = create_engine(settings.sqlalchemy_database_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Use the ingestion manager to process the job
        result = ingestion_manager.process_ingestion_job(db, job_id)
        print(f"Ingestion job {job_id} completed: {result['status']}")
        
    except Exception as e:
        print(f"Ingestion job {job_id} failed: {str(e)}")
        
    finally:
        db.close()
