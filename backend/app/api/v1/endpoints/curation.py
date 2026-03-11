from fastapi import APIRouter
from app.services.reconciliation.journal import load_journal

router = APIRouter()


@router.get("/conflicts")
def get_pending_conflicts():
    """
    Endpoint for curators/agents to review unresolved ConflictRecords.
    """
    conflicts = load_journal()
    return [c for c in conflicts if c["status"] == "UNRESOLVED"]
