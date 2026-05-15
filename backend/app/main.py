from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1.endpoints import triplets
from app.api.v1.endpoints.ingestion import router as ingestion_router
from app.api.v1.endpoints.triplet_extraction import router as triplet_extraction_router
from app.api.v1.endpoints.curation import router as curation_router
from app.api.v1.endpoints.templates import router as templates_router
from app.api.v1.endpoints.vector_store import router as vector_store_router
from app.api.v1.endpoints.block_preview import router as block_preview_router
from app.api.v1.endpoints.trust_routing import router as trust_routing_router
from app.api.v1.endpoints.delta_alerts import router as delta_alerts_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.blocks_card import router as blocks_card_router

# New endpoints for website crawling (FR-001, FR-002, FR-003)
from app.api.v1.endpoints.websites import router as websites_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.topics import router as topics_router
from app.api.v1.endpoints.team_members import router as team_members_router
from app.api.v1.endpoints.website_topics import router as website_topics_router
from app.api.v1.endpoints.crawler_settings import router as crawler_settings_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(triplets.router, prefix="/api/v1/triplets")
app.include_router(ingestion_router, prefix="/api/v1/ingestion")
app.include_router(triplet_extraction_router, prefix="/api/v1/extraction")
app.include_router(curation_router, prefix="/api/v1/curation")
app.include_router(templates_router, prefix="/api/v1/templates")
app.include_router(vector_store_router, prefix="/api/v1/vector")
app.include_router(block_preview_router, prefix="/api/v1/blocks")
app.include_router(trust_routing_router, prefix="/api/v1/trust")
app.include_router(delta_alerts_router, prefix="/api/v1/alerts")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(blocks_card_router, prefix="/api/v1/blocks")

# Website crawling and management endpoints
app.include_router(websites_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(topics_router, prefix="/api/v1")
app.include_router(team_members_router, prefix="/api/v1")
app.include_router(website_topics_router, prefix="/api/v1")
app.include_router(crawler_settings_router, prefix="/api/v1")

# Knowledge graph endpoints
from app.api.v1.endpoints.knowledge_graph import router as knowledge_graph_router
app.include_router(knowledge_graph_router, prefix="/api/v1")

# Knowledge card endpoints
from app.api.v1.endpoints.knowledge_cards import router as knowledge_cards_router
app.include_router(knowledge_cards_router, prefix="/api/v1")

# Agentic content generation endpoints
from app.api.v1.endpoints.agentic_content import router as agentic_content_router
app.include_router(agentic_content_router, prefix="/api/v1")

# Advanced search endpoints
from app.api.v1.endpoints.advanced_search import router as advanced_search_router
app.include_router(advanced_search_router, prefix="/api/v1")

# Analytics endpoints
from app.api.v1.endpoints.analytics import router as analytics_router
app.include_router(analytics_router, prefix="/api/v1")

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
