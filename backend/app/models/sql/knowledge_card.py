"""
Knowledge Card Models (US-KCM-001, US-KCM-002)

SQL models for knowledge cards, wiki blocks, validation, and discussion.
Corresponds to the v3.0 data model for knowledge management.
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum as PyEnum

from .base import Base


class CardType(PyEnum):
    """Type of knowledge card"""
    KC1 = "KC-1"  # Donor Intelligence
    KC2 = "KC-2"  # Field Context
    KC3 = "KC-3"  # Outcome Evidence
    KC4 = "KC-4"  # Partner Capacity
    KC5 = "KC-5"  # Track Record
    KC6 = "KC-6"  # Crisis Political Economy


class CardStatus(PyEnum):
    """Status of a knowledge card"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class BlockType(PyEnum):
    """Type of wiki block"""
    TEXT = "text"
    TABLE = "table"
    LIST = "list"
    QUOTE = "quote"
    CODE = "code"
    IMAGE = "image"
    CHART = "chart"


class VerificationState(PyEnum):
    """Verification state of a block"""
    PENDING = "pending"
    AUTO_ACCEPTED = "auto_accepted"
    ACCEPTED = "accepted"
    DISPUTED = "disputed"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class KnowledgeCard(Base):
    """Knowledge Card model - structured knowledge representation"""
    __tablename__ = "knowledge_cards"
    
    id = Column(String(50), primary_key=True, index=True)
    card_type = Column(Enum(CardType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(50), nullable=False)  # geographic, crisis, demographics, etc.
    
    status = Column(Enum(CardStatus), default=CardStatus.DRAFT, nullable=False)
    
    # Validity period
    validity_start = Column(DateTime, nullable=True)
    validity_end = Column(DateTime, nullable=True)
    
    # Creation and modification tracking
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    updated_by = Column(String(50), nullable=True)
    
    # Approval tracking
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(50), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Rejection tracking
    rejected_at = Column(DateTime, nullable=True)
    rejected_by = Column(String(50), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Source tracking
    source_websites = Column(JSON, nullable=False, default=[])  # List of website IDs
    source_documents = Column(JSON, nullable=False, default=[])  # List of document IDs
    source_entities = Column(JSON, nullable=False, default=[])   # List of entity IDs
    
    # Metadata
    tags = Column(JSON, nullable=False, default=[])
    confidence_score = Column(Float, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    # Relationships
    blocks = relationship("WikiBlock", back_populates="card", cascade="all, delete-orphan")
    validation_cards = relationship("ValidationCard", back_populates="card")
    discussion_threads = relationship("DiscussionThread", back_populates="card")


class WikiBlock(Base):
    """Wiki Block model - individual content blocks within knowledge cards"""
    __tablename__ = "wiki_blocks"
    
    id = Column(String(50), primary_key=True, index=True)
    card_id = Column(String(50), ForeignKey("knowledge_cards.id", ondelete="CASCADE"), nullable=False)
    
    section_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    word_limit = Column(Integer, nullable=False)
    block_type = Column(Enum(BlockType), default=BlockType.TEXT, nullable=False)
    
    # Template and generation info
    template_query = Column(String(100), nullable=True)
    generated_from = Column(String(50), nullable=True)  # Source document/block ID
    
    # Verification and curation
    verification_state = Column(Enum(VerificationState), default=VerificationState.PENDING, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(50), nullable=True)
    verification_notes = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Provenance tracking
    source_website_id = Column(String(50), nullable=True)
    source_file_id = Column(String(50), nullable=True)
    source_document_id = Column(String(50), nullable=True)
    extraction_date = Column(DateTime, nullable=True)
    extraction_tool = Column(String(50), nullable=True)
    
    # Maintenance
    maintenance_tags = Column(JSON, nullable=False, default=[])
    is_live = Column(Boolean, default=False, nullable=False)
    
    # Creation and modification tracking
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    updated_by = Column(String(50), nullable=True)
    
    # Relationships
    card = relationship("KnowledgeCard", back_populates="blocks")
    provenance_records = relationship("BlockProvenance", back_populates="block")


class BlockProvenance(Base):
    """Provenance tracking for wiki blocks"""
    __tablename__ = "block_provenance"
    
    id = Column(String(50), primary_key=True, index=True)
    block_id = Column(String(50), ForeignKey("wiki_blocks.id", ondelete="CASCADE"), nullable=False)
    
    # Source information
    source_website_id = Column(String(50), nullable=True)
    source_website_url = Column(String(255), nullable=True)
    source_file_id = Column(String(50), nullable=True)
    source_file_url = Column(String(255), nullable=True)
    source_document_id = Column(String(50), nullable=True)
    
    # Extraction details
    extraction_date = Column(DateTime, nullable=True)
    extraction_tool = Column(String(50), nullable=True)
    extraction_version = Column(String(20), nullable=True)
    
    # Curation details
    curator_id = Column(String(50), nullable=True)
    curation_date = Column(DateTime, nullable=True)
    curation_notes = Column(Text, nullable=True)
    
    # Validation details
    validation_state = Column(Enum(VerificationState), nullable=True)
    validation_date = Column(DateTime, nullable=True)
    validator_id = Column(String(50), nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # Relationships
    block = relationship("WikiBlock", back_populates="provenance_records")


class ValidationCard(Base):
    """Validation Card model - tracks content conflicts and resolutions"""
    __tablename__ = "validation_cards"
    
    id = Column(String(50), primary_key=True, index=True)
    
    # Target of validation
    target_type = Column(String(50), nullable=False)  # 'block', 'entity', 'card', 'triplet'
    target_id = Column(String(50), nullable=False)
    card_id = Column(String(50), ForeignKey("knowledge_cards.id", ondelete="CASCADE"), nullable=True)
    
    # Content details
    current_value = Column(Text, nullable=True)
    proposed_value = Column(Text, nullable=True)
    diff = Column(Text, nullable=True)
    
    # Validation metadata
    status = Column(String(50), default="open", nullable=False)  # open, under_review, approved, rejected, merged, escalated, no_consensus
    sensitivity = Column(String(20), default="medium", nullable=False)  # low, medium, high
    assigned_tier = Column(String(20), nullable=True)  # tier_1, tier_2, tier_3
    confidence_score = Column(Float, nullable=True)
    
    # Evidence and provenance
    evidence = Column(JSON, nullable=False, default=[])
    provenance = Column(JSON, nullable=False, default={})
    source_reliability = Column(String(20), nullable=True)
    contradiction_type = Column(String(50), nullable=True)
    
    # Assignment and resolution
    assigned_to = Column(String(50), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    assigned_by = Column(String(50), nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(50), nullable=True)
    resolution = Column(Text, nullable=True)
    resolution_type = Column(String(20), nullable=True)  # approved, rejected, merged, escalated
    
    # Creation tracking
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    
    # Relationships
    card = relationship("KnowledgeCard", back_populates="validation_cards")


class DiscussionThread(Base):
    """Discussion Thread model - collaborative discussion around knowledge content"""
    __tablename__ = "discussion_threads"
    
    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(100), nullable=True)
    
    # Status and resolution
    status = Column(String(50), default="open", nullable=False)  # open, under_review, consensus_reached, no_consensus, rejected, escalated, resolved, archived
    consensus_result = Column(String(20), nullable=True)  # accept, reject, modify
    resolution_summary = Column(Text, nullable=True)
    
    # Linked entities
    linked_card_id = Column(String(50), ForeignKey("knowledge_cards.id", ondelete="CASCADE"), nullable=True)
    linked_block_id = Column(String(50), nullable=True)
    linked_entity_id = Column(String(50), nullable=True)
    
    # Quality and compliance
    evidence_quality = Column(String(20), nullable=True)  # low, medium, high
    policy_compliance = Column(Boolean, nullable=True)
    
    # Creation and resolution tracking
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    updated_by = Column(String(50), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(50), nullable=True)
    
    # Watchers
    watchers = Column(JSON, nullable=False, default=[])
    
    # Relationships
    card = relationship("KnowledgeCard", back_populates="discussion_threads")
    comments = relationship("DiscussionComment", back_populates="thread", cascade="all, delete-orphan")


class DiscussionComment(Base):
    """Discussion Comment model - individual comments in discussion threads"""
    __tablename__ = "discussion_comments"
    
    id = Column(String(50), primary_key=True, index=True)
    thread_id = Column(String(50), ForeignKey("discussion_threads.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    
    # Quality and compliance
    evidence_quality = Column(String(20), nullable=True)  # low, medium, high
    policy_compliance = Column(Boolean, nullable=True)
    
    # Mentions and attachments
    mentions = Column(JSON, nullable=False, default=[])
    attachments = Column(JSON, nullable=False, default=[])
    
    # Creation and modification tracking
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    updated_by = Column(String(50), nullable=True)
    
    # Relationships
    thread = relationship("DiscussionThread", back_populates="comments")


class SearchIndex(Base):
    """Search Index model - for advanced search capabilities"""
    __tablename__ = "search_index"
    
    id = Column(String(50), primary_key=True, index=True)
    
    # Indexed entity
    entity_type = Column(String(50), nullable=False)  # card, block, entity, document, website
    entity_id = Column(String(50), nullable=False)
    
    # Search content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    content_text = Column(Text, nullable=True)  # Plain text version
    snippet = Column(Text, nullable=True)
    
    # Metadata for search
    keywords = Column(JSON, nullable=False, default=[])
    domains = Column(JSON, nullable=False, default=[])
    card_types = Column(JSON, nullable=False, default=[])
    verification_states = Column(JSON, nullable=False, default=[])
    
    # Search vectors (would be populated by separate vector store)
    search_vector = Column(JSON, nullable=True)
    
    # Last updated
    last_indexed = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)