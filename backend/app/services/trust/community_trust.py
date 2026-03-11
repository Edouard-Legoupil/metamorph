import time
from datetime import datetime, timedelta
from typing import Dict, List, Set
import uuid

CONFIG = {
    "COMMUNITY_TRUST_THRESHOLD": 3,
    "TRUST_DECAY_YEARS": 0.10,
    "NO_READS_MONTHS": 6,
}


# --- Models (stubs, typically would be DB records or graph node fields) ---
class BlockTrust:
    def __init__(self, block_id: str):
        self.block_id = block_id
        self.community_trust_score = 0
        self.verification_status = "AUTO_ACCEPTED"
        self.verified_at = None
        self._reads: Set[str] = set()  # user_id string
        self._verify: Set[str] = set()  # user_id
        self._flags: Set[str] = set()
        self.last_verification = None

    def increment_read(self, user_id: str):
        if user_id not in self._reads:
            self.community_trust_score += 1
            self._reads.add(user_id)

    def increment_verify(self, user_id: str):
        if user_id not in self._verify:
            self.community_trust_score += 3
            self._verify.add(user_id)
            self.update_status_if_needed()

    def increment_cite(self, user_id: str):
        self.community_trust_score += 5
        self.update_status_if_needed()

    def decrement_flag(self, user_id: str):
        self.community_trust_score -= 2
        self._flags.add(user_id)
        self.verification_status = "UNDER_REVIEW"
        if len(self._flags) >= 3:
            self.auto_escalate_tier2()

    def decrement_conflict(self, user_ids: List[str]):
        for user_id in user_ids:
            self.community_trust_score -= 1

    def decay_trust(self):
        decay_rate = CONFIG["TRUST_DECAY_YEARS"]
        self.community_trust_score = int(self.community_trust_score * (1 - decay_rate))

    def update_status_if_needed(self):
        threshold = CONFIG["COMMUNITY_TRUST_THRESHOLD"]
        if (
            self.verification_status == "AUTO_ACCEPTED"
            and self.community_trust_score >= threshold
        ):
            self.verification_status = "COMMUNITY_VERIFIED"
            self.verified_at = datetime.utcnow()

    def auto_escalate_tier2(self):
        self.verification_status = "ESCALATED_TIER2"

    def no_reads_check(self):
        # If no reads in 6 months, flag for review
        # (assuming _reads stores most recent 24h per user)
        now = datetime.utcnow()
        # Pseudo logic for last read timestamps per user
        # If required, would add actual timestamps here
        if len(self._reads) == 0:  # no reads ever
            self.verification_status = "FLAGGED_FOR_REVIEW"


# --- Read Tracking ---
class ReadTracker:
    # Map of (block_id, user_id): last_read timestamp
    reads: Dict[str, Dict[str, float]] = {}

    @classmethod
    def record_read(cls, block_id: str, user_id: str):
        day = datetime.utcnow().date()
        if block_id not in cls.reads:
            cls.reads[block_id] = {}
        # Deduplicate by date (24h window)
        if (
            user_id not in cls.reads[block_id]
            or datetime.utcfromtimestamp(cls.reads[block_id][user_id]).date() != day
        ):
            cls.reads[block_id][user_id] = time.time()
            return True
        return False


# --- Flag Workflow ---
def flag_block(block: BlockTrust, user_id: str):
    block.decrement_flag(user_id)
    # Curation queue integration, notification stub
    # Flag UI banner logic can be handled by block.verification_status
    return block


# --- Trust visualization helper ---
def get_verification_icon(block: BlockTrust):
    if block.verification_status == "AUTO_ACCEPTED":
        return "🤖"
    if block.verification_status in ("UNDER_REVIEW", "FLAGGED_FOR_REVIEW"):
        return "⚠️"
    if block.verification_status == "COMMUNITY_VERIFIED":
        return "👥"
    if block.verification_status == "ESCALATED_TIER2":
        return "🔴"
    if block.verification_status == "HUMAN_VERIFIED":
        return "✅"
    return "❓"
