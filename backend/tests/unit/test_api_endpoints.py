"""Unit tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triplet_validation_endpoint():
    """Test triplet validation endpoint."""
    triplet = {
        "subject": {"label": "Donor", "name": "USAID", "properties": {"name": "USAID"}},
        "predicate": "FUNDS",
        "object": {"label": "FundingInstrument", "name": "HIP 2024", "properties": {"amountUsd": 1000000}},
        "metadata": {
            "source_document_id": "doc-123",
            "source_document_title": "Test",
            "extracted_at": "2024-01-01T00:00:00",
            "extraction_confidence": 0.9,
            "raw_text_snippet": "USAID funds HIP 2024",
            "extraction_method": "LLM"
        }
    }
    
    # Note: This endpoint requires API key in real usage
    # For testing, we'll test the validation logic directly
    from app.services.extraction.triplet_schema import validate_triplet, Triplet
    
    validated_triplet = Triplet(**triplet)
    errors = validate_triplet(validated_triplet)
    assert len(errors) == 0


def test_invalid_triplet():
    """Test validation of invalid triplet."""
    from app.services.extraction.triplet_schema import validate_triplet, Triplet
    
    # Missing required properties
    invalid_triplet = {
        "subject": {"label": "Settlement", "name": "Bidi Bidi", "properties": {"settlementType": "Camp"}},  # Missing 'name'
        "predicate": "DISPLACED_TO",
        "object": {"label": "PopulationGroup", "name": "Refugees", "properties": {"groupType": "Refugee"}},
        "metadata": {
            "source_document_id": "doc-123",
            "source_document_title": "Test",
            "extracted_at": "2024-01-01T00:00:00",
            "extraction_confidence": 0.9,
            "raw_text_snippet": "Refugees moved to Bidi Bidi",
            "extraction_method": "LLM"
        }
    }
    
    validated_triplet = Triplet(**invalid_triplet)
    errors = validate_triplet(validated_triplet)
    assert len(errors) > 0
    assert any("Missing required property 'name' for Settlement" in e for e in errors)


def test_endpoint_error_handling():
    """Test API error handling."""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    
    # Test invalid method
    response = client.post("/")
    assert response.status_code == 405  # Method not allowed


@pytest.mark.asyncio
async def test_async_endpoints():
    """Test async endpoints if any exist."""
    # This would test any async-specific endpoints
    # Current API is mostly sync, but structure is here for future async endpoints
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])