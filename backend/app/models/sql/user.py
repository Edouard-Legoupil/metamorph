"""
User and Team Models

SQL models for user management and team organization.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
from enum import Enum as PyEnum

from .base import Base


class UserRole(PyEnum):
    """User roles in the application"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class UserStatus(PyEnum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(Base):
    """
    User entity for authentication and authorization.
    
    Represents a user account in the Metamorph application.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(500), nullable=True)  # Hashed password
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Role and status
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    
    # Preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    theme = Column(String(20), default="light")  # light, dark, system
    
    # API keys and tokens
    api_key = Column(String(100), unique=True, nullable=True)
    api_key_secret = Column(String(200), nullable=True)  # Hashed
    
    # Last activity
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    
    # Quotas and limits
    max_websites = Column(Integer, nullable=True)  # Max websites user can create
    max_storage_gb = Column(Integer, nullable=True)  # Max storage in GB
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teams = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    owned_teams = relationship("Team", back_populates="owner", foreign_keys="Team.owner_id")
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.email
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"


class Team(Base):
    """
    Team entity for organizing users.
    
    Represents a team or organization in the Metamorph application.
    """
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Team information
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Settings
    is_public = Column(Boolean, default=False)  # Anyone can join
    max_members = Column(Integer, nullable=True)
    max_websites = Column(Integer, nullable=True)
    
    # Quotas
    total_storage_gb = Column(Integer, default=10)  # Default 10GB
    total_websites = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class TeamMember(Base):
    """
    Many-to-many relationship between teams and users.
    
    Represents a user's membership in a team.
    """
    
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Member role within the team
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Invitation tracking
    invited_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role.value})>"
