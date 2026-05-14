"""
Knowledge Card API Endpoints (US-KCM-001, US-KCM-002)

API endpoints for knowledge card management, wiki blocks, validation, and discussion.
Corresponds to API endpoints defined in spec.md v3.0.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.database import get_db
from app.models.sql.knowledge_card import (
    KnowledgeCard, WikiBlock, ValidationCard, DiscussionThread, DiscussionComment,
    CardType, CardStatus, BlockType, VerificationState
)
from app.models.sql.user import User

router = APIRouter(prefix="/cards", tags=["knowledge_cards"])


# Pydantic models for request/response

class KnowledgeCardCreate(BaseModel):
    """Request model for creating a knowledge card"""
    card_type: CardType = Field(..., description="Type of knowledge card (KC-1 to KC-6)")
    title: str = Field(..., min_length=3, max_length=255, description="Card title")
    description: Optional[str] = Field(None, description="Card description")
    domain: str = Field(..., description="Knowledge domain")
    
    validity_start: Optional[datetime] = Field(None, description="Start of validity period")
    validity_end: Optional[datetime] = Field(None, description="End of validity period")
    
    source_website_ids: Optional[List[str]] = Field([], description="List of source website IDs")
    source_document_ids: Optional[List[str]] = Field([], description="List of source document IDs")
    source_entity_ids: Optional[List[str]] = Field([], description="List of source entity IDs")
    
    tags: Optional[List[str]] = Field([], description="Card tags")


class KnowledgeCardUpdate(BaseModel):
    """Request model for updating a knowledge card"""
    title: Optional[str] = Field(None, min_length=3, max_length=255, description="Card title")
    description: Optional[str] = Field(None, description="Card description")
    domain: Optional[str] = Field(None, description="Knowledge domain")
    
    validity_start: Optional[datetime] = Field(None, description="Start of validity period")
    validity_end: Optional[datetime] = Field(None, description="End of validity period")
    
    tags: Optional[List[str]] = Field(None, description="Card tags")


class KnowledgeCardResponse(BaseModel):
    """Response model for knowledge card"""
    id: str
    card_type: CardType
    title: str
    description: Optional[str]
    domain: str
    
    status: CardStatus
    validity_start: Optional[datetime]
    validity_end: Optional[datetime]
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    
    rejected_at: Optional[datetime]
    rejected_by: Optional[str]
    
    source_websites: List[str]
    source_documents: List[str]
    source_entities: List[str]
    
    tags: List[str]
    confidence_score: Optional[float]
    version: int
    
    blocks_count: int
    validation_cards_count: int
    discussion_threads_count: int
    
    class Config:
        from_attributes = True


class KnowledgeCardListResponse(BaseModel):
    """Response model for listing knowledge cards"""
    data: List[KnowledgeCardResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class WikiBlockCreate(BaseModel):
    """Request model for creating a wiki block"""
    section_name: str = Field(..., description="Section name")
    content: str = Field(..., description="Block content")
    word_limit: int = Field(..., gt=0, description="Word limit for this block")
    block_type: BlockType = Field(BlockType.TEXT, description="Type of block")
    
    template_query: Optional[str] = Field(None, description="Template query used")
    generated_from: Optional[str] = Field(None, description="Source document/block ID")
    
    source_website_id: Optional[str] = Field(None, description="Source website ID")
    source_file_id: Optional[str] = Field(None, description="Source file ID")
    source_document_id: Optional[str] = Field(None, description="Source document ID")
    
    maintenance_tags: Optional[List[str]] = Field([], description="Maintenance tags")
    is_live: bool = Field(False, description="Is this a live-updating block")


class WikiBlockUpdate(BaseModel):
    """Request model for updating a wiki block"""
    content: Optional[str] = Field(None, description="Block content")
    word_limit: Optional[int] = Field(None, gt=0, description="Word limit for this block")
    block_type: Optional[BlockType] = Field(None, description="Type of block")
    
    verification_state: Optional[VerificationState] = Field(None, description="Verification state")
    verification_notes: Optional[str] = Field(None, description="Verification notes")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    
    maintenance_tags: Optional[List[str]] = Field(None, description="Maintenance tags")
    is_live: Optional[bool] = Field(None, description="Is this a live-updating block")


class WikiBlockResponse(BaseModel):
    """Response model for wiki block"""
    id: str
    card_id: str
    section_name: str
    content: str
    word_limit: int
    block_type: BlockType
    
    template_query: Optional[str]
    generated_from: Optional[str]
    
    verification_state: VerificationState
    verified_at: Optional[datetime]
    verified_by: Optional[str]
    verification_notes: Optional[str]
    confidence_score: Optional[float]
    
    source_website_id: Optional[str]
    source_file_id: Optional[str]
    source_document_id: Optional[str]
    extraction_date: Optional[datetime]
    extraction_tool: Optional[str]
    
    maintenance_tags: List[str]
    is_live: bool
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    
    class Config:
        from_attributes = True


class ValidationCardCreate(BaseModel):
    """Request model for creating a validation card"""
    target_type: str = Field(..., description="Type of target (block, entity, card, triplet)")
    target_id: str = Field(..., description="ID of the target")
    
    current_value: Optional[str] = Field(None, description="Current value")
    proposed_value: Optional[str] = Field(None, description="Proposed value")
    diff: Optional[str] = Field(None, description="Diff between values")
    
    sensitivity: str = Field("medium", description="Sensitivity level (low, medium, high)")
    assigned_tier: Optional[str] = Field(None, description="Review tier (tier_1, tier_2, tier_3)")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    
    evidence: Optional[List[str]] = Field([], description="Evidence sources")
    provenance: Optional[Dict[str, Any]] = Field({}, description="Provenance information")
    source_reliability: Optional[str] = Field(None, description="Source reliability")
    contradiction_type: Optional[str] = Field(None, description="Type of contradiction")


class ValidationCardResponse(BaseModel):
    """Response model for validation card"""
    id: str
    target_type: str
    target_id: str
    card_id: Optional[str]
    
    current_value: Optional[str]
    proposed_value: Optional[str]
    diff: Optional[str]
    
    status: str
    sensitivity: str
    assigned_tier: Optional[str]
    confidence_score: Optional[float]
    
    evidence: List[str]
    provenance: Dict[str, Any]
    source_reliability: Optional[str]
    contradiction_type: Optional[str]
    
    assigned_to: Optional[str]
    assigned_at: Optional[datetime]
    assigned_by: Optional[str]
    due_date: Optional[datetime]
    
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution: Optional[str]
    resolution_type: Optional[str]
    
    created_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True


class DiscussionThreadCreate(BaseModel):
    """Request model for creating a discussion thread"""
    title: str = Field(..., description="Thread title")
    topic: Optional[str] = Field(None, description="Thread topic")
    
    linked_card_id: Optional[str] = Field(None, description="Linked knowledge card ID")
    linked_block_id: Optional[str] = Field(None, description="Linked wiki block ID")
    linked_entity_id: Optional[str] = Field(None, description="Linked entity ID")
    
    evidence_quality: Optional[str] = Field(None, description="Evidence quality (low, medium, high)")
    policy_compliance: Optional[bool] = Field(None, description="Policy compliance")
    
    mentions: Optional[List[str]] = Field([], description="User mentions")
    initial_comment: str = Field(..., description="Initial comment content")


class DiscussionThreadResponse(BaseModel):
    """Response model for discussion thread"""
    id: str
    title: str
    topic: Optional[str]
    
    status: str
    consensus_result: Optional[str]
    resolution_summary: Optional[str]
    
    linked_card_id: Optional[str]
    linked_block_id: Optional[str]
    linked_entity_id: Optional[str]
    
    evidence_quality: Optional[str]
    policy_compliance: Optional[bool]
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    
    watchers: List[str]
    comment_count: int
    
    class Config:
        from_attributes = True


class DiscussionCommentCreate(BaseModel):
    """Request model for creating a discussion comment"""
    content: str = Field(..., description="Comment content")
    
    evidence_quality: Optional[str] = Field(None, description="Evidence quality (low, medium, high)")
    policy_compliance: Optional[bool] = Field(None, description="Policy compliance")
    
    mentions: Optional[List[str]] = Field([], description="User mentions")
    attachments: Optional[List[Dict[str, str]]] = Field([], description="Attachments")


class DiscussionCommentResponse(BaseModel):
    """Response model for discussion comment"""
    id: str
    thread_id: str
    content: str
    is_edited: bool
    
    evidence_quality: Optional[str]
    policy_compliance: Optional[bool]
    
    mentions: List[str]
    attachments: List[Dict[str, str]]
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    
    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    """Request model for approving a knowledge card"""
    validity_period: Optional[Dict[str, datetime]] = Field(None, description="Validity period")
    approval_notes: Optional[str] = Field(None, description="Approval notes")


class RejectionRequest(BaseModel):
    """Request model for rejecting a knowledge card"""
    rejection_reason: str = Field(..., description="Rejection reason")
    suggested_actions: Optional[List[str]] = Field([], description="Suggested actions")


class VerificationRequest(BaseModel):
    """Request model for verifying a wiki block"""
    verification_state: VerificationState = Field(..., description="Verification state")
    verification_notes: Optional[str] = Field(None, description="Verification notes")
    confidence_score: Optional[float] = Field(None, description="Confidence score")


class FlagRequest(BaseModel):
    """Request model for flagging a wiki block"""
    verification_state: VerificationState = Field(..., description="Verification state")
    flag_reason: str = Field(..., description="Flag reason")
    suggested_action: Optional[str] = Field(None, description="Suggested action")
    maintenance_tags: Optional[List[str]] = Field([], description="Maintenance tags")


class AssignmentRequest(BaseModel):
    """Request model for assigning a validation card"""
    assigned_to: str = Field(..., description="User ID to assign to")
    assigned_tier: str = Field(..., description="Review tier (tier_1, tier_2, tier_3)")
    priority: Optional[str] = Field("normal", description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Due date")


class ResolutionRequest(BaseModel):
    """Request model for resolving a validation card"""
    resolution: str = Field(..., description="Resolution description")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    update_target: bool = Field(True, description="Whether to update the target")
    notification_message: Optional[str] = Field(None, description="Notification message")


class MergeRequest(BaseModel):
    """Request model for merging a validation card"""
    resolution: str = Field(..., description="Resolution type")
    merged_value: str = Field(..., description="Merged value")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    update_target: bool = Field(True, description="Whether to update the target")
    new_evidence: Optional[List[str]] = Field([], description="Additional evidence")


class EscalationRequest(BaseModel):
    """Request model for escalating a validation card"""
    escalation_reason: str = Field(..., description="Escalation reason")
    escalate_to: str = Field(..., description="Tier to escalate to")
    escalation_notes: Optional[str] = Field(None, description="Escalation notes")
    urgency: Optional[str] = Field("normal", description="Urgency level")


# Helper functions

def generate_id(prefix: str = "card") -> str:
    """Generate a unique ID"""
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# API Endpoints

@router.post("/", response_model=KnowledgeCardResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_card(
    card_data: KnowledgeCardCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> KnowledgeCard:
    """
    Create a new knowledge card.
    
    Acceptance Criteria (US-KCM-001):
    - Create knowledge card with metadata
    - Support all card types (KC-1 to KC-6)
    - Track source information
    """
    # Generate card ID
    card_id = generate_id("card")
    
    # Create knowledge card
    db_card = KnowledgeCard(
        id=card_id,
        card_type=card_data.card_type,
        title=card_data.title,
        description=card_data.description,
        domain=card_data.domain,
        status=CardStatus.DRAFT,
        validity_start=card_data.validity_start,
        validity_end=card_data.validity_end,
        source_websites=card_data.source_website_ids,
        source_documents=card_data.source_document_ids,
        source_entities=card_data.source_entity_ids,
        tags=card_data.tags,
        created_by=api_key,  # Using API key as user ID for now
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    return db_card


@router.get("/", response_model=KnowledgeCardListResponse)
async def list_knowledge_cards(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    card_type: Optional[CardType] = None,
    domain: Optional[str] = None,
    status: Optional[CardStatus] = None,
    validity: Optional[str] = None,  # valid, expired, expiring_soon
    search: Optional[str] = None,
    source_website: Optional[str] = None,
    created_by: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    List all knowledge cards with filtering.
    
    Acceptance Criteria:
    - List knowledge cards with pagination
    - Filter by card type, domain, status, etc.
    - Support search functionality
    """
    query = db.query(KnowledgeCard)
    
    # Apply filters
    if card_type:
        query = query.filter(KnowledgeCard.card_type == card_type)
    if domain:
        query = query.filter(KnowledgeCard.domain == domain)
    if status:
        query = query.filter(KnowledgeCard.status == status)
    if source_website:
        query = query.filter(KnowledgeCard.source_websites.contains([source_website]))
    if created_by:
        query = query.filter(KnowledgeCard.created_by == created_by)
    
    # Apply validity filter
    now = datetime.now()
    if validity == "valid":
        query = query.filter(
            KnowledgeCard.validity_start <= now,
            KnowledgeCard.validity_end >= now
        )
    elif validity == "expired":
        query = query.filter(KnowledgeCard.validity_end < now)
    elif validity == "expiring_soon":
        # Expires within next 7 days
        expiry_threshold = now + timedelta(days=7)
        query = query.filter(
            KnowledgeCard.validity_end >= now,
            KnowledgeCard.validity_end <= expiry_threshold
        )
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            KnowledgeCard.title.ilike(search_pattern) |
            KnowledgeCard.description.ilike(search_pattern)
        )
    
    # Pagination
    total = query.count()
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    cards = query.all()
    
    return {
        "data": cards,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": page * page_size < total
    }


