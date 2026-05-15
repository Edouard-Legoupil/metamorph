"""
Crawler Settings API Endpoints

API endpoints for managing crawler configuration settings for users and teams.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.database import get_db
from app.models.sql.user import User, Team
from app.models.sql.settings import CrawlerSettings, NotificationSettings

router = APIRouter(prefix="/crawler-settings", tags=["crawler-settings"])


# Pydantic models

class CrawlerSettingsBase(BaseModel):
    """Base model for crawler settings"""
    user_id: Optional[int] = Field(None, description="User ID (NULL for global settings)")
    team_id: Optional[int] = Field(None, description="Team ID (NULL for user-specific or global)")
    default_max_pages: int = Field(100, description="Default maximum pages to crawl")
    default_max_depth: int = Field(5, description="Default maximum crawl depth")
    default_crawl_delay: float = Field(0.5, description="Default delay between requests in seconds")
    default_respect_robots: bool = Field(True, description="Default: respect robots.txt")
    default_same_domain_only: bool = Field(True, description="Default: only crawl same domain")
    default_discover_files: bool = Field(True, description="Default: discover files during crawling")
    default_file_types: List[str] = Field([], description="Default file types to discover")
    rate_limit_enabled: bool = Field(True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(60, description="Rate limit: requests per minute")
    custom_user_agent: Optional[str] = Field(None, description="Custom user agent string")


class CrawlerSettingsCreate(CrawlerSettingsBase):
    """Request model for creating crawler settings"""
    pass


class CrawlerSettingsUpdate(BaseModel):
    """Request model for updating crawler settings"""
    user_id: Optional[int] = Field(None, description="User ID")
    team_id: Optional[int] = Field(None, description="Team ID")
    default_max_pages: Optional[int] = Field(None, description="Maximum pages to crawl")
    default_max_depth: Optional[int] = Field(None, description="Maximum crawl depth")
    default_crawl_delay: Optional[float] = Field(None, description="Delay between requests in seconds")
    default_respect_robots: Optional[bool] = Field(None, description="Respect robots.txt")
    default_same_domain_only: Optional[bool] = Field(None, description="Only crawl same domain")
    default_discover_files: Optional[bool] = Field(None, description="Discover files during crawling")
    default_file_types: Optional[List[str]] = Field(None, description="File types to discover")
    rate_limit_enabled: Optional[bool] = Field(None, description="Enable rate limiting")
    rate_limit_requests_per_minute: Optional[int] = Field(None, description="Requests per minute")
    custom_user_agent: Optional[str] = Field(None, description="Custom user agent")


class CrawlerSettingsResponse(CrawlerSettingsBase):
    """Response model for crawler settings"""
    id: int
    user_id: Optional[int]
    team_id: Optional[int]
    default_max_pages: int
    default_max_depth: int
    default_crawl_delay: float
    default_respect_robots: bool
    default_same_domain_only: bool
    default_discover_files: bool
    default_file_types: List[str]
    rate_limit_enabled: bool
    rate_limit_requests_per_minute: int
    custom_user_agent: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Notification Settings Models

class NotificationSettingsBase(BaseModel):
    """Base model for notification settings"""
    user_id: int = Field(..., description="User ID")
    email_enabled: bool = Field(True, description="Enable email notifications")
    email_crawl_completed: bool = Field(True, description="Notify on crawl completion")
    email_ingestion_completed: bool = Field(True, description="Notify on ingestion completion")
    email_errors: bool = Field(True, description="Notify on errors")
    slack_enabled: bool = Field(False, description="Enable Slack notifications")
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")
    discord_enabled: bool = Field(False, description="Enable Discord notifications")
    discord_webhook_url: Optional[str] = Field(None, description="Discord webhook URL")
    in_app_enabled: bool = Field(True, description="Enable in-app notifications")


class NotificationSettingsUpdate(BaseModel):
    """Request model for updating notification settings"""
    email_enabled: Optional[bool] = Field(None, description="Enable email notifications")
    email_crawl_completed: Optional[bool] = Field(None, description="Notify on crawl completion")
    email_ingestion_completed: Optional[bool] = Field(None, description="Notify on ingestion completion")
    email_errors: Optional[bool] = Field(None, description="Notify on errors")
    slack_enabled: Optional[bool] = Field(None, description="Enable Slack notifications")
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")
    discord_enabled: Optional[bool] = Field(None, description="Enable Discord notifications")
    discord_webhook_url: Optional[str] = Field(None, description="Discord webhook URL")
    in_app_enabled: Optional[bool] = Field(None, description="Enable in-app notifications")


class NotificationSettingsResponse(NotificationSettingsBase):
    """Response model for notification settings"""
    id: int
    user_id: int
    email_enabled: bool
    email_crawl_completed: bool
    email_ingestion_completed: bool
    email_errors: bool
    slack_enabled: bool
    slack_webhook_url: Optional[str]
    discord_enabled: bool
    discord_webhook_url: Optional[str]
    in_app_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Crawler Settings Endpoints

@router.get("/", response_model=List[CrawlerSettingsResponse])
async def list_crawler_settings(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[CrawlerSettings]:
    """
    List all crawler settings configurations.
    """
    settings = db.query(CrawlerSettings).all()
    return settings


@router.post("/", response_model=CrawlerSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_crawler_settings(
    settings: CrawlerSettingsCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> CrawlerSettings:
    """
    Create new crawler settings.
    """
    # Verify user exists if specified
    if settings.user_id:
        db_user = db.query(User).filter(User.id == settings.user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Verify team exists if specified
    if settings.team_id:
        db_team = db.query(Team).filter(Team.id == settings.team_id).first()
        if not db_team:
            raise HTTPException(status_code=404, detail="Team not found")
    
    # Check for duplicate (same user and team)
    existing_settings = db.query(CrawlerSettings).filter(
        CrawlerSettings.user_id == settings.user_id,
        CrawlerSettings.team_id == settings.team_id,
    ).first()
    
    if existing_settings:
        raise HTTPException(
            status_code=400,
            detail="Crawler settings already exist for this user/team combination"
        )
    
    db_settings = CrawlerSettings(
        user_id=settings.user_id,
        team_id=settings.team_id,
        default_max_pages=settings.default_max_pages,
        default_max_depth=settings.default_max_depth,
        default_crawl_delay=settings.default_crawl_delay,
        default_respect_robots=settings.default_respect_robots,
        default_same_domain_only=settings.default_same_domain_only,
        default_discover_files=settings.default_discover_files,
        default_file_types=settings.default_file_types,
        rate_limit_enabled=settings.rate_limit_enabled,
        rate_limit_requests_per_minute=settings.rate_limit_requests_per_minute,
        custom_user_agent=settings.custom_user_agent,
    )
    
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    
    return db_settings


@router.get("/{settings_id}", response_model=CrawlerSettingsResponse)
async def get_crawler_settings(
    settings_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> CrawlerSettings:
    """
    Get specific crawler settings by ID.
    """
    db_settings = db.query(CrawlerSettings).filter(CrawlerSettings.id == settings_id).first()
    if not db_settings:
        raise HTTPException(status_code=404, detail="Crawler settings not found")
    return db_settings


@router.put("/{settings_id}", response_model=CrawlerSettingsResponse)
async def update_crawler_settings(
    settings_id: int,
    settings: CrawlerSettingsUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> CrawlerSettings:
    """
    Update existing crawler settings.
    """
    db_settings = db.query(CrawlerSettings).filter(CrawlerSettings.id == settings_id).first()
    if not db_settings:
        raise HTTPException(status_code=404, detail="Crawler settings not found")
    
    # Update fields that are provided
    for key, value in settings.model_dump(exclude_unset=True).items():
        if hasattr(db_settings, key):
            setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    
    return db_settings


@router.delete("/{settings_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crawler_settings(
    settings_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Delete crawler settings by ID.
    """
    db_settings = db.query(CrawlerSettings).filter(CrawlerSettings.id == settings_id).first()
    if not db_settings:
        raise HTTPException(status_code=404, detail="Crawler settings not found")
    
    db.delete(db_settings)
    db.commit()


