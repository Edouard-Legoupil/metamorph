"""
User Management API Endpoints

API endpoints for managing users and authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_api_key, hash_password, verify_password
from app.database import get_db
from app.models.sql.user import User, UserRole, UserStatus, Team, TeamMember

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic models

class UserCreate(BaseModel):
    """Request model for creating a user"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    display_name: Optional[str] = Field(None, description="Display name")
    role: Optional[UserRole] = Field(UserRole.VIEWER, description="User role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "role": "viewer",
            }
        }


class UserUpdate(BaseModel):
    """Request model for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    display_name: Optional[str] = Field(None, description="Display name")
    role: Optional[UserRole] = Field(None, description="User role")
    status: Optional[UserStatus] = Field(None, description="User status")
    max_websites: Optional[int] = Field(None, description="Max websites limit")
    max_storage_gb: Optional[int] = Field(None, description="Max storage in GB")
    timezone: Optional[str] = Field(None, description="Timezone")
    theme: Optional[str] = Field(None, description="UI theme")


class UserResponse(BaseModel):
    """Response model for user"""
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str]
    
    max_websites: Optional[int]
    max_storage_gb: Optional[int]
    
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    """Request model for creating a team"""
    name: str = Field(..., min_length=2, max_length=200, description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    slug: Optional[str] = Field(None, description="Team slug (URL-friendly)")
    is_public: Optional[bool] = Field(False, description="Is team public")
    max_members: Optional[int] = Field(None, description="Max team members")
    max_websites: Optional[int] = Field(None, description="Max websites for team")


class TeamUpdate(BaseModel):
    """Request model for updating a team"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    slug: Optional[str] = Field(None)
    is_public: Optional[bool] = Field(None)
    max_members: Optional[int] = Field(None)
    max_websites: Optional[int] = Field(None)


class TeamResponse(BaseModel):
    """Response model for team"""
    id: int
    name: str
    description: Optional[str]
    slug: str
    owner_id: Optional[int]
    is_public: bool
    max_members: Optional[int]
    max_websites: Optional[int]
    total_storage_gb: int
    total_websites: int
    total_files: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamMemberCreate(BaseModel):
    """Request model for adding a team member"""
    user_id: int = Field(..., description="User ID to add to team")
    role: Optional[UserRole] = Field(UserRole.VIEWER, description="Member role in team")


class TeamMemberResponse(BaseModel):
    """Response model for team member"""
    id: int
    team_id: int
    user_id: int
    role: UserRole
    is_active: bool
    invited_at: Optional[datetime]
    joined_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# API Endpoints

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> User:
    """
    Create a new user.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        display_name=user_data.display_name or f"{user_data.first_name} {user_data.last_name}" if user_data.first_name and user_data.last_name else None,
        role=user_data.role,
        status=UserStatus.ACTIVE,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    role_filter: Optional[UserRole] = None,
    status_filter: Optional[UserStatus] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[User]:
    """
    List all users.
    """
    query = db.query(User)
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    if status_filter:
        query = query.filter(User.status == status_filter)
    
    query = query.offset(offset).limit(limit)
    
    return query.all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> User:
    """
    Get user details by ID.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> User:
    """
    Update user information.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.email:
        # Check if email is already in use by another user
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id,
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
        db_user.email = user_data.email
    
    if user_data.first_name:
        db_user.first_name = user_data.first_name
    if user_data.last_name:
        db_user.last_name = user_data.last_name
    if user_data.display_name:
        db_user.display_name = user_data.display_name
    if user_data.role:
        db_user.role = user_data.role
    if user_data.status:
        db_user.status = user_data.status
    if user_data.max_websites:
        db_user.max_websites = user_data.max_websites
    if user_data.max_storage_gb:
        db_user.max_storage_gb = user_data.max_storage_gb
    if user_data.timezone:
        db_user.timezone = user_data.timezone
    if user_data.theme:
        db_user.theme = user_data.theme
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Delete a user.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()


# Team Endpoints

@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Team:
    """
    Create a new team.
    """
    # Generate slug if not provided
    if not team_data.slug:
        import re
        slug = re.sub(r'[^\w\-]', '-', team_data.name.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        team_data.slug = slug or "team"
    
    # Check if slug already exists
    existing_team = db.query(Team).filter(Team.slug == team_data.slug).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team slug already exists")
    
    # Create team
    db_team = Team(
        name=team_data.name,
        description=team_data.description,
        slug=team_data.slug,
        is_public=team_data.is_public,
        max_members=team_data.max_members,
        max_websites=team_data.max_websites,
    )
    
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    return db_team


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    limit: int = 100,
    offset: int = 0,
) -> List[Team]:
    """
    List all teams.
    """
    query = db.query(Team)
    query = query.offset(offset).limit(limit)
    return query.all()


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Team:
    """
    Get team details by ID.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Team:
    """
    Update team information.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team_data.name:
        db_team.name = team_data.name
    if team_data.description:
        db_team.description = team_data.description
    if team_data.slug:
        db_team.slug = team_data.slug
    if team_data.is_public is not None:
        db_team.is_public = team_data.is_public
    if team_data.max_members:
        db_team.max_members = team_data.max_members
    if team_data.max_websites:
        db_team.max_websites = team_data.max_websites
    
    db_team.updated_at = datetime.now()
    db.commit()
    db.refresh(db_team)
    
    return db_team


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Delete a team.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db.delete(db_team)
    db.commit()


@router.post("/teams/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: int,
    member_data: TeamMemberCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> TeamMember:
    """
    Add a user to a team.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db_user = db.query(User).filter(User.id == member_data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a member
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == member_data.user_id,
    ).first()
    
    if existing_member:
        # Update role if different
        if existing_member.role != member_data.role:
            existing_member.role = member_data.role
            existing_member.updated_at = datetime.now()
            db.commit()
        raise HTTPException(status_code=400, detail="User is already a team member")
    
    # Add member
    db_member = TeamMember(
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role,
        invited_at=datetime.now(),
        joined_at=datetime.now(),
    )
    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return db_member


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[TeamMember]:
    """
    List members of a team.
    """
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return members


@router.delete("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Remove a user from a team.
    """
    db_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
    ).first()
    
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    db.delete(db_member)
    db.commit()