@router.get("/{card_id}", response_model=KnowledgeCardResponse)
async def get_knowledge_card(
    card_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> KnowledgeCard:
    """
    Get knowledge card details by ID.
    """
    db_card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Knowledge card not found")
    return db_card


@router.patch("/{card_id}", response_model=KnowledgeCardResponse)
async def update_knowledge_card(
    card_id: str,
    card_data: KnowledgeCardUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> KnowledgeCard:
    """
    Update knowledge card properties.
    """
    db_card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Knowledge card not found")
    
    # Update fields
    if card_data.title:
        db_card.title = card_data.title
    if card_data.description:
        db_card.description = card_data.description
    if card_data.domain:
        db_card.domain = card_data.domain
    if card_data.validity_start:
        db_card.validity_start = card_data.validity_start
    if card_data.validity_end:
        db_card.validity_end = card_data.validity_end
    if card_data.tags is not None:
        db_card.tags = card_data.tags
    
    db_card.updated_at = datetime.now()
    db_card.updated_by = api_key
    
    db.commit()
    db.refresh(db_card)
    
    return db_card


@router.post("/{card_id}/approve", response_model=KnowledgeCardResponse)
async def approve_knowledge_card(
    card_id: str,
    approval_data: ApprovalRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> KnowledgeCard:
    """
    Approve a knowledge card for use.
    
    Acceptance Criteria:
    - Transition card to approved status
    - Set validity period
    - Track approval metadata
    """
    db_card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Knowledge card not found")
    
    if db_card.status != CardStatus.DRAFT and db_card.status != CardStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=400, 
            detail=f"Card cannot be approved from status: {db_card.status}"
        )
    
    # Update validity period if provided
    if approval_data.validity_period:
        if approval_data.validity_period.get("start"):
            db_card.validity_start = approval_data.validity_period["start"]
        if approval_data.validity_period.get("end"):
            db_card.validity_end = approval_data.validity_period["end"]
    
    # Update approval metadata
    db_card.status = CardStatus.APPROVED
    db_card.approved_at = datetime.now()
    db_card.approved_by = api_key
    db_card.approval_notes = approval_data.approval_notes
    
    db.commit()
    db.refresh(db_card)
    
    return db_card


@router.post("/{card_id}/reject", response_model=KnowledgeCardResponse)
async def reject_knowledge_card(
    card_id: str,
    rejection_data: RejectionRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> KnowledgeCard:
    """
    Reject a knowledge card.
    
    Acceptance Criteria:
    - Transition card to rejected status
    - Capture rejection reason
    - Track rejection metadata
    """
    db_card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Knowledge card not found")
    
    if db_card.status != CardStatus.DRAFT and db_card.status != CardStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=400, 
            detail=f"Card cannot be rejected from status: {db_card.status}"
        )
    
    # Update rejection metadata
    db_card.status = CardStatus.REJECTED
    db_card.rejected_at = datetime.now()
    db_card.rejected_by = api_key
    db_card.rejection_reason = rejection_data.rejection_reason
    
    db.commit()
    db.refresh(db_card)
    
    return db_card


@router.post("/{card_id}/blocks", response_model=WikiBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_wiki_block(
    card_id: str,
    block_data: WikiBlockCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> WikiBlock:
    """
    Create a new wiki block in a knowledge card.
    
    Acceptance Criteria (US-KCM-002):
    - Create wiki block with content
    - Track word limits and templates
    - Support provenance tracking
    """
    # Check if card exists
    db_card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Knowledge card not found")
    
    # Generate block ID
    block_id = generate_id("block")
    
    # Create wiki block
    db_block = WikiBlock(
        id=block_id,
        card_id=card_id,
        section_name=block_data.section_name,
        content=block_data.content,
        word_limit=block_data.word_limit,
        block_type=block_data.block_type,
        template_query=block_data.template_query,
        generated_from=block_data.generated_from,
        source_website_id=block_data.source_website_id,
        source_file_id=block_data.source_file_id,
        source_document_id=block_data.source_document_id,
        maintenance_tags=block_data.maintenance_tags,
        is_live=block_data.is_live,
        created_by=api_key,
    )
    
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    
    return db_block


@router.get("/{card_id}/blocks", response_model=List[WikiBlockResponse])
async def list_wiki_blocks(
    card_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[WikiBlock]:
    """
    List all wiki blocks in a knowledge card.
    """
    # Check if card exists
    db_card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Knowledge card not found")
    
    blocks = db.query(WikiBlock).filter(WikiBlock.card_id == card_id).all()
    return blocks


@router.get("/{card_id}/blocks/{block_id}", response_model=WikiBlockResponse)
async def get_wiki_block(
    card_id: str,
    block_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> WikiBlock:
    """
    Get wiki block details.
    """
    db_block = db.query(WikiBlock).filter(
        WikiBlock.card_id == card_id,
        WikiBlock.id == block_id
    ).first()
    
    if not db_block:
        raise HTTPException(status_code=404, detail="Wiki block not found")
    
    return db_block


@router.patch("/{card_id}/blocks/{block_id}", response_model=WikiBlockResponse)
async def update_wiki_block(
    card_id: str,
    block_id: str,
    block_data: WikiBlockUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> WikiBlock:
    """
    Update wiki block content and properties.
    
    Acceptance Criteria:
    - Update block content
    - Change verification state
    - Track modification history
    """
    db_block = db.query(WikiBlock).filter(
        WikiBlock.card_id == card_id,
        WikiBlock.id == block_id
    ).first()
    
    if not db_block:
        raise HTTPException(status_code=404, detail="Wiki block not found")
    
    # Update fields
    if block_data.content:
        db_block.content = block_data.content
    if block_data.word_limit:
        db_block.word_limit = block_data.word_limit
    if block_data.block_type:
        db_block.block_type = block_data.block_type
    if block_data.verification_state:
        db_block.verification_state = block_data.verification_state
    if block_data.verification_notes:
        db_block.verification_notes = block_data.verification_notes
    if block_data.confidence_score:
        db_block.confidence_score = block_data.confidence_score
    if block_data.maintenance_tags is not None:
        db_block.maintenance_tags = block_data.maintenance_tags
    if block_data.is_live is not None:
        db_block.is_live = block_data.is_live
    
    db_block.updated_at = datetime.now()
    db_block.updated_by = api_key
    
    db.commit()
    db.refresh(db_block)
    
    return db_block


@router.post("/{card_id}/blocks/{block_id}/verify", response_model=WikiBlockResponse)
async def verify_wiki_block(
    card_id: str,
    block_id: str,
    verification_data: VerificationRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> WikiBlock:
    """
    Mark a wiki block as verified.
    
    Acceptance Criteria:
    - Update verification state
    - Track verification metadata
    - Set confidence score
    """
    db_block = db.query(WikiBlock).filter(
        WikiBlock.card_id == card_id,
        WikiBlock.id == block_id
    ).first()
    
    if not db_block:
        raise HTTPException(status_code=404, detail="Wiki block not found")
    
    # Update verification metadata
    db_block.verification_state = verification_data.verification_state
    db_block.verified_at = datetime.now()
    db_block.verified_by = api_key
    db_block.verification_notes = verification_data.verification_notes
    db_block.confidence_score = verification_data.confidence_score
    
    db.commit()
    db.refresh(db_block)
    
    return db_block


@router.post("/{card_id}/blocks/{block_id}/flag", response_model=WikiBlockResponse)
async def flag_wiki_block(
    card_id: str,
    block_id: str,
    flag_data: FlagRequest,
    db: Session = Depends(get_api_key),
    api_key: str = Depends(get_api_key),
) -> WikiBlock:
    """
    Flag a wiki block for review.
    
    Acceptance Criteria:
    - Set verification state to disputed/flagged
    - Capture flag reason
    - Add maintenance tags
    """
    db_block = db.query(WikiBlock).filter(
        WikiBlock.card_id == card_id,
        WikiBlock.id == block_id
    ).first()
    
    if not db_block:
        raise HTTPException(status_code=404, detail="Wiki block not found")
    
    # Update flag metadata
    db_block.verification_state = flag_data.verification_state
    db_block.verification_notes = flag_data.flag_reason
    
    # Add maintenance tags
    if flag_data.maintenance_tags:
        db_block.maintenance_tags = list(set(db_block.maintenance_tags + flag_data.maintenance_tags))
    
    db.commit()
    db.refresh(db_block)
    
    return db_block


# Validation Card Endpoints

@router.post("/validation/cards", response_model=ValidationCardResponse, status_code=status.HTTP_201_CREATED)
async def create_validation_card(
    validation_data: ValidationCardCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Create a new validation card.
    
    Acceptance Criteria (US-VAL-001):
    - Create validation card for content conflicts
    - Track target information
    - Capture evidence and provenance
    """
    # Generate validation card ID
    validation_id = generate_id("val")
    
    # Create validation card
    db_validation = ValidationCard(
        id=validation_id,
        target_type=validation_data.target_type,
        target_id=validation_data.target_id,
        card_id=validation_data.card_id,  # Can be None for non-card targets
        
        current_value=validation_data.current_value,
        proposed_value=validation_data.proposed_value,
        diff=validation_data.diff,
        
        status="open",
        sensitivity=validation_data.sensitivity,
        assigned_tier=validation_data.assigned_tier,
        confidence_score=validation_data.confidence_score,
        
        evidence=validation_data.evidence,
        provenance=validation_data.provenance,
        source_reliability=validation_data.source_reliability,
        contradiction_type=validation_data.contradiction_type,
        
        created_by=api_key,
    )
    
    db.add(db_validation)
    db.commit()
    db.refresh(db_validation)
    
    return db_validation


@router.get("/validation/cards", response_model=List[ValidationCardResponse])
async def list_validation_cards(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    status: Optional[str] = None,
    assigned_tier: Optional[str] = None,
    sensitivity: Optional[str] = None,
    target_type: Optional[str] = None,
    contradiction_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[ValidationCard]:
    """
    List validation cards with filtering.
    """
    query = db.query(ValidationCard)
    
    # Apply filters
    if status:
        query = query.filter(ValidationCard.status == status)
    if assigned_tier:
        query = query.filter(ValidationCard.assigned_tier == assigned_tier)
    if sensitivity:
        query = query.filter(ValidationCard.sensitivity == sensitivity)
    if target_type:
        query = query.filter(ValidationCard.target_type == target_type)
    if contradiction_type:
        query = query.filter(ValidationCard.contradiction_type == contradiction_type)
    if assigned_to:
        query = query.filter(ValidationCard.assigned_to == assigned_to)
    
    # Pagination
    validation_cards = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return validation_cards


@router.get("/validation/cards/{validation_id}", response_model=ValidationCardResponse)
async def get_validation_card(
    validation_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Get validation card details.
    """
    db_validation = db.query(ValidationCard).filter(ValidationCard.id == validation_id).first()
    if not db_validation:
        raise HTTPException(status_code=404, detail="Validation card not found")
    return db_validation


@router.post("/validation/cards/{validation_id}/assign", response_model=ValidationCardResponse)
async def assign_validation_card(
    validation_id: str,
    assignment_data: AssignmentRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Assign a validation card to a reviewer.
    
    Acceptance Criteria:
    - Assign to specific user/tier
    - Set priority and due date
    - Track assignment metadata
    """
    db_validation = db.query(ValidationCard).filter(ValidationCard.id == validation_id).first()
    if not db_validation:
        raise HTTPException(status_code=404, detail="Validation card not found")
    
    if db_validation.status != "open":
        raise HTTPException(
            status_code=400,
            detail=f"Validation card cannot be assigned from status: {db_validation.status}"
        )
    
    # Update assignment metadata
    db_validation.status = "under_review"
    db_validation.assigned_to = assignment_data.assigned_to
    db_validation.assigned_tier = assignment_data.assigned_tier
    db_validation.assigned_at = datetime.now()
    db_validation.assigned_by = api_key
    db_validation.due_date = assignment_data.due_date
    
    db.commit()
    db.refresh(db_validation)
    
    return db_validation


@router.post("/validation/cards/{validation_id}/approve", response_model=ValidationCardResponse)
async def approve_validation_card(
    validation_id: str,
    resolution_data: ResolutionRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Approve a validation card.
    
    Acceptance Criteria:
    - Resolve validation card as approved
    - Optionally update target content
    - Track resolution metadata
    """
    db_validation = db.query(ValidationCard).filter(ValidationCard.id == validation_id).first()
    if not db_validation:
        raise HTTPException(status_code=404, detail="Validation card not found")
    
    if db_validation.status not in ["open", "under_review"]:
        raise HTTPException(
            status_code=400,
            detail=f"Validation card cannot be approved from status: {db_validation.status}"
        )
    
    # Update resolution metadata
    db_validation.status = "approved"
    db_validation.resolved_at = datetime.now()
    db_validation.resolved_by = api_key
    db_validation.resolution = resolution_data.resolution
    db_validation.resolution_type = "approved"
    db_validation.confidence_score = resolution_data.confidence_score
    
    # If requested, update the target
    if resolution_data.update_target and db_validation.target_type == "block":
        # This would update the wiki block content
        # Implementation would depend on specific requirements
        pass
    
    db.commit()
    db.refresh(db_validation)
    
    return db_validation


@router.post("/validation/cards/{validation_id}/reject", response_model=ValidationCardResponse)
async def reject_validation_card(
    validation_id: str,
    rejection_data: RejectionRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Reject a validation card.
    
    Acceptance Criteria:
    - Resolve validation card as rejected
    - Capture rejection reason and suggested actions
    - Track resolution metadata
    """
    db_validation = db.query(ValidationCard).filter(ValidationCard.id == validation_id).first()
    if not db_validation:
        raise HTTPException(status_code=404, detail="Validation card not found")
    
    if db_validation.status not in ["open", "under_review"]:
        raise HTTPException(
            status_code=400,
            detail=f"Validation card cannot be rejected from status: {db_validation.status}"
        )
    
    # Update resolution metadata
    db_validation.status = "rejected"
    db_validation.resolved_at = datetime.now()
    db_validation.resolved_by = api_key
    db_validation.resolution = rejection_data.rejection_reason
    db_validation.resolution_type = "rejected"
    
    db.commit()
    db.refresh(db_validation)
    
    return db_validation


@router.post("/validation/cards/{validation_id}/merge", response_model=ValidationCardResponse)
async def merge_validation_card(
    validation_id: str,
    merge_data: MergeRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Merge a validation card.
    
    Acceptance Criteria:
    - Resolve validation card as merged
    - Update target with merged value
    - Track resolution metadata and new evidence
    """
    db_validation = db.query(ValidationCard).filter(ValidationCard.id == validation_id).first()
    if not db_validation:
        raise HTTPException(status_code=404, detail="Validation card not found")
    
    if db_validation.status not in ["open", "under_review"]:
        raise HTTPException(
            status_code=400,
            detail=f"Validation card cannot be merged from status: {db_validation.status}"
        )
    
    # Update resolution metadata
    db_validation.status = "merged"
    db_validation.resolved_at = datetime.now()
    db_validation.resolved_by = api_key
    db_validation.resolution = merge_data.resolution
    db_validation.resolution_type = "merged"
    db_validation.confidence_score = merge_data.confidence_score
    
    # Update evidence if provided
    if merge_data.new_evidence:
        current_evidence = db_validation.evidence or []
        db_validation.evidence = current_evidence + merge_data.new_evidence
    
    # If requested, update the target
    if merge_data.update_target and db_validation.target_type == "block":
        # This would update the wiki block content with merged_value
        # Implementation would depend on specific requirements
        pass
    
    db.commit()
    db.refresh(db_validation)
    
    return db_validation


@router.post("/validation/cards/{validation_id}/escalate", response_model=ValidationCardResponse)
async def escalate_validation_card(
    validation_id: str,
    escalation_data: EscalationRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> ValidationCard:
    """
    Escalate a validation card.
    
    Acceptance Criteria:
    - Escalate validation card to higher tier
    - Capture escalation reason and notes
    - Track escalation metadata
    """
    db_validation = db.query(ValidationCard).filter(ValidationCard.id == validation_id).first()
    if not db_validation:
        raise HTTPException(status_code=404, detail="Validation card not found")
    
    if db_validation.status not in ["open", "under_review"]:
        raise HTTPException(
            status_code=400,
            detail=f"Validation card cannot be escalated from status: {db_validation.status}"
        )
    
    # Update escalation metadata
    db_validation.status = "escalated"
    db_validation.assigned_tier = escalation_data.escalate_to
    db_validation.assigned_at = datetime.now()
    db_validation.assigned_by = api_key
    db_validation.resolution = escalation_data.escalation_reason
    db_validation.resolution_type = "escalated"
    
    # Add escalation notes to evidence
    escalation_note = {
        "type": "escalation",
        "reason": escalation_data.escalation_reason,
        "notes": escalation_data.escalation_notes,
        "urgency": escalation_data.urgency,
        "escalated_by": api_key,
        "escalated_at": str(datetime.now())
    }
    
    current_evidence = db_validation.evidence or []
    db_validation.evidence = current_evidence + [escalation_note]
    
    db.commit()
    db.refresh(db_validation)
    
    return db_validation


# Discussion Thread Endpoints

@router.post("/discussion/threads", response_model=DiscussionThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion_thread(
    thread_data: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> DiscussionThread:
    """
    Create a new discussion thread.
    
    Acceptance Criteria (US-DIS-001):
    - Create discussion thread
    - Link to knowledge entities
    - Capture initial comment
    """
    # Generate thread ID
    thread_id = generate_id("thread")
    
    # Create discussion thread
    db_thread = DiscussionThread(
        id=thread_id,
        title=thread_data.title,
        topic=thread_data.topic,
        
        status="open",
        
        linked_card_id=thread_data.linked_card_id,
        linked_block_id=thread_data.linked_block_id,
        linked_entity_id=thread_data.linked_entity_id,
        
        evidence_quality=thread_data.evidence_quality,
        policy_compliance=thread_data.policy_compliance,
        
        created_by=api_key,
    )
    
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    
    # Create initial comment
    comment_id = generate_id("comment")
    db_comment = DiscussionComment(
        id=comment_id,
        thread_id=thread_id,
        content=thread_data.initial_comment,
        evidence_quality=thread_data.evidence_quality,
        policy_compliance=thread_data.policy_compliance,
        mentions=thread_data.mentions,
        created_by=api_key,
    )
    
    db.add(db_comment)
    db.commit()
    
    return db_thread


@router.get("/discussion/threads", response_model=List[DiscussionThreadResponse])
async def list_discussion_threads(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    status: Optional[str] = None,
    linked_card_id: Optional[str] = None,
    linked_block_id: Optional[str] = None,
    created_by: Optional[str] = None,
    watcher: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> List[DiscussionThread]:
    """
    List discussion threads with filtering.
    """
    query = db.query(DiscussionThread)
    
    # Apply filters
    if status:
        query = query.filter(DiscussionThread.status == status)
    if linked_card_id:
        query = query.filter(DiscussionThread.linked_card_id == linked_card_id)
    if linked_block_id:
        query = query.filter(DiscussionThread.linked_block_id == linked_block_id)
    if created_by:
        query = query.filter(DiscussionThread.created_by == created_by)
    if watcher:
        query = query.filter(DiscussionThread.watchers.contains([watcher]))
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            DiscussionThread.title.ilike(search_pattern) |
            DiscussionThread.topic.ilike(search_pattern)
        )
    
    # Pagination
    threads = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return threads


@router.get("/discussion/threads/{thread_id}", response_model=DiscussionThreadResponse)
async def get_discussion_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    include_comments: bool = True,
    comment_page: int = 1,
    comment_page_size: int = 50,
) -> Dict[str, Any]:
    """
    Get discussion thread details with comments.
    """
    db_thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    
    result = {"thread": db_thread}
    
    if include_comments:
        comment_query = db.query(DiscussionComment).filter(
            DiscussionComment.thread_id == thread_id
        ).order_by(DiscussionComment.created_at.asc())
        
        comments = comment_query.offset((comment_page - 1) * comment_page_size).limit(comment_page_size).all()
        result["comments"] = comments
        result["comment_count"] = comment_query.count()
    
    return result


@router.post("/discussion/threads/{thread_id}/comments", response_model=DiscussionCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_discussion_comment(
    thread_id: str,
    comment_data: DiscussionCommentCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> DiscussionComment:
    """
    Add a comment to a discussion thread.
    
    Acceptance Criteria:
    - Add comment to thread
    - Track mentions and attachments
    - Update thread activity
    """
    db_thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    
    # Generate comment ID
    comment_id = generate_id("comment")
    
    # Create comment
    db_comment = DiscussionComment(
        id=comment_id,
        thread_id=thread_id,
        content=comment_data.content,
        evidence_quality=comment_data.evidence_quality,
        policy_compliance=comment_data.policy_compliance,
        mentions=comment_data.mentions,
        attachments=comment_data.attachments,
        created_by=api_key,
    )
    
    db.add(db_comment)
    
    # Update thread
    db_thread.updated_at = datetime.now()
    db_thread.updated_by = api_key
    
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@router.patch("/discussion/threads/{thread_id}", response_model=DiscussionThreadResponse)
async def update_discussion_thread_status(
    thread_id: str,
    status_update: Dict[str, Any],
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> DiscussionThread:
    """
    Update discussion thread status.
    
    Acceptance Criteria:
    - Change thread status
    - Capture resolution information
    - Track consensus results
    """
    db_thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    
    # Update status
    if "status" in status_update:
        db_thread.status = status_update["status"]
    if "consensus_result" in status_update:
        db_thread.consensus_result = status_update["consensus_result"]
    if "resolution_summary" in status_update:
        db_thread.resolution_summary = status_update["resolution_summary"]
    
    # If resolving, set resolution metadata
    if status_update.get("status") in ["consensus_reached", "resolved", "no_consensus", "rejected"]:
        db_thread.resolved_at = datetime.now()
        db_thread.resolved_by = api_key
    
    db_thread.updated_at = datetime.now()
    db_thread.updated_by = api_key
    
    db.commit()
    db.refresh(db_thread)
    
    return db_thread


@router.post("/discussion/threads/{thread_id}/watch", response_model=Dict[str, Any])
async def watch_discussion_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Start watching a discussion thread.
    
    Acceptance Criteria:
    - Add user to watchers list
    - Prevent duplicate watchers
    - Return updated watcher count
    """
    db_thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    
    # Add watcher if not already watching
    if api_key not in db_thread.watchers:
        db_thread.watchers.append(api_key)
        db.commit()
    
    return {
        "success": True,
        "thread_id": thread_id,
        "is_watching": True,
        "watcher_count": len(db_thread.watchers)
    }


@router.delete("/discussion/threads/{thread_id}/watch", response_model=Dict[str, Any])
async def unwatch_discussion_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Stop watching a discussion thread.
    
    Acceptance Criteria:
    - Remove user from watchers list
    - Handle user not watching gracefully
    - Return updated watcher count
    """
    db_thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    
    # Remove watcher if watching
    if api_key in db_thread.watchers:
        db_thread.watchers.remove(api_key)
        db.commit()
    
    return {
        "success": True,
        "thread_id": thread_id,
        "is_watching": False,
        "watcher_count": len(db_thread.watchers)
    }