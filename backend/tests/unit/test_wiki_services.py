"""Unit tests for wiki services - card templates, block assembly, etc."""
import pytest
from app.services.wiki.card_templates import (
    KC1DonorCard, KC2FieldContextCard, validate_card
)
from app.services.wiki.block_assembler import assemble_blocks_for_card


def test_donor_card_validation():
    """Test donor card template validation."""
    card = KC1DonorCard()
    assert card.card_id == "KC-1"
    assert len(card.sections) > 0
    assert "Donor Overview" in [s["name"] for s in card.sections]


def test_field_card_validation():
    """Test field context card template validation."""
    card = KC2FieldContextCard()
    assert card.card_id == "KC-2"
    assert "Protection Landscape" in [s["name"] for s in card.sections]
    assert len(card.freshness_rules) > 0


def test_card_validation_logic():
    """Test card validation with blocks."""
    card = KC1DonorCard()
    
    # Test valid blocks
    valid_blocks = [
        {"section_name": "Donor Overview", "word_count": 50, "sources": ["doc-1"], "word_limit": 80},
        {"section_name": "Funding History", "word_count": 60, "sources": ["doc-2"], "word_limit": 75}
    ]
    errors = validate_card(card, valid_blocks)
    assert len(errors) == 0
    
    # Test invalid blocks
    invalid_blocks = [
        {"section_name": "NonExistent Section", "word_count": 50, "sources": ["doc-1"], "word_limit": 80},
        {"section_name": "Donor Overview", "word_count": 200, "sources": [], "word_limit": 80}  # Over word limit, no sources
    ]
    errors = validate_card(card, invalid_blocks, require_sources=True)
    assert len(errors) > 0
    assert any("not in card" in e for e in errors)
    assert any("exceeds word limit" in e for e in errors)
    assert any("missing sources" in e for e in errors)


def test_block_assembly():
    """Test wiki block assembly from triplets."""
    # Test with card ID and page ID
    blocks = assemble_blocks_for_card("KC-1", "page-001")
    assert len(blocks) > 0
    assert any("Donor Overview" in b["section_name"] for b in blocks)
    assert all("block_id" in b for b in blocks)


def test_card_edge_cases():
    """Test card templates with edge cases."""
    card = KC1DonorCard()
    
    # Test empty blocks
    errors = validate_card(card, [])
    assert len(errors) == 0  # Empty is valid
    
    # Test blocks with missing required fields (but with required validation off)
    incomplete_blocks = [
        {"section_name": "Donor Overview", "word_count": 50}  # Missing sources but we don't require them
    ]
    errors = validate_card(card, incomplete_blocks, require_sources=False)
    # Should pass if not requiring sources
    assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])