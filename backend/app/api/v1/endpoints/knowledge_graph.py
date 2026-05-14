"""
Knowledge Graph API Endpoints

API endpoints for knowledge graph operations including entity management,
relationship tracking, and knowledge extraction.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.security import get_api_key
from app.database import get_db
from app.services.knowledge_graph import knowledge_graph, EntityType, RelationshipType, KnowledgeStatus
from app.models.sql.website import DiscoveredFile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


# Pydantic Models

class EntityCreate(BaseModel):
    name: str
    entity_type: str
    properties: Dict[str, Any] = {}
    provenance: Dict[str, Any] = None

class EntityUpdate(BaseModel):
    properties: Dict[str, Any] = {}
    new_status: str = None

class RelationshipCreate(BaseModel):
    subject_id: str
    predicate: str
    object_id: str
    properties: Dict[str, Any] = {}
    provenance: Dict[str, Any] = None

class RelationshipUpdate(BaseModel):
    properties: Dict[str, Any] = {}
    new_status: str = None

class KnowledgeExtractionRequest(BaseModel):
    document_id: str
    markdown_content: str
    document_metadata: Dict[str, Any]

class ValidationRequest(BaseModel):
    validator_id: str
    validation_result: bool
    notes: str = None


# Entity Endpoints

@router.post("/entities/", response_model=Dict[str, Any])
async def create_entity(
    entity_data: EntityCreate,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Create a new entity in the knowledge graph
    """
    try:
        entity = knowledge_graph.create_entity(
            name=entity_data.name,
            entity_type=EntityType(entity_data.entity_type),
            properties=entity_data.properties,
            provenance=entity_data.provenance
        )
        return {
            "success": True,
            "entity": entity
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create entity: {str(e)}"
        )


