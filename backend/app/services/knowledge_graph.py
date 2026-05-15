"""
Knowledge Graph Core Service

Foundation for knowledge extraction, storage, and curation.
Implements entity management, relationship tracking, provenance, and validation.
"""

import os
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from neo4j import GraphDatabase, Transaction
from app.services.ingestion.graph_db import upsert_document_txn, upsert_triplets_neo4j
from app.services.extraction.triplet_extractor import extract_triplets_from_markdown


class EntityType(str, Enum):
    """Supported entity types in the knowledge graph"""
    PERSON = "Person"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    EVENT = "Event"
    DOCUMENT = "Document"
    CONCEPT = "Concept"
    DATE = "Date"
    VALUE = "Value"
    STATEMENT = "Statement"
    GENERIC = "Entity"


class RelationshipType(str, Enum):
    """Supported relationship types"""
    MENTIONS = "MENTIONS"
    RELATED_TO = "RELATED_TO"
    HAS_VALUE = "HAS_VALUE"
    ATTRIBUTED_STATEMENT = "ATTRIBUTED_STATEMENT"
    DATED = "DATED"
    LOCATED_AT = "LOCATED_AT"
    PART_OF = "PART_OF"
    CAUSED_BY = "CAUSED_BY"
    RESULTS_IN = "RESULTS_IN"
    GENERIC = "RELATED"


class KnowledgeStatus(str, Enum):
    """Status of knowledge entities"""
    PROPOSED = "proposed"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"
    DEPRECATED = "deprecated"


