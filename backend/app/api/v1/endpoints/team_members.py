"""
Team Member Management API Endpoints

API endpoints for managing team memberships.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.database import get_db
from app.models.sql.user import User, Team, TeamMember, UserRole

router = APIRouter(prefix="/team-members", tags=["team-members"])


# Pydantic models

class TeamMemberBase(BaseModel):
    """Base model for team member"""
    team_id: int = Field(..., description="Team ID")
    user_id: int = Field(..., description="User ID")
    role: UserRole = Field(UserRole.VIEWER, description="Member role in the team")
    is_active: bool = Field(True, description="Whether the membership is active")


class TeamMemberCreate(TeamMemberBase):
    """Request model for creating a team member"""
    invited_by_id: Optional[int] = Field(None, description="ID of the user who invited this member")


class TeamMemberResponse(TeamMemberBase):
    """Response model for team member"""
    id: int
    team_id: int
    user_id: int
    role: UserRole
    is_active: bool
    invited_by_id: Optional[int]
    invited_at: Optional[datetime]
    joined_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamMemberWithDetailsResponse(TeamMemberResponse):
    """Response model for team member with user and team details"""
    user: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None


@router.get("/", response_model=List[TeamMemberResponse])
async def list_all_team_members(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[TeamMember]:
    """
    List all team members across all teams.
    """
    members = db.query(TeamMember).all()
    return members


@router.post("/", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member: TeamMemberCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> TeamMember:
    """
    Create a new team member association.
    """
    # Verify team exists
    db_team = db.query(Team).filter(Team.id == member.team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify user exists
    db_user = db.query(User).filter(User.id == member.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a member of this team
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == member.team_id,
        TeamMember.user_id == member.user_id,
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this team"
        )
    
    db_member = TeamMember(
        team_id=member.team_id,
        user_id=member.user_id,
        role=member.role,
        is_active=member.is_active,
        invited_by_id=member.invited_by_id,
        invited_at=datetime.now(),
        joined_at=datetime.now(),
    )
    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return db_member


@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> TeamMember:
    """
    Get a specific team member by ID.
    """
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    return db_member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Remove a team member by ID.
    """
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    db.delete(db_member)
    db.commit()
