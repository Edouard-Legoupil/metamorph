"""Integration tests for service interactions."""
import pytest
from tempfile import NamedTemporaryFile
from app.services.ingestion.ingestion_pipeline import process_document
from app.services.extraction.triplet_extractor import extract_triplets_from_markdown
from app.services.reconciliation.delta_engine import delta_engine


def test_full_pipeline_integration():
    """Test complete document processing pipeline."""
    with NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tf.write(b"""
# Test Document

USAID funds HIP 2024 with $1,000,000 for refugee support.

## Key Figures

- Refugees: 100,000
- Funding: $1,000,000

| Organization | Amount |
|-------------|--------|
| USAID | $1,000,000 |
| UNHCR | $500,000 |
""".strip())
        
        # Process document through full pipeline
        result = process_document(tf.name)
        
        # Verify pipeline stages
        assert "doc_id" in result
        assert "markdown_path" in result
        assert "status" in result
        assert result["status"] == "EXTRACTED"
        assert "all_triplets" in result
        # Check that we have some triplets or the pipeline completed
        assert isinstance(result["all_triplets"], list)


def test_extraction_to_reconciliation():
    """Test extraction output feeding into reconciliation."""
    markdown = """
# Population Update

Refugee population increased from 100,000 to 150,000 in 2024.
"""
    
    # Extract triplets
    extraction_result = extract_triplets_from_markdown(
        markdown, "Update", "pop-doc-001"
    )
    
    # Get first triplet for testing
    if extraction_result["triplets"]:
        triplet = extraction_result["triplets"][0]
        
        # Test reconciliation with empty existing data (should be expansion)
        delta_result = delta_engine(triplet, [])
        assert delta_result["outcome"] == "EXPANSION"
        
        # Test reconciliation with same data (should be confirmation)
        delta_result2 = delta_engine(triplet, [triplet])
        assert delta_result2["outcome"] == "CONFIRMATION"


def test_error_handling_integration():
    """Test error handling across service boundaries."""
    # Test with empty document
    with NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tf.write(b"")  # Empty document
        
        result = process_document(tf.name)
        assert result["status"] == "EXTRACTED"
        # Check all_triplets exists and is a list
        assert "all_triplets" in result
        assert isinstance(result["all_triplets"], list)
    
    # Test with malformed document
    with NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tf.write(b"Random text without structure or meaningful content")
        
        result = process_document(tf.name)
        assert result["status"] == "EXTRACTED"
        # Should still process even if no meaningful triplets found
        assert "all_triplets" in result
        assert isinstance(result["all_triplets"], list)


def test_service_chaining():
    """Test chaining multiple services together."""
    # Create test data
    test_triplets = [
        {
            "subject": {"name": "USAID", "label": "Donor"},
            "predicate": "FUNDS",
            "object": {"name": "Project X", "label": "Project", "amountUsd": 1000000},
            "metadata": {"source_document_id": "test-doc-001"}
        }
    ]
    
    # Process through delta engine
    results = []
    for triplet in test_triplets:
        result = delta_engine(triplet, [])
        results.append(result)
    
    # Verify all processed correctly
    assert all(r["outcome"] == "EXPANSION" for r in results)
    assert all(r["action"] == "route_by_confidence" for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])