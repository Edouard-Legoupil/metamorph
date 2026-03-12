from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.endpoints import triplets
from app.api.v1.endpoints.ingestion import router as ingestion_router
from app.api.v1.endpoints.triplet_extraction import router as triplet_extraction_router
from app.api.v1.endpoints.curation import router as curation_router
from app.api.v1.endpoints.templates import router as templates_router
from app.api.v1.endpoints.block_preview import router as block_preview_router
from app.api.v1.endpoints.trust_routing import router as trust_routing_router
from app.api.v1.endpoints.delta_alerts import router as delta_alerts_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.blocks_card import router as blocks_card_router

app = FastAPI()
app.include_router(triplets.router, prefix="/api/v1/triplets")
app.include_router(ingestion_router, prefix="/api/v1/ingestion")
app.include_router(triplet_extraction_router, prefix="/api/v1/extraction")
app.include_router(curation_router, prefix="/api/v1/curation")
app.include_router(templates_router, prefix="/api/v1/templates")
app.include_router(block_preview_router, prefix="/api/v1/blocks")
app.include_router(trust_routing_router, prefix="/api/v1/trust")
app.include_router(delta_alerts_router, prefix="/api/v1/alerts")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(blocks_card_router, prefix="/api/v1/blocks")

# Must be LAST: Serve React build at /
FRONTEND_BUILD_DIR = os.getenv(
    "FRONTEND_BUILD_DIR",
    os.path.join(os.path.dirname(__file__), "../../../frontend/dist"),
)
if os.path.exists(FRONTEND_BUILD_DIR):
    app.mount(
        "/", StaticFiles(directory=FRONTEND_BUILD_DIR, html=True), name="frontend"
    )


@app.get("/")
def health_check():
    return {"status": "ok"}
