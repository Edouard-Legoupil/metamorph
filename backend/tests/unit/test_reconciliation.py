"""Unit tests for reconciliation services - delta engine, conflict detection, etc."""
import pytest
from app.services.reconciliation.delta_engine import delta_engine, classify_conflict


def test_delta_engine_expansion():
    """Test delta engine with new triplet (expansion case)."""
    new_triplet = {
        "subject": {"name": "USAID", "label": "Donor"},
        "predicate": "FUNDS",
        "object": {"name": "HIP 2024", "label": "FundingInstrument"},
        "metadata": {"source_document_id": "doc-123"}
    }
    
    result = delta_engine(new_triplet, [])
    assert result["outcome"] == "EXPANSION"
    assert result["action"] == "route_by_confidence"


def test_delta_engine_confirmation():
    """Test delta engine with duplicate triplet (confirmation case)."""
    existing = {
        "subject": {"name": "USAID", "label": "Donor"},
        "predicate": "FUNDS",
        "object": {"name": "HIP 2024", "label": "FundingInstrument"}
    }
    
    new_triplet = {
        "subject": {"name": "USAID", "label": "Donor"},
        "predicate": "FUNDS",
        "object": {"name": "HIP 2024", "label": "FundingInstrument"},
        "metadata": {"source_document_id": "doc-456"}
    }
    
    result = delta_engine(new_triplet, [existing])
    assert result["outcome"] == "CONFIRMATION"
    assert result["action"] == "increment_source_count"


def test_conflict_classification():
    """Test conflict classification for different types."""
    existing = {
        "subject": {"name": "Refugees", "label": "PopulationGroup"},
        "predicate": "POPULATION_FIGURE",
        "object": {"name": "100000", "label": "Figure", "populationFigure": 100000}
    }
    
    incoming = {
        "subject": {"name": "Refugees", "label": "PopulationGroup"},
        "predicate": "POPULATION_FIGURE",
        "object": {"name": "150000", "label": "Figure", "populationFigure": 150000}
    }
    
    conflict_type, severity = classify_conflict(existing, incoming, "POPULATION_FIGURE")
    assert conflict_type == "QUANTITATIVE"
    assert severity in ["CRITICAL", "MINOR"]


def test_delta_engine_contradiction():
    """Test delta engine with contradictory data."""
    existing = {
        "subject": {"name": "Refugees", "label": "PopulationGroup"},
        "predicate": "POPULATION_FIGURE",
        "object": {"name": "100000", "label": "Figure", "populationFigure": 100000}
    }
    
    new_triplet = {
        "subject": {"name": "Refugees", "label": "PopulationGroup"},
        "predicate": "POPULATION_FIGURE",
        "object": {"name": "150000", "label": "Figure", "populationFigure": 150000},
        "metadata": {"source_document_id": "doc-789"}
    }
    
    result = delta_engine(new_triplet, [existing])
    assert result["outcome"] == "CONTRADICTION"
    assert "conflict_record" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])