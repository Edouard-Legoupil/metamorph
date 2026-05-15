"""
Topic Management API Endpoints

API endpoints for managing topics and categories.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.database import get_db
from app.models.sql.settings import Topic, TopicCategory

router = APIRouter(prefix="/topics", tags=["topics"])


# Pydantic models

class TopicCreate(BaseModel):
    """Request model for creating a topic"""
    name: str = Field(..., min_length=2, max_length=200, description="Topic name")
    description: Optional[str] = Field(None, description="Topic description")
    slug: Optional[str] = Field(None, description="Topic slug (URL-friendly)")
    category: Optional[TopicCategory] = Field(TopicCategory.GENERAL, description="Topic category")
    parent_id: Optional[int] = Field(None, description="Parent topic ID")
    color: Optional[str] = Field(None, description="Hex color code")
    icon: Optional[str] = Field(None, description="Icon name")
    order_index: Optional[int] = Field(0, description="Order index")


class TopicUpdate(BaseModel):
    """Request model for updating a topic"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None)
    slug: Optional[str] = Field(None)
    category: Optional[TopicCategory] = Field(None)
    parent_id: Optional[int] = Field(None)
    color: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    order_index: Optional[int] = Field(None)
    is_active: Optional[bool] = Field(None)


class TopicResponse(BaseModel):
    """Response model for topic"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    category: TopicCategory
    parent_id: Optional[int]
    color: Optional[str]
    icon: Optional[str]
    order_index: int
    is_active: bool
    is_system: bool
    website_count: int
    file_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TopicTreeResponse(BaseModel):
    """Response model for topic tree (hierarchical)"""
    id: int
    name: str
    slug: str
    category: TopicCategory
    children: List["TopicTreeResponse"] = []
    
    class Config:
        from_attributes = True


# API Endpoints

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Topic:
    """
    Create a new topic.
    """
    # Generate slug if not provided
    if not topic_data.slug:
        import re
        slug = re.sub(r'[^\w\-]', '-', topic_data.name.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        topic_data.slug = slug or "topic"
    
    # Check if slug already exists
    existing_topic = db.query(Topic).filter(Topic.slug == topic_data.slug).first()
    if existing_topic:
        raise HTTPException(status_code=400, detail="Topic slug already exists")
    
    # Create topic
    db_topic = Topic(
        name=topic_data.name,
        slug=topic_data.slug,
        description=topic_data.description,
        category=topic_data.category,
        parent_id=topic_data.parent_id,
        color=topic_data.color,
        icon=topic_data.icon,
        order_index=topic_data.order_index,
    )
    
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    return db_topic


@router.get("/", response_model=List[TopicResponse])
async def list_topics(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    category_filter: Optional[TopicCategory] = None,
    is_active: Optional[bool] = True,
    parent_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Topic]:
    """
    List all topics.
    """
    query = db.query(Topic)
    
    if category_filter:
        query = query.filter(Topic.category == category_filter)
    if is_active is not None:
        query = query.filter(Topic.is_active == is_active)
    if parent_id is not None:
        if parent_id == 0:
            query = query.filter(Topic.parent_id.is_(None))
        else:
            query = query.filter(Topic.parent_id == parent_id)
    
    query = query.offset(offset).limit(limit).order_by(Topic.order_index, Topic.name)
    
    return query.all()


@router.get("/tree", response_model=List[TopicTreeResponse])
async def get_topic_tree(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    is_active: Optional[bool] = True,
) -> List[Topic]:
    """
    Get hierarchical topic tree.
    """
    def build_tree(topics: List[Topic], parent_id: Optional[int] = None) -> List[Dict]:
        """Recursively build topic tree"""
        tree = []
        for topic in topics:
            if topic.parent_id == parent_id and (is_active is None or topic.is_active == is_active):
                node = {
                    "id": topic.id,
                    "name": topic.name,
                    "slug": topic.slug,
                    "category": topic.category,
                    "children": build_tree(topics, topic.id),
                }
                tree.append(node)
        return tree
    
    all_topics = db.query(Topic).all()
    tree = build_tree(all_topics)
    
    # Convert to TopicTreeResponse models
    return [TopicTreeResponse(**node) for node in tree]


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Topic:
    """
    Get topic details by ID.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Topic:
    """
    Update topic information.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if topic_data.name:
        db_topic.name = topic_data.name
    if topic_data.description:
        db_topic.description = topic_data.description
    if topic_data.slug:
        db_topic.slug = topic_data.slug
    if topic_data.category:
        db_topic.category = topic_data.category
    if topic_data.parent_id:
        db_topic.parent_id = topic_data.parent_id
    if topic_data.color:
        db_topic.color = topic_data.color
    if topic_data.icon:
        db_topic.icon = topic_data.icon
    if topic_data.order_index:
        db_topic.order_index = topic_data.order_index
    if topic_data.is_active is not None:
        db_topic.is_active = topic_data.is_active
    
    db_topic.updated_at = datetime.now()
    db.commit()
    db.refresh(db_topic)
    
    return db_topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> None:
    """
    Delete a topic.
    """
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check if topic is system-defined
    if db_topic.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system topic")
    
    db.delete(db_topic)
    db.commit()


@router.get("/{topic_id}/websites")
async def get_topic_websites(
    topic_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Get websites associated with a topic.
    """
    from app.models.sql.website import WebsiteTopic
    
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get website associations
    associations = db.query(WebsiteTopic).filter(
        WebsiteTopic.topic_id == topic_id,
    ).offset(offset).limit(limit).all()
    
    website_ids = [assoc.website_id for assoc in associations]
    
    from app.models.sql.website import Website
    websites = db.query(Website).filter(Website.id.in_(website_ids)).all()
    
    return {
        "topic": {
            "id": db_topic.id,
            "name": db_topic.name,
            "slug": db_topic.slug,
        },
        "websites": websites,
        "total": len(websites),
    }
