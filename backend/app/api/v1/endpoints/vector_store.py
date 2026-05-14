"""
Vector Store API Endpoints

Provides RESTful endpoints for vector operations including:
- Storing and retrieving document embeddings
- Semantic search on documents and knowledge cards
- Hybrid search combining vector and text search
- Vector store statistics and management
"""

from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Dict, Any
from pydantic import BaseModel

from app.services.vector_store import vector_store_service


router = APIRouter(
    prefix="/vector",
    tags=["vector"],
    responses={404: {"description": "Not found"}}
)


class EmbeddingRequest(BaseModel):
    """Request model for storing embeddings"""
    embedding: List[float]
    document_type: str = "unknown"
    document_source: str = ""
    metadata: Dict[str, Any] = {}


class KnowledgeCardEmbeddingRequest(BaseModel):
    """Request model for storing knowledge card embeddings"""
    card_id: str
    section_name: str
    embedding: List[float]
    card_type: str = "unknown"
    content_text: str = ""
    metadata: Dict[str, Any] = {}


class SearchRequest(BaseModel):
    """Request model for search operations"""
    embedding: List[float]
    limit: int = 10
    min_score: float = 0.1


class HybridSearchRequest(BaseModel):
    """Request model for hybrid search operations"""
    embedding: List[float]
    text_query: str = ""
    limit: int = 10
    min_score: float = 0.1


@router.post("/documents/", response_model=Dict[str, Any])
async def store_document_embedding(
    document_id: str = Query(..., description="Unique document identifier"),
    request: EmbeddingRequest = Body(...)
):
    """
    Store a document embedding in the vector store
    
    Args:
        document_id: Unique identifier for the document
        request: EmbeddingRequest containing embedding and metadata
        
    Returns:
        Dictionary with storage result including id and timestamps
    """
    try:
        result = vector_store_service.store_document_embedding(
            document_id=document_id,
            embedding=request.embedding,
            document_type=request.document_type,
            document_source=request.document_source,
            metadata=request.metadata
        )
        return {
            "success": True,
            "data": result,
            "message": "Document embedding stored successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-cards/", response_model=Dict[str, Any])
async def store_knowledge_card_embedding(
    request: KnowledgeCardEmbeddingRequest = Body(...)
):
    """
    Store a knowledge card section embedding in the vector store
    
    Args:
        request: KnowledgeCardEmbeddingRequest containing card and embedding info
        
    Returns:
        Dictionary with storage result including id and timestamps
    """
    try:
        result = vector_store_service.store_knowledge_card_embedding(
            card_id=request.card_id,
            section_name=request.section_name,
            embedding=request.embedding,
            card_type=request.card_type,
            content_text=request.content_text,
            metadata=request.metadata
        )
        return {
            "success": True,
            "data": result,
            "message": "Knowledge card embedding stored successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/search", response_model=Dict[str, Any])
async def semantic_search_documents(
    request: SearchRequest = Body(...)
):
    """
    Perform semantic search on documents using vector similarity
    
    Args:
        request: SearchRequest containing query embedding and parameters
        
    Returns:
        Dictionary with search results including similarity scores
    """
    try:
        results = vector_store_service.semantic_search_documents(
            query_embedding=request.embedding,
            limit=request.limit,
            min_score=request.min_score
        )
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} document matches"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-cards/search", response_model=Dict[str, Any])
async def semantic_search_knowledge_cards(
    request: SearchRequest = Body(...)
):
    """
    Perform semantic search on knowledge card sections using vector similarity
    
    Args:
        request: SearchRequest containing query embedding and parameters
        
    Returns:
        Dictionary with search results including similarity scores
    """
    try:
        results = vector_store_service.semantic_search_knowledge_cards(
            query_embedding=request.embedding,
            limit=request.limit,
            min_score=request.min_score
        )
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} knowledge card matches"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid-search", response_model=Dict[str, Any])
async def hybrid_search(
    request: HybridSearchRequest = Body(...)
):
    """
    Perform hybrid search combining vector similarity and text search
    
    Args:
        request: HybridSearchRequest containing embedding and text query
        
    Returns:
        Dictionary with hybrid search results including combined scores
    """
    try:
        results = vector_store_service.hybrid_search(
            query_embedding=request.embedding,
            text_query=request.text_query,
            limit=request.limit,
            min_score=request.min_score
        )
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} hybrid search matches"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, Any])
async def get_vector_stats():
    """
    Get statistics about the vector store
    
    Returns:
        Dictionary with statistics about documents and knowledge cards
    """
    try:
        stats = vector_store_service.get_embedding_stats()
        return {
            "success": True,
            "stats": stats,
            "message": "Vector store statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}", response_model=Dict[str, Any])
async def delete_document_embedding(
    document_id: str
):
    """
    Delete a document embedding from the vector store
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Dictionary with deletion result
    """
    try:
        success = vector_store_service.delete_document_embedding(document_id)
        if success:
            return {
                "success": True,
                "document_id": document_id,
                "message": "Document embedding deleted successfully"
            }
        else:
            return {
                "success": False,
                "document_id": document_id,
                "message": "Document embedding not found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge-cards/{card_id}", response_model=Dict[str, Any])
async def delete_knowledge_card_embeddings(
    card_id: str
):
    """
    Delete all embeddings for a knowledge card
    
    Args:
        card_id: ID of the knowledge card to delete
        
    Returns:
        Dictionary with deletion result
    """
    try:
        success = vector_store_service.delete_knowledge_card_embeddings(card_id)
        if success:
            return {
                "success": True,
                "card_id": card_id,
                "message": "Knowledge card embeddings deleted successfully"
            }
        else:
            return {
                "success": False,
                "card_id": card_id,
                "message": "No knowledge card embeddings found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def vector_health_check():
    """
    Health check endpoint for vector store service
    
    Returns:
        Dictionary with health status
    """
    try:
        # Test database connection
        stats = vector_store_service.get_embedding_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "pgvector": "enabled",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
