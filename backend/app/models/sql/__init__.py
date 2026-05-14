"""
SQL Database Models for PostgreSQL.

Contains all relational data models for the Metamorph application.
"""

from .website import Website, DiscoveredFile, ScrapeSession, IngestionJob, WebsiteTopic
from .user import User, Team, TeamMember
from .settings import Topic, AppSettings, CrawlerSettings, NotificationSettings
from .knowledge_card import (
    KnowledgeCard, WikiBlock, ValidationCard, DiscussionThread, DiscussionComment,
    CardType, CardStatus, BlockType, VerificationState, BlockProvenance, SearchIndex
)

__all__ = [
    "Website",
    "DiscoveredFile",
    "ScrapeSession",
    "IngestionJob",
    "WebsiteTopic",
    "User",
    "Team",
    "TeamMember",
    "Topic",
    "AppSettings",
    "CrawlerSettings",
    "NotificationSettings",
    # Knowledge Card Models
    "KnowledgeCard",
    "WikiBlock",
    "ValidationCard",
    "DiscussionThread",
    "DiscussionComment",
    "CardType",
    "CardStatus",
    "BlockType",
    "VerificationState",
    "BlockProvenance",
    "SearchIndex",
]