@router.get("/entities/{entity_id}", response_model=Dict[str, Any])
async def get_entity(
    entity_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Retrieve an entity from the knowledge graph
    """
    entity = knowledge_graph.get_entity(entity_id)
    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Entity not found"
        )
    return {
        "success": True,
        "entity": entity
    }


@router.put("/entities/{entity_id}", response_model=Dict[str, Any])
async def update_entity(
    entity_id: str,
    update_data: EntityUpdate,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Update an existing entity
    """
    try:
        new_status = None
        if update_data.new_status:
            new_status = KnowledgeStatus(update_data.new_status)
        
        entity = knowledge_graph.update_entity(
            entity_id=entity_id,
            updates=update_data.properties,
            new_status=new_status
        )
        return {
            "success": True,
            "entity": entity
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update entity: {str(e)}"
        )


@router.get("/entities/", response_model=Dict[str, Any])
async def search_entities(
    query: str = None,
    entity_type: str = None,
    limit: int = 50,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Search for entities in the knowledge graph
    """
    type_filter = None
    if entity_type:
        type_filter = EntityType(entity_type)
    
    entities = knowledge_graph.search_entities(
        query=query,
        entity_type=type_filter,
        limit=limit
    )
    
    return {
        "success": True,
        "entities": entities,
        "count": len(entities)
    }


# Relationship Endpoints

@router.post("/relationships/", response_model=Dict[str, Any])
async def create_relationship(
    relationship_data: RelationshipCreate,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Create a new relationship between entities
    """
    try:
        relationship = knowledge_graph.create_relationship(
            subject_id=relationship_data.subject_id,
            predicate=RelationshipType(relationship_data.predicate),
            object_id=relationship_data.object_id,
            properties=relationship_data.properties,
            provenance=relationship_data.provenance
        )
        return {
            "success": True,
            "relationship": relationship
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create relationship: {str(e)}"
        )


@router.get("/relationships/{relationship_id}", response_model=Dict[str, Any])
async def get_relationship(
    relationship_id: str,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Retrieve a relationship from the knowledge graph
    """
    relationship = knowledge_graph.get_relationship(relationship_id)
    if not relationship:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found"
        )
    return {
        "success": True,
        "relationship": relationship
    }


@router.put("/relationships/{relationship_id}", response_model=Dict[str, Any])
async def update_relationship(
    relationship_id: str,
    update_data: RelationshipUpdate,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Update an existing relationship
    """
    try:
        new_status = None
        if update_data.new_status:
            new_status = KnowledgeStatus(update_data.new_status)
        
        relationship = knowledge_graph.update_relationship(
            relationship_id=relationship_id,
            updates=update_data.properties,
            new_status=new_status
        )
        return {
            "success": True,
            "relationship": relationship
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update relationship: {str(e)}"
        )


@router.get("/entities/{entity_id}/relationships/", response_model=Dict[str, Any])
async def get_entity_relationships(
    entity_id: str,
    relationship_type: str = None,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Get all relationships for an entity
    """
    type_filter = None
    if relationship_type:
        type_filter = RelationshipType(relationship_type)
    
    relationships = knowledge_graph.get_entity_relationships(
        entity_id=entity_id,
        relationship_type=type_filter
    )
    
    return {
        "success": True,
        "relationships": relationships,
        "count": len(relationships)
    }


# Knowledge Extraction Endpoints

@router.post("/extract/", response_model=Dict[str, Any])
async def extract_knowledge(
    extraction_request: KnowledgeExtractionRequest,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Extract knowledge from document content and store in graph
    """
    try:
        result = knowledge_graph.extract_and_store_knowledge(
            document_id=extraction_request.document_id,
            markdown_content=extraction_request.markdown_content,
            document_metadata=extraction_request.document_metadata
        )
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Knowledge extraction failed: {str(e)}"
        )


@router.post("/validate/{entity_id}", response_model=Dict[str, Any])
async def validate_knowledge(
    entity_id: str,
    validation_request: ValidationRequest,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Validate a knowledge entity
    """
    try:
        result = knowledge_graph.validate_knowledge(
            entity_id=entity_id,
            validator_id=validation_request.validator_id,
            validation_result=validation_request.validation_result,
            notes=validation_request.notes
        )
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation failed: {str(e)}"
        )


# Graph Analysis Endpoints

@router.get("/stats/", response_model=Dict[str, Any])
async def get_knowledge_graph_stats(
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Get statistics about the knowledge graph
    """
    stats = knowledge_graph.get_knowledge_graph_stats()
    return {
        "success": True,
        "stats": stats
    }


@router.get("/related/{entity_id}", response_model=Dict[str, Any])
async def find_related_entities(
    entity_id: str,
    max_depth: int = 2,
    relationship_types: List[str] = None,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Find entities related to a given entity
    """
    type_filters = None
    if relationship_types:
        type_filters = [RelationshipType(rt) for rt in relationship_types]
    
    result = knowledge_graph.find_related_entities(
        entity_id=entity_id,
        max_depth=max_depth,
        relationship_types=type_filters
    )
    
    return {
        "success": True,
        **result
    }


@router.post("/export/", response_model=Dict[str, Any])
async def export_knowledge_subgraph(
    entity_ids: List[str],
    format: str = "json",
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Export a subgraph containing specified entities
    """
    try:
        export_data = knowledge_graph.export_knowledge_subgraph(
            entity_ids=entity_ids,
            format=format
        )
        return {
            "success": True,
            "export": export_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Export failed: {str(e)}"
        )


# Integration with Ingestion Pipeline

@router.post("/ingest-from-file/{file_id}", response_model=Dict[str, Any])
async def ingest_file_to_knowledge_graph(
    file_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Ingest a file's content into the knowledge graph
    """
    try:
        # Get file from database
        discovered_file = db.query(DiscoveredFile).filter(DiscoveredFile.id == file_id).first()
        if not discovered_file:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Get file content (in a real implementation, this would come from storage)
        # For now, we'll use the file metadata
        markdown_content = f"# {discovered_file.file_name}\n\n"
        markdown_content += f"**Type:** {discovered_file.file_type}\n\n"
        markdown_content += f"**URL:** {discovered_file.url}\n\n"
        markdown_content += f"**Discovered:** {discovered_file.discovered_at}\n\n"
        
        # Create document metadata
        document_metadata = {
            "title": discovered_file.file_name,
            "source_url": discovered_file.url,
            "file_path": discovered_file.path or "",
            "file_type": discovered_file.file_type.value,
            "document_id": str(file_id),
            "content_hash": discovered_file.content_hash or "",
            "discovered_at": discovered_file.discovered_at.isoformat() if discovered_file.discovered_at else ""
        }
        
        # Extract and store knowledge
        result = knowledge_graph.extract_and_store_knowledge(
            document_id=str(file_id),
            markdown_content=markdown_content,
            document_metadata=document_metadata
        )
        
        # Update file status
        discovered_file.knowledge_graph_status = "INGESTED"
        discovered_file.knowledge_graph_ingested_at = datetime.now()
        db.commit()
        
        return {
            "success": True,
            "file_id": file_id,
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to ingest file to knowledge graph: {str(e)}"
        )


@router.get("/entity-types/", response_model=Dict[str, Any])
async def get_entity_types(
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Get available entity types
    """
    types = [{"value": et.value, "name": et.value} for et in EntityType]
    return {
        "success": True,
        "entity_types": types
    }


@router.get("/relationship-types/", response_model=Dict[str, Any])
async def get_relationship_types(
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Get available relationship types
    """
    types = [{"value": rt.value, "name": rt.value} for rt in RelationshipType]
    return {
        "success": True,
        "relationship_types": types
    }


@router.get("/knowledge-statuses/", response_model=Dict[str, Any])
async def get_knowledge_statuses(
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Get available knowledge statuses
    """
    statuses = [{"value": ks.value, "name": ks.value} for ks in KnowledgeStatus]
    return {
        "success": True,
        "knowledge_statuses": statuses
    }
