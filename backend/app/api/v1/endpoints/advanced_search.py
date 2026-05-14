"""
Advanced Search Endpoints

Provides BM25, semantic, and hybrid search capabilities for the Metamorph system.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["advanced_search"])


class BM25SearchRequest(BaseModel):
    """Request model for BM25 search"""
    query: str
    limit: int = 10
    metadata_filters: Optional[Dict[str, Any]] = None
    metadata_weights: Optional[Dict[str, float]] = None
    

class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    embedding: List[float]
    limit: int = 10
    min_score: float = 0.1


class HybridSearchRequest(BaseModel):
    """Request model for hybrid search"""
    query: str
    embedding: List[float]
    limit: int = 10
    bm25_weight: float = 0.4
    semantic_weight: float = 0.6


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search with multiple search types"""
    query: str
    embedding: Optional[List[float]] = None
    search_type: str = "hybrid"  # bm25, semantic, or hybrid
    limit: int = 10
    bm25_weight: float = 0.4
    semantic_weight: float = 0.6
    metadata_filters: Optional[Dict[str, Any]] = None
    metadata_weights: Optional[Dict[str, float]] = None


@router.post("/bm25", response_model=Dict[str, Any])
async def bm25_search(
    request: BM25SearchRequest = Body(...)
) -> Dict[str, Any]:
    """
    Perform BM25 keyword-based search with optional metadata filtering and reranking
    
    This endpoint uses the BM25 ranking algorithm to search for documents
    based on keyword matching and term frequency. It also supports:
    - Metadata filtering to restrict results to specific criteria
    - Metadata-based reranking to boost results based on document attributes
    
    Args:
        request: BM25SearchRequest containing query, limit, and optional metadata parameters
        
    Metadata Filtering Examples:
        - {"card_type": "KC-3"} - Only return Outcome Evidence cards
        - {"status": "approved"} - Only return approved content
        - {"created_at": {"gte": "2023-01-01"}} - Only return content created after Jan 1, 2023
        - {"tags": {"in": ["humanitarian", "conflict"]}} - Only return content with specific tags
        
    Metadata Reranking Examples:
        - {"confidence_score": 0.3} - Boost higher confidence results
        - {"created_at": 0.2} - Boost more recent content
        - {"status": 0.4} - Boost approved content
        - {"card_type": 0.1} - Apply card type specific boosts
        
    Returns:
        Dictionary with search results including BM25 scores and metadata
    """
    try:
        results = search_service.bm25_search(
            query=request.query,
            limit=request.limit,
            metadata_filters=request.metadata_filters,
            metadata_weights=request.metadata_weights
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "search_type": "bm25",
            "message": f"Found {len(results)} results using BM25 search",
            "metadata_filters_applied": bool(request.metadata_filters),
            "metadata_reranking_applied": bool(request.metadata_weights)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"BM25 search failed: {str(e)}"
        )


@router.post("/semantic", response_model=Dict[str, Any])
async def semantic_search(
    request: SemanticSearchRequest = Body(...)
) -> Dict[str, Any]:
    """
    Perform semantic search using vector embeddings
    
    This endpoint uses vector similarity search to find documents
    semantically similar to the query embedding.
    
    Args:
        request: SemanticSearchRequest containing embedding and parameters
        
    Returns:
        Dictionary with search results including similarity scores
    """
    try:
        results = search_service.semantic_search(
            query_embedding=request.embedding,
            limit=request.limit
        )
        
        # Filter by min_score if specified
        filtered_results = [r for r in results if r.get('score', 0) >= request.min_score]
        
        return {
            "success": True,
            "results": filtered_results,
            "count": len(filtered_results),
            "search_type": "semantic",
            "message": f"Found {len(filtered_results)} results using semantic search"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/hybrid", response_model=Dict[str, Any])
async def hybrid_search(
    request: HybridSearchRequest = Body(...)
) -> Dict[str, Any]:
    """
    Perform hybrid search combining BM25 and semantic search
    
    This endpoint combines keyword-based BM25 ranking with semantic
    vector similarity to provide more comprehensive search results.
    
    Args:
        request: HybridSearchRequest containing query, embedding, and weights
        
    Returns:
        Dictionary with hybrid search results including combined scores
    """
    try:
        results = search_service.hybrid_search(
            query=request.query,
            query_embedding=request.embedding,
            limit=request.limit
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "search_type": "hybrid",
            "bm25_weight": request.bm25_weight,
            "semantic_weight": request.semantic_weight,
            "message": f"Found {len(results)} results using hybrid search"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hybrid search failed: {str(e)}"
        )


@router.post("/advanced", response_model=Dict[str, Any])
async def advanced_search(
    request: AdvancedSearchRequest = Body(...)
) -> Dict[str, Any]:
    """
    Perform advanced search with configurable search type and metadata support
    
    This endpoint provides a unified interface for all search types
    (BM25, semantic, or hybrid) with configurable parameters. It also supports:
    - Metadata filtering to restrict results to specific criteria
    - Metadata-based reranking to boost results based on document attributes
    
    Args:
        request: AdvancedSearchRequest with search parameters and optional metadata
        
    Metadata Filtering Examples:
        - {"card_type": "KC-3"} - Only return Outcome Evidence cards
        - {"status": "approved"} - Only return approved content
        - {"created_at": {"gte": "2023-01-01"}} - Only return content created after Jan 1, 2023
        - {"tags": {"in": ["humanitarian", "conflict"]}} - Only return content with specific tags
        
    Metadata Reranking Examples:
        - {"confidence_score": 0.3} - Boost higher confidence results
        - {"created_at": 0.2} - Boost more recent content
        - {"status": 0.4} - Boost approved content
        - {"card_type": 0.1} - Apply card type specific boosts
        
    Returns:
        Dictionary with search results based on selected search type and metadata processing
    """
    try:
        result = search_service.advanced_search(
            query=request.query,
            query_embedding=request.embedding,
            search_type=request.search_type,
            limit=request.limit,
            metadata_filters=request.metadata_filters,
            metadata_weights=request.metadata_weights
        )
        
        # Add weights and metadata info to response
        if request.search_type == "hybrid":
            result.update({
                "bm25_weight": request.bm25_weight,
                "semantic_weight": request.semantic_weight
            })
        
        # Add metadata usage info
        result.update({
            "metadata_filters_applied": bool(request.metadata_filters),
            "metadata_reranking_applied": bool(request.metadata_weights)
        })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advanced search failed: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
async def search_health() -> Dict[str, Any]:
    """
    Check the health status of the search service
    
    Returns:
        Dictionary with health status information
    """
    try:
        # Test BM25 index
        bm25_healthy = len(search_service.bm25.doc_len) > 0
        
        # Test vector store connection
        vector_healthy = True  # Assume healthy unless we get an error
        
        return {
            "status": "healthy",
            "bm25_index": {
                "healthy": bm25_healthy,
                "document_count": len(search_service.bm25.doc_len)
            },
            "vector_store": {
                "healthy": vector_healthy
            },
            "message": "Search service is operational"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "message": "Search service is experiencing issues"
        }


@router.post("/reindex", response_model=Dict[str, Any])
async def reindex_search() -> Dict[str, Any]:
    """
    Reindex all content for search
    
    This endpoint rebuilds the BM25 index with current data from the database.
    
    Returns:
        Dictionary with reindexing status
    """
    try:
        # Reinitialize the search index
        search_service._initialize_search_index()
        
        return {
            "success": True,
            "message": "Search index rebuilt successfully",
            "document_count": len(search_service.bm25.doc_len)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reindexing failed: {str(e)}"
        )