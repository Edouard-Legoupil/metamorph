"""Unit tests for Knowledge Graph Service"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.services.knowledge_graph import KnowledgeGraphService, Entity, Relationship


def test_knowledge_graph_initialization():
    """Test KnowledgeGraphService initialization"""
    service = KnowledgeGraphService()
    assert service.cache_size == 1000
    assert service.max_entity_name_length == 255
    assert service.max_relationship_types == 50


def test_entity_creation():
    """Test entity creation"""
    service = KnowledgeGraphService()
    
    # Test valid entity creation
    entity = service.create_entity("USAID", "ORGANIZATION", {"description": "US Agency for International Development"})
    assert entity is not None
    assert entity.entity_id is not None
    assert entity.name == "USAID"
    assert entity.type == "ORGANIZATION"
    assert entity.properties["description"] == "US Agency for International Development"


def test_entity_validation():
    """Test entity validation"""
    service = KnowledgeGraphService()
    
    # Test valid entity
    valid_entity = Entity("test1", "ORGANIZATION", {"name": "Test Org"})
    assert service._validate_entity(valid_entity) is True
    
    # Test invalid entity (missing required properties)
    invalid_entity = Entity("test2", "ORGANIZATION", {})
    assert service._validate_entity(invalid_entity) is False
    
    # Test entity with name too long
    long_name = "A" * 300
    invalid_entity = Entity("test3", "ORGANIZATION", {"name": long_name})
    assert service._validate_entity(invalid_entity) is False


def test_relationship_creation():
    """Test relationship creation"""
    service = KnowledgeGraphService()
    
    # Create entities first
    entity1 = service.create_entity("USAID", "ORGANIZATION", {"name": "USAID"})
    entity2 = service.create_entity("HIP 2024", "PROJECT", {"name": "HIP 2024"})
    
    # Test valid relationship creation
    relationship = service.create_relationship(
        entity1.entity_id, 
        entity2.entity_id, 
        "FUNDS", 
        {"amount": 1000000, "currency": "USD"}
    )
    
    assert relationship is not None
    assert relationship.relationship_id is not None
    assert relationship.source_id == entity1.entity_id
    assert relationship.target_id == entity2.entity_id
    assert relationship.type == "FUNDS"


def test_relationship_validation():
    """Test relationship validation"""
    service = KnowledgeGraphService()
    
    # Test valid relationship
    valid_rel = Relationship("rel1", "entity1", "entity2", "FUNDS", {"amount": 1000000})
    assert service._validate_relationship(valid_rel) is True
    
    # Test invalid relationship (same source and target)
    invalid_rel = Relationship("rel2", "entity1", "entity1", "FUNDS", {})
    assert service._validate_relationship(invalid_rel) is False
    
    # Test invalid relationship type
    invalid_rel = Relationship("rel3", "entity1", "entity2", "INVALID_TYPE", {})
    assert service._validate_relationship(invalid_rel) is False


def test_entity_caching():
    """Test entity caching functionality"""
    service = KnowledgeGraphService()
    
    # Create an entity
    entity1 = service.create_entity("TestEntity", "ORGANIZATION", {"name": "Test Entity"})
    
    # Retrieve from cache
    cached_entity = service._get_cached_entity(entity1.entity_id)
    assert cached_entity is not None
    assert cached_entity.entity_id == entity1.entity_id
    
    # Test cache eviction (exceed max size)
    service.cache_size = 2
    entity2 = service.create_entity("TestEntity2", "ORGANIZATION", {"name": "Test Entity 2"})
    entity3 = service.create_entity("TestEntity3", "ORGANIZATION", {"name": "Test Entity 3"})
    
    # First entity should be evicted
    assert service._get_cached_entity(entity1.entity_id) is None


def test_entity_search():
    """Test entity search functionality"""
    service = KnowledgeGraphService()
    
    # Create test entities
    entity1 = service.create_entity("USAID", "ORGANIZATION", {"name": "USAID", "country": "USA"})
    entity2 = service.create_entity("UNHCR", "ORGANIZATION", {"name": "UNHCR", "country": "Global"})
    entity3 = service.create_entity("HIP 2024", "PROJECT", {"name": "HIP 2024", "funder": "USAID"})
    
    # Test search by name
    results = service.search_entities("USAID")
    assert len(results) >= 1
    assert any(e.name == "USAID" for e in results)
    
    # Test search by type
    org_results = service.search_entities("", entity_type="ORGANIZATION")
    assert len(org_results) >= 2
    assert all(e.type == "ORGANIZATION" for e in org_results)


def test_relationship_search():
    """Test relationship search functionality"""
    service = KnowledgeGraphService()
    
    # Create entities and relationships
    entity1 = service.create_entity("USAID", "ORGANIZATION", {"name": "USAID"})
    entity2 = service.create_entity("HIP 2024", "PROJECT", {"name": "HIP 2024"})
    entity3 = service.create_entity("UNHCR", "ORGANIZATION", {"name": "UNHCR"})
    
    rel1 = service.create_relationship(entity1.entity_id, entity2.entity_id, "FUNDS", {"amount": 1000000})
    rel2 = service.create_relationship(entity1.entity_id, entity3.entity_id, "PARTNERS_WITH", {})
    
    # Test search by type
    funding_rels = service.search_relationships("FUNDS")
    assert len(funding_rels) >= 1
    assert any(r.type == "FUNDS" for r in funding_rels)
    
    # Test search by source entity
    usaid_rels = service.search_relationships("", source_id=entity1.entity_id)
    assert len(usaid_rels) >= 2
    assert all(r.source_id == entity1.entity_id for r in usaid_rels)


def test_graph_statistics():
    """Test graph statistics calculation"""
    service = KnowledgeGraphService()
    
    # Create test data
    entity1 = service.create_entity("USAID", "ORGANIZATION", {})
    entity2 = service.create_entity("HIP 2024", "PROJECT", {})
    entity3 = service.create_entity("UNHCR", "ORGANIZATION", {})
    
    rel1 = service.create_relationship(entity1.entity_id, entity2.entity_id, "FUNDS", {})
    rel2 = service.create_relationship(entity1.entity_id, entity3.entity_id, "PARTNERS_WITH", {})
    
    # Get statistics
    stats = service.get_graph_statistics()
    
    assert stats.total_entities >= 3
    assert stats.total_relationships >= 2
    assert stats.entity_types >= 2
    assert stats.relationship_types >= 2


def test_entity_update():
    """Test entity update functionality"""
    service = KnowledgeGraphService()
    
    # Create an entity
    entity = service.create_entity("TestEntity", "ORGANIZATION", {"name": "Original Name"})
    
    # Update the entity
    updated_entity = service.update_entity(
        entity.entity_id,
        name="Updated Name",
        entity_type="ORGANIZATION",
        properties={"name": "Updated Name", "description": "Updated description"}
    )
    
    assert updated_entity is not None
    assert updated_entity.name == "Updated Name"
    assert updated_entity.properties["description"] == "Updated description"


def test_relationship_update():
    """Test relationship update functionality"""
    service = KnowledgeGraphService()
    
    # Create entities and relationship
    entity1 = service.create_entity("USAID", "ORGANIZATION", {})
    entity2 = service.create_entity("HIP 2024", "PROJECT", {})
    
    relationship = service.create_relationship(
        entity1.entity_id, 
        entity2.entity_id, 
        "FUNDS", 
        {"amount": 1000000}
    )
    
    # Update the relationship
    updated_rel = service.update_relationship(
        relationship.relationship_id,
        source_id=entity1.entity_id,
        target_id=entity2.entity_id,
        relationship_type="FUNDS",
        properties={"amount": 1500000, "currency": "USD"}
    )
    
    assert updated_rel is not None
    assert updated_rel.properties["amount"] == 1500000
    assert updated_rel.properties["currency"] == "USD"


def test_entity_deletion():
    """Test entity deletion functionality"""
    service = KnowledgeGraphService()
    
    # Create an entity
    entity = service.create_entity("TestEntity", "ORGANIZATION", {})
    entity_id = entity.entity_id
    
    # Verify entity exists
    assert service.get_entity(entity_id) is not None
    
    # Delete the entity
    success = service.delete_entity(entity_id)
    assert success is True
    
    # Verify entity is deleted
    assert service.get_entity(entity_id) is None


def test_relationship_deletion():
    """Test relationship deletion functionality"""
    service = KnowledgeGraphService()
    
    # Create entities and relationship
    entity1 = service.create_entity("USAID", "ORGANIZATION", {})
    entity2 = service.create_entity("HIP 2024", "PROJECT", {})
    
    relationship = service.create_relationship(
        entity1.entity_id, 
        entity2.entity_id, 
        "FUNDS", 
        {}
    )
    rel_id = relationship.relationship_id
    
    # Verify relationship exists
    assert service.get_relationship(rel_id) is not None
    
    # Delete the relationship
    success = service.delete_relationship(rel_id)
    assert success is True
    
    # Verify relationship is deleted
    assert service.get_relationship(rel_id) is None


def test_graph_export_import():
    """Test graph export and import functionality"""
    service = KnowledgeGraphService()
    
    # Create test data
    entity1 = service.create_entity("USAID", "ORGANIZATION", {"name": "USAID"})
    entity2 = service.create_entity("HIP 2024", "PROJECT", {"name": "HIP 2024"})
    
    rel = service.create_relationship(
        entity1.entity_id, 
        entity2.entity_id, 
        "FUNDS", 
        {"amount": 1000000}
    )
    
    # Export graph
    export_data = service.export_graph()
    
    assert export_data is not None
    assert "entities" in export_data
    assert "relationships" in export_data
    assert len(export_data["entities"]) >= 2
    assert len(export_data["relationships"]) >= 1


def test_related_entities():
    """Test finding related entities"""
    service = KnowledgeGraphService()
    
    # Create entities and relationships
    usaid = service.create_entity("USAID", "ORGANIZATION", {})
    hip = service.create_entity("HIP 2024", "PROJECT", {})
    unhcr = service.create_entity("UNHCR", "ORGANIZATION", {})
    
    service.create_relationship(usaid.entity_id, hip.entity_id, "FUNDS", {})
    service.create_relationship(usaid.entity_id, unhcr.entity_id, "PARTNERS_WITH", {})
    
    # Find entities related to USAID
    related = service.get_related_entities(usaid.entity_id)
    
    assert len(related) >= 2
    related_ids = [e.entity_id for e in related]
    assert hip.entity_id in related_ids
    assert unhcr.entity_id in related_ids


def test_graph_analysis():
    """Test graph analysis functions"""
    service = KnowledgeGraphService()
    
    # Create a more complex graph
    usaid = service.create_entity("USAID", "ORGANIZATION", {})
    hip = service.create_entity("HIP 2024", "PROJECT", {})
    unhcr = service.create_entity("UNHCR", "ORGANIZATION", {})
    refugee_camp = service.create_entity("Bidi Bidi", "LOCATION", {"type": "refugee_camp"})
    
    service.create_relationship(usaid.entity_id, hip.entity_id, "FUNDS", {"amount": 1000000})
    service.create_relationship(hip.entity_id, refugee_camp.entity_id, "SUPPORTS", {})
    service.create_relationship(usaid.entity_id, unhcr.entity_id, "PARTNERS_WITH", {})
    
    # Test shortest path
    path = service.find_shortest_path(usaid.entity_id, refugee_camp.entity_id)
    assert path is not None
    assert len(path) >= 2  # Should be USAID -> HIP -> Refugee Camp
    
    # Test community detection
    communities = service.detect_communities()
    assert communities is not None
    assert len(communities) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
