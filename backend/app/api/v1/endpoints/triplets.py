from fastapi import APIRouter
from app.services.extraction.triplet_schema import Triplet, validate_triplet

router = APIRouter()


from fastapi import Depends
from app.core.security import get_api_key


@router.post("/validate-triplet")
async def validate_triplet_endpoint(
    triplet: Triplet, api_key: str = Depends(get_api_key)
):
    errors = validate_triplet(triplet)
    return {"valid": not errors, "errors": errors, "triplet": triplet.dict()}
