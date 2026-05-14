"""
Topic and App Settings Models

SQL models for topics, categories, and application settings.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum as PyEnum

from .base import Base


class TopicCategory(PyEnum):
    """Categories for topics"""
    GENERAL = "general"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    SCIENCE = "science"
    EDUCATION = "education"
    FINANCE = "finance"
    LEGAL = "legal"
    POLICY = "policy"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    CUSTOM = "custom"


class Topic(Base):
    """
    Topic entity for categorizing content.
    
    Represents a topic or category for organizing websites and knowledge.
    """
    
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Topic information
    name = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(Enum(TopicCategory), default=TopicCategory.GENERAL)
    
    # Parent-child hierarchy
    parent_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    color = Column(String(20), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)  # Icon name
    
    # Ordering
    order_index = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System-defined topic
    
    # Usage statistics
    website_count = Column(Integer, default=0)
    file_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("Topic", remote_side=[id], back_populates="children")
    children = relationship("Topic", back_populates="parent", cascade="all, delete-orphan")
    websites = relationship("WebsiteTopic", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class AppSettings(Base):
    """
    Application settings and configuration.
    
    Stores global application settings and preferences.
    """
    
    __tablename__ = "app_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Setting key (unique)
    key = Column(String(200), unique=True, nullable=False, index=True)
    
    # Setting value (can be JSON for complex values)
    value = Column(Text, nullable=True)
    json_value = Column(JSON, nullable=True)  # For structured data
    
    # Metadata
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "general", "scraping", "ai", "storage"
    
    # Validation
    is_required = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @classmethod
    def get_value(cls, key: str, default: Any = None) -> Any:
        """Get a setting value by key"""
        # This would be implemented with a database query
        # For now, this is a placeholder
        return default
    
    @classmethod
    def set_value(cls, key: str, value: Any) -> None:
        """Set a setting value by key"""
        # This would be implemented with a database query
        pass
    
    def __repr__(self):
        return f"<AppSettings(id={self.id}, key='{self.key}')>"


class CrawlerSettings(Base):
    """
    Crawler-specific settings.
    
    Stores configuration for the website crawler.
    """
    
    __tablename__ = "crawler_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User/Team association (can be NULL for global settings)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    
    # Crawler defaults
    default_max_pages = Column(Integer, default=100)
    default_max_depth = Column(Integer, default=5)
    default_crawl_delay = Column(Float, default=0.5)
    default_respect_robots = Column(Boolean, default=True)
    default_same_domain_only = Column(Boolean, default=True)
    
    # File discovery defaults
    default_discover_files = Column(Boolean, default=True)
    default_file_types = Column(JSON, default=[])  # List of file extensions
    
    # Rate limiting
    rate_limit_enabled = Column(Boolean, default=True)
    rate_limit_requests_per_minute = Column(Integer, default=60)
    
    # User agent
    custom_user_agent = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    team = relationship("Team")
    
    def __repr__(self):
        return f"<CrawlerSettings(id={self.id}, user_id={self.user_id}, team_id={self.team_id})>"


class NotificationSettings(Base):
    """
    Notification settings for users.
    
    Stores user preferences for notifications.
    """
    
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Email notifications
    email_enabled = Column(Boolean, default=True)
    email_crawl_completed = Column(Boolean, default=True)
    email_ingestion_completed = Column(Boolean, default=True)
    email_errors = Column(Boolean, default=True)
    
    # Slack/Teams notifications
    slack_enabled = Column(Boolean, default=False)
    slack_webhook_url = Column(String(500), nullable=True)
    
    # Discord notifications
    discord_enabled = Column(Boolean, default=False)
    discord_webhook_url = Column(String(500), nullable=True)
    
    # In-app notifications
    in_app_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<NotificationSettings(id={self.id}, user_id={self.user_id})>"
