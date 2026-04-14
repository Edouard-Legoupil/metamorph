"""Edge case tests for error handling and boundary conditions."""
import pytest
from app.services.extraction.triplet_schema import validate_triplet, Triplet, score_confidence
from app.services.ingestion.ingestion_pipeline import analyze_layout, route_parser


def test_triplet_validation_edge_cases():
    """Test triplet validation with edge cases."""
    # Test with minimal valid triplet
    minimal_triplet = {
        "subject": {"label": "Donor", "name": "Test", "properties": {"name": "Test"}},
        "predicate": "TEST_PREDICATE",
        "object": {"label": "Test", "name": "Test", "properties": {}},
        "metadata": {
            "source_document_id": "test-001",
            "source_document_title": "Test",
            "extracted_at": "2024-01-01T00:00:00",
            "extraction_confidence": 0.5,
            "raw_text_snippet": "Test",
            "extraction_method": "LLM"
        }
    }
    
    validated = Triplet(**minimal_triplet)
    errors = validate_triplet(validated)
    assert len(errors) == 0
    
    # Test with complete metadata (all required fields)
    complete_triplet = minimal_triplet.copy()
    # This should pass validation since all required fields are present
    validated3 = Triplet(**complete_triplet)
    errors3 = validate_triplet(validated3)
    assert len(errors3) == 0


def test_confidence_scoring_edge_cases():
    """Test confidence scoring with edge cases."""
    # Test minimum confidence
    min_conf = score_confidence("LLM", self_reported_score=0.0)
    assert min_conf >= 0
    
    # Test maximum confidence
    max_conf = score_confidence("LLM", self_reported_score=1.0)
    assert max_conf <= 1
    
    # Test hybrid with missing scores
    hybrid_conf = score_confidence("HYBRID")  # No scores provided
    assert 0 <= hybrid_conf <= 1


def test_layout_analysis_edge_cases():
    """Test layout analysis with edge cases."""
    # Test with minimal layout
    minimal_layout = {
        "table_density": 0.0,
        "column_count": 1,
        "complex_layout_score": 0.0,
        "embedded_charts": 0,
        "pages_sampled": 1
    }
    
    result = analyze_layout("test-file.pdf")
    # Should return default analysis
    assert "table_density" in result
    assert "column_count" in result
    
    # Test routing with minimal layout (should use docling)
    parser = route_parser(minimal_layout)
    assert parser == "docling"
    
    # Test with complex layout (should use mineru)
    complex_layout = {
        "table_density": 0.5,
        "column_count": 3,
        "complex_layout_score": 0.8
    }
    
    parser2 = route_parser(complex_layout)
    assert parser2 == "mineru"


def test_empty_and_null_inputs():
    """Test handling of empty and null inputs."""
    # Test empty string inputs
    from app.services.extraction.triplet_extractor import extract_triplets_from_markdown
    
    result = extract_triplets_from_markdown("", "Empty", "test-001")
    assert result["triplet_count"] == 0
    assert result["status"] == "ok"
    
    # Test with whitespace only
    result2 = extract_triplets_from_markdown("   \n\n  ", "Whitespace", "test-002")
    assert result2["triplet_count"] == 0


def test_unicode_and_special_characters():
    """Test handling of unicode and special characters."""
    markdown_with_unicode = """
# Document with Unicode

- Organization: UNHCR (អង្គការសហបានន័យកម្ពុជា)
- Amount: $1,000,000 (៛4,000,000,000)
"""
    
    from app.services.extraction.triplet_extractor import extract_triplets_from_markdown
    result = extract_triplets_from_markdown(markdown_with_unicode, "Unicode Test", "test-003")
    # Should handle unicode without crashing
    assert "triplets" in result


def test_large_input_handling():
    """Test handling of large inputs."""
    # Create large markdown document
    large_markdown = "# Header\n" + "\n".join([f"Item {i}" for i in range(1000)])
    
    from app.services.extraction.triplet_extractor import extract_triplets_from_markdown
    result = extract_triplets_from_markdown(large_markdown, "Large Test", "test-004")
    # Should process without crashing
    assert "triplets" in result
    assert result["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])