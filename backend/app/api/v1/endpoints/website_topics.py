"""
Website-Topic Association API Endpoints

API endpoints for managing associations between websites and topics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.database import get_db
from app.models.sql.website import Website
from app.models.sql.settings import Topic, WebsiteTopic

router = APIRouter(prefix="/website-topics", tags=["website-topics"])


# Pydantic models

class WebsiteTopicBase(BaseModel):
    """Base model for website-topic association"""
    website_id: int = Field(..., description="Website ID")
    topic_id: int = Field(..., description="Topic ID")


class WebsiteTopicCreate(WebsiteTopicBase):
    """Request model for creating a website-topic association"""
    pass


class WebsiteTopicResponse(WebsiteTopicBase):
    """Response model for website-topic association"""
    id: int
    website_id: int
    topic_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebsiteTopicWithDetailsResponse(WebsiteTopicResponse):
    """Response model for website-topic association with details"""
    website: Optional[Dict[str, Any]] = None
    topic: Optional[Dict[str, Any]] = None


@router.get("/", response_model=List[WebsiteTopicResponse])
async def list_all_website_topics(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[WebsiteTopic]:
    """
    List all website-topic associations.
    """
    associations = db.query(WebsiteTopic).all()
    return associations


@router.post("/", response_model=WebsiteTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_website_topic(
    association: WebsiteTopicCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> WebsiteTopic:
    """
    Create a new website-topic association.
    """
    # Verify website exists
    db_website = db.query(Website).filter(Website.id == association.website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Verify topic exists
    db_topic = db.query(Topic).filter(Topic.id == association.topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check if association already exists
    existing_association = db.query(WebsiteTopic).filter(
        WebsiteTopic.website_id == association.website_id,
        WebsiteTopic.topic_id == association.topic_id,
    ).first()
    
    if existing_association:
        raise HTTPException(
            status_code=400,
            detail="This website is already associated with this topic"
        )
    
    db_association = WebsiteTopic(
        website_id=association.website_id,
        topic_id=association.topic_id,
    )
    
    db.add(db_association)
    db.commit()
    db.refresh(db_association)
    
    return db_association


@router.get("/{association_id}", response_model=WebsiteTopicResponse)
async def get_website_topic(
    association_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> WebsiteTopic:
    """
    Get a specific website-topic association by ID.
    """
    db_association = db.query(WebsiteTopic).filter(WebsiteTopic.id == association_id).first()
    if not db_association:
        raise HTTPException(status_code=404, detail="Association not found")
    return db_association


@router.delete("/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website_topic(
    association_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Remove a website-topic association by ID.
    """
    db_association = db.query(WebsiteTopic).filter(WebsiteTopic.id == association_id).first()
    if not db_association:
        raise HTTPException(status_code=404, detail="Association not found")
    
    db.delete(db_association)
    db.commit()


@router.get("/website/{website_id}", response_model=List[WebsiteTopicResponse])
async def list_website_topics(
    website_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[WebsiteTopic]:
    """
    List all topics associated with a specific website.
    """
    db_website = db.query(Website).filter(Website.id == website_id).first()
    if not db_website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    associations = db.query(WebsiteTopic).filter(
        WebsiteTopic.website_id == website_id
    ).all()
    return associations


@router.get("/topic/{topic_id}", response_model=List[WebsiteTopicResponse])
async def list_topic_websites(
    topic_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[WebsiteTopic]:
    """
    List all websites associated with a specific topic.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    associations = db.query(WebsiteTopic).filter(
        WebsiteTopic.topic_id == topic_id
    ).all()
    return associations
