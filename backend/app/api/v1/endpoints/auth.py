from fastapi import APIRouter, Body, Depends
from app.core.security import get_api_key

router = APIRouter()


@router.post("/login")
def login(api_key: str = Body(...), depends_ok: str = Depends(get_api_key)):
    """Login endpoint - returns 'ok' if API key is valid"""
    return {"status": "ok"}