@router.get("/user/{user_id}", response_model=CrawlerSettingsResponse)
async def get_user_crawler_settings(
    user_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> CrawlerSettings:
    """
    Get crawler settings for a specific user.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_settings = db.query(CrawlerSettings).filter(
        CrawlerSettings.user_id == user_id,
        CrawlerSettings.team_id.is_(None),
    ).first()
    
    if not db_settings:
        raise HTTPException(status_code=404, detail="No crawler settings found for this user")
    
    return db_settings


@router.get("/team/{team_id}", response_model=CrawlerSettingsResponse)
async def get_team_crawler_settings(
    team_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> CrawlerSettings:
    """
    Get crawler settings for a specific team.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db_settings = db.query(CrawlerSettings).filter(
        CrawlerSettings.team_id == team_id,
        CrawlerSettings.user_id.is_(None),
    ).first()
    
    if not db_settings:
        raise HTTPException(status_code=404, detail="No crawler settings found for this team")
    
    return db_settings


# Notification Settings Endpoints

@router.get("/notifications", response_model=List[NotificationSettingsResponse])
async def list_notification_settings(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[NotificationSettings]:
    """
    List all notification settings.
    """
    settings = db.query(NotificationSettings).all()
    return settings


@router.get("/notifications/{user_id}", response_model=NotificationSettingsResponse)
async def get_user_notification_settings(
    user_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> NotificationSettings:
    """
    Get notification settings for a specific user.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_settings = db.query(NotificationSettings).filter(
        NotificationSettings.user_id == user_id
    ).first()
    
    if not db_settings:
        # Create default settings if they don't exist
        db_settings = NotificationSettings(
            user_id=user_id,
            email_enabled=True,
            email_crawl_completed=True,
            email_ingestion_completed=True,
            email_errors=True,
            slack_enabled=False,
            slack_webhook_url=None,
            discord_enabled=False,
            discord_webhook_url=None,
            in_app_enabled=True,
        )
        db.add(db_settings)
        db.commit()
        db.refresh(db_settings)
    
    return db_settings


@router.put("/notifications/{user_id}", response_model=NotificationSettingsResponse)
async def update_user_notification_settings(
    user_id: int,
    settings: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> NotificationSettings:
    """
    Update notification settings for a specific user.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_settings = db.query(NotificationSettings).filter(
        NotificationSettings.user_id == user_id
    ).first()
    
    if not db_settings:
        db_settings = NotificationSettings(
            user_id=user_id,
            email_enabled=True,
            email_crawl_completed=True,
            email_ingestion_completed=True,
            email_errors=True,
            slack_enabled=False,
            slack_webhook_url=None,
            discord_enabled=False,
            discord_webhook_url=None,
            in_app_enabled=True,
        )
        db.add(db_settings)
    
    # Update fields that are provided
    for key, value in settings.model_dump(exclude_unset=True).items():
        if hasattr(db_settings, key):
            setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    
    return db_settings
