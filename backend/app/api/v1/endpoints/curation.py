from fastapi import APIRouter
from app.services.reconciliation.journal import load_journal

router = APIRouter()


from fastapi import Depends
from app.core.security import get_api_key


@router.get("/conflicts")
def get_pending_conflicts(api_key: str = Depends(get_api_key)):
    """
    Endpoint for curators/agents to review unresolved ConflictRecords.
    """
    conflicts = load_journal()
    return [c for c in conflicts if c["status"] == "UNRESOLVED"]
