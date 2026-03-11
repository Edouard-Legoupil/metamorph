from typing import List, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class Entity(BaseModel):
    identifier: UUID
    createdAt: datetime
    lastUpdated: datetime
    verificationStatus: Literal[
        "AUTO_ACCEPTED", "SHADOW", "HUMAN_VERIFIED", "COMMUNITY_VERIFIED"
    ]
    hasTag: List[str] = Field(default_factory=list)