class ProvenanceLevel(str, Enum):
    """Levels of provenance confidence"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


# Neo4j Connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


class KnowledgeGraph:
    """Core knowledge graph service"""
    
    def __init__(self):
        self.entity_cache = {}
        self.relationship_cache = {}
    
    def _generate_entity_id(self, entity_type: EntityType, name: str) -> str:
        """Generate deterministic entity ID"""
        import hashlib
        base = f"{entity_type.value}_{name.lower()}"
        return hashlib.md5(base.encode('utf-8')).hexdigest()
    
    def create_entity(
        self, 
        name: str, 
        entity_type: EntityType, 
        properties: Dict[str, Any] = None,
        source_document_id: str = None,
        provenance: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new entity in the knowledge graph"""
        entity_id = self._generate_entity_id(entity_type, name)
        
        # Set default properties
        entity_properties = {
            "identifier": entity_id,
            "name": name,
            "type": entity_type.value,
            "status": KnowledgeStatus.PROPOSED.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": 1,
            ** (properties or {})
        }
        
        # Add provenance if provided
        if provenance:
            entity_properties["provenance"] = provenance
        
        # Cypher query to create entity
        cypher = (
            "CREATE (e:`Entity`:`{entity_type}` {props}) "
            "RETURN e"
        ).format(entity_type=entity_type.value)
        
        with driver.session() as session:
            result = session.run(cypher, props=entity_properties)
            record = result.single()
            
            # Convert Neo4j node to dict
            entity_node = record[0]
            entity_data = dict(entity_node)
            
            # Cache the entity
            self.entity_cache[entity_id] = entity_data
            
            return entity_data
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an entity from the knowledge graph"""
        # Check cache first
        if entity_id in self.entity_cache:
            return self.entity_cache[entity_id]
        
        # Query database
        cypher = (
            "MATCH (e:Entity {identifier: $id}) "
            "RETURN e"
        )
        
        with driver.session() as session:
            result = session.run(cypher, id=entity_id)
            record = result.single()
            
            if record:
                entity_node = record[0]
                entity_data = dict(entity_node)
                
                # Cache the entity
                self.entity_cache[entity_id] = entity_data
                return entity_data
        
        return None
    
    def update_entity(
        self, 
        entity_id: str, 
        updates: Dict[str, Any],
        new_status: KnowledgeStatus = None
    ) -> Dict[str, Any]:
        """Update an existing entity"""
        # Get current entity
        entity = self.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")
        
        # Apply updates
        entity.update(updates)
        if new_status:
            entity["status"] = new_status.value
        
        entity["updated_at"] = datetime.utcnow().isoformat()
        entity["version"] = entity.get("version", 1) + 1
        
        # Update in database
        cypher = (
            "MATCH (e:Entity {identifier: $id}) "
            "SET e += $props "
            "RETURN e"
        )
        
        with driver.session() as session:
            result = session.run(cypher, id=entity_id, props=entity)
            record = result.single()
            
            if record:
                updated_entity = dict(record[0])
                # Update cache
                self.entity_cache[entity_id] = updated_entity
                return updated_entity
        
        raise RuntimeError("Failed to update entity")
    
    def create_relationship(
        self,
        subject_id: str,
        predicate: RelationshipType,
        object_id: str,
        properties: Dict[str, Any] = None,
        source_document_id: str = None,
        provenance: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a relationship between entities"""
        relationship_id = f"{subject_id}_{predicate.value}_{object_id}"
        
        # Set default properties
        rel_properties = {
            "identifier": relationship_id,
            "type": predicate.value,
            "subject_id": subject_id,
            "object_id": object_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": 1,
            "status": KnowledgeStatus.PROPOSED.value,
            ** (properties or {})
        }
        
        # Add provenance if provided
        if provenance:
            rel_properties["provenance"] = provenance
        
        # Cypher query to create relationship
        cypher = (
            "MATCH (s:Entity {identifier: $subject_id}), (o:Entity {identifier: $object_id}) "
            "CREATE (s)-[r:RELATIONSHIP {props}]->(o) "
            "RETURN r"
        )
        
        with driver.session() as session:
            result = session.run(cypher, 
                               subject_id=subject_id, 
                               object_id=object_id, 
                               props=rel_properties)
            record = result.single()
            
            if record:
                rel_node = record[0]
                rel_data = dict(rel_node)
                
                # Cache the relationship
                self.relationship_cache[relationship_id] = rel_data
                return rel_data
        
        raise RuntimeError("Failed to create relationship")
    
    def get_relationship(self, relationship_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a relationship from the knowledge graph"""
        # Check cache first
        if relationship_id in self.relationship_cache:
            return self.relationship_cache[relationship_id]
        
        # Query database
        cypher = (
            "MATCH ()-[r:RELATIONSHIP {identifier: $id}]->() "
            "RETURN r"
        )
        
        with driver.session() as session:
            result = session.run(cypher, id=relationship_id)
            record = result.single()
            
            if record:
                rel_node = record[0]
                rel_data = dict(rel_node)
                
                # Cache the relationship
                self.relationship_cache[relationship_id] = rel_data
                return rel_data
        
        return None
    
    def update_relationship(
        self,
        relationship_id: str,
        updates: Dict[str, Any],
        new_status: KnowledgeStatus = None
    ) -> Dict[str, Any]:
        """Update an existing relationship"""
        # Get current relationship
        relationship = self.get_relationship(relationship_id)
        if not relationship:
            raise ValueError(f"Relationship {relationship_id} not found")
        
        # Apply updates
        relationship.update(updates)
        if new_status:
            relationship["status"] = new_status.value
        
        relationship["updated_at"] = datetime.utcnow().isoformat()
        relationship["version"] = relationship.get("version", 1) + 1
        
        # Update in database
        cypher = (
            "MATCH ()-[r:RELATIONSHIP {identifier: $id}]->() "
            "SET r += $props "
            "RETURN r"
        )
        
        with driver.session() as session:
            result = session.run(cypher, id=relationship_id, props=relationship)
            record = result.single()
            
            if record:
                updated_rel = dict(record[0])
                # Update cache
                self.relationship_cache[relationship_id] = updated_rel
                return updated_rel
        
        raise RuntimeError("Failed to update relationship")
    
    def extract_and_store_knowledge(
        self,
        document_id: str,
        markdown_content: str,
        document_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete knowledge extraction and storage pipeline"""
        # Step 1: Extract triplets from markdown
        extraction_result = extract_triplets_from_markdown(
            markdown_content,
            doc_type=document_metadata.get("file_type", "Document"),
            doc_id=document_id
        )
        
        triplets = extraction_result.get("triplets", [])
        
        # Step 2: Create document entity
        document_entity = self.create_entity(
            name=document_metadata.get("title", f"Document {document_id}"),
            entity_type=EntityType.DOCUMENT,
            properties={
                "source_url": document_metadata.get("source_url"),
                "file_path": document_metadata.get("file_path"),
                "document_id": document_id,
                "content_hash": document_metadata.get("content_hash")
            },
            provenance={
                "source": "ingestion_pipeline",
                "extracted_at": datetime.utcnow().isoformat(),
                "provenance_level": ProvenanceLevel.MEDIUM.value
            }
        )
        
        # Step 3: Create entities and relationships from triplets
        created_entities = []
        created_relationships = []
        
        for triplet in triplets:
            # Create subject entity
            subject_props = triplet["subject"].copy()
            subject_type = EntityType(subject_props.pop("label", EntityType.GENERIC.value))
            subject_entity = self.create_entity(
                name=subject_props["name"],
                entity_type=subject_type,
                properties=subject_props,
                provenance=triplet.get("provenance", {})
            )
            created_entities.append(subject_entity)
            
            # Create object entity
            object_props = triplet["object"].copy()
            object_type = EntityType(object_props.pop("label", EntityType.GENERIC.value))
            object_entity = self.create_entity(
                name=object_props["name"],
                entity_type=object_type,
                properties=object_props,
                provenance=triplet.get("provenance", {})
            )
            created_entities.append(object_entity)
            
            # Create relationship
            relationship = self.create_relationship(
                subject_id=subject_entity["identifier"],
                predicate=RelationshipType(triplet["predicate"]),
                object_id=object_entity["identifier"],
                properties={
                    "confidence": triplet.get("confidence", {}),
                    "qualifiers": triplet.get("qualifiers", {}),
                    "temporal": triplet.get("temporal", {})
                },
                provenance=triplet.get("provenance", {})
            )
            created_relationships.append(relationship)
        
        # Step 4: Store in Neo4j using existing functions
        upsert_document_txn(document_metadata, document_metadata.get("file_path", ""))
        upsert_triplets_neo4j(document_id, triplets)
        
        return {
            "success": True,
            "document_id": document_id,
            "triplets_extracted": len(triplets),
            "entities_created": len(created_entities),
            "relationships_created": len(created_relationships),
            "document_entity": document_entity,
            "entities": created_entities,
            "relationships": created_relationships
        }
    
    def search_entities(
        self,
        query: str,
        entity_type: EntityType = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for entities in the knowledge graph"""
        cypher_parts = ["MATCH (e:Entity)"]
        params = {}
        
        if query:
            cypher_parts.append("WHERE toLower(e.name) CONTAINS toLower($query)")
            params["query"] = query
        
        if entity_type:
            if "WHERE" in cypher_parts[1]:
                cypher_parts.append("AND")
            else:
                cypher_parts.append("WHERE")
            cypher_parts.append(f"e:{entity_type.value}")
        
        cypher_parts.append(f"RETURN e LIMIT {limit}")
        cypher = " ".join(cypher_parts)
        
        with driver.session() as session:
            result = session.run(cypher, **params)
            return [dict(record[0]) for record in result]
    
    def get_entity_relationships(
        self,
        entity_id: str,
        relationship_type: RelationshipType = None
    ) -> List[Dict[str, Any]]:
        """Get all relationships for an entity"""
        cypher_parts = [
            "MATCH (e:Entity {identifier: $id})-[r:RELATIONSHIP]->(o:Entity)"
        ]
        params = {"id": entity_id}
        
        if relationship_type:
            cypher_parts.append("WHERE r.type = $rel_type")
            params["rel_type"] = relationship_type.value
        
        cypher_parts.append("RETURN r, o")
        cypher = " ".join(cypher_parts)
        
        with driver.session() as session:
            result = session.run(cypher, **params)
            return [{
                "relationship": dict(record[0]),
                "target_entity": dict(record[1])
            } for record in result]
    
    def validate_knowledge(
        self,
        entity_id: str,
        validator_id: str,
        validation_result: bool,
        notes: str = None
    ) -> Dict[str, Any]:
        """Validate a knowledge entity or relationship"""
        # Update entity status
        new_status = KnowledgeStatus.VALIDATED if validation_result else KnowledgeStatus.REJECTED
        
        update_data = {
            "validated_by": validator_id,
            "validated_at": datetime.utcnow().isoformat(),
            "validation_notes": notes or ""
        }
        
        updated_entity = self.update_entity(entity_id, update_data, new_status)
        
        return {
            "success": True,
            "entity_id": entity_id,
            "new_status": new_status.value,
            "validated_by": validator_id,
            "validated_at": update_data["validated_at"],
            "entity": updated_entity
        }
    
    def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        stats = {}
        
        # Count entities by type
        with driver.session() as session:
            result = session.run(
                "MATCH (e:Entity) RETURN e.type as type, count(e) as count"
            )
            stats["entities_by_type"] = {record["type"]: record["count"] for record in result}
        
        # Count relationships by type
        with driver.session() as session:
            result = session.run(
                "MATCH ()-[r:RELATIONSHIP]->() RETURN r.type as type, count(r) as count"
            )
            stats["relationships_by_type"] = {record["type"]: record["count"] for record in result}
        
        # Count entities by status
        with driver.session() as session:
            result = session.run(
                "MATCH (e:Entity) RETURN e.status as status, count(e) as count"
            )
            stats["entities_by_status"] = {record["status"]: record["count"] for record in result}
        
        # Total counts
        stats["total_entities"] = sum(stats["entities_by_type"].values())
        stats["total_relationships"] = sum(stats["relationships_by_type"].values())
        
        return stats
    
    def find_related_entities(
        self,
        entity_id: str,
        max_depth: int = 2,
        relationship_types: List[RelationshipType] = None
    ) -> Dict[str, Any]:
        """Find entities related to a given entity"""
        # This would be implemented with a more complex Cypher query
        # For now, return a simple implementation
        
        cypher_parts = [
            "MATCH path = (start:Entity {identifier: $id})-[*..{depth}]-(end:Entity)"
        ]
        params = {"id": entity_id, "depth": max_depth}
        
        if relationship_types:
            rel_types = [rt.value for rt in relationship_types]
            cypher_parts.append("WHERE ALL(r IN relationships(path) WHERE r.type IN $rel_types)")
            params["rel_types"] = rel_types
        
        cypher_parts.append("RETURN path")
        cypher = " ".join(cypher_parts)
        
        with driver.session() as session:
            result = session.run(cypher, **params)
            
            paths = []
            for record in result:
                path = record["path"]
                path_data = {
                    "nodes": [dict(node) for node in path.nodes],
                    "relationships": [dict(rel) for rel in path.relationships]
                }
                paths.append(path_data)
            
            return {
                "entity_id": entity_id,
                "max_depth": max_depth,
                "paths_found": len(paths),
                "paths": paths
            }
    
    def export_knowledge_subgraph(
        self,
        entity_ids: List[str],
        format: str = "json"
    ) -> str:
        """Export a subgraph containing specified entities"""
        if format.lower() != "json":
            raise ValueError("Only JSON format supported for now")
        
        # Query the subgraph
        cypher = (
            "MATCH path = (e:Entity)-[r:RELATIONSHIP]-(o:Entity) "
            "WHERE e.identifier IN $ids OR o.identifier IN $ids "
            "RETURN e, r, o"
        )
        
        with driver.session() as session:
            result = session.run(cypher, ids=entity_ids)
            
            nodes = {}
            relationships = []
            
            for record in result:
                # Add nodes
                for node in [record["e"], record["o"]]:
                    node_dict = dict(node)
                    if node_dict["identifier"] not in nodes:
                        nodes[node_dict["identifier"]] = node_dict
                
                # Add relationship
                rel_dict = dict(record["r"])
                relationships.append(rel_dict)
            
            # Build export structure
            export_data = {
                "nodes": list(nodes.values()),
                "relationships": relationships,
                "entity_count": len(nodes),
                "relationship_count": len(relationships),
                "export_timestamp": datetime.utcnow().isoformat(),
                "format": "knowledge_graph_json",
                "version": "1.0"
            }
            
            return json.dumps(export_data, indent=2)
    
    def shutdown(self) -> None:
        """Shutdown the knowledge graph service"""
        driver.close()


# Singleton instance
knowledge_graph = KnowledgeGraph()