from fastapi import APIRouter
from app.services.extraction.triplet_schema import Triplet, validate_triplet

router = APIRouter()


@router.post("/validate-triplet")
async def validate_triplet_endpoint(triplet: Triplet):
    errors = validate_triplet(triplet)
    return {"valid": not errors, "errors": errors, "triplet": triplet.dict()}
