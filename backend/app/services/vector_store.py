"""
Vector Store Service using PostgreSQL pgvector extension

Provides semantic search, similarity matching, and hybrid query capabilities
using PostgreSQL's pgvector extension for efficient vector operations.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sqlalchemy import text, bindparam
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.core.config import settings
from app.database import engine


class VectorStoreService:
    """Service for vector-based operations using pgvector"""
    
    def __init__(self):
        self.db_url = settings.sqlalchemy_database_url
        self.dimensions = int(os.getenv("VECTOR_DIMENSIONS", "384"))
        self.index_type = os.getenv("VECTOR_INDEX_TYPE", "HNSW")
        self.hnsw_m = int(os.getenv("VECTOR_M", "16"))
        self.hnsw_ef_construction = int(os.getenv("VECTOR_EF_CONSTRUCTION", "64"))
        self.hnsw_ef_search = int(os.getenv("VECTOR_EF_SEARCH", "40"))
        
        # Ensure pgvector extension is available
        self._ensure_pgvector_extension()
        
        # Create tables if they don't exist
        self._initialize_vector_tables()
    
    def _ensure_pgvector_extension(self) -> None:
        """Ensure pgvector extension is enabled in the database"""
        try:
            with engine.connect() as conn:
                # Check if extension exists
                result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
                if result.fetchone() is None:
                    # Enable the extension
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    print("✅ pgvector extension enabled successfully")
                else:
                    print("✅ pgvector extension already enabled")
        except SQLAlchemyError as e:
            print(f"❌ Error enabling pgvector extension: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enable pgvector extension: {str(e)}"
            )
    
    def _initialize_vector_tables(self) -> None:
        """Create vector tables if they don't exist"""
        try:
            with engine.connect() as conn:
                # Create document embeddings table
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) NOT NULL,
                    document_type VARCHAR(50),
                    document_source VARCHAR(255),
                    embedding vector(:dimensions) NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(document_id)
                )
                """).bindparams(dimensions=self.dimensions))
                
                # Create index based on configuration
                if self.index_type.upper() == "HNSW":
                    conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_document_embeddings_hnsw 
                    ON document_embeddings USING hnsw (embedding vector_l2_ops)
                    """))
                else:  # IVFFlat
                    conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_document_embeddings_ivfflat 
                    ON document_embeddings USING ivfflat (embedding vector_l2_ops)
                    """))
                
                # Create index for document_id lookup
                conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_embeddings_doc_id 
                ON document_embeddings (document_id)
                """))
                
                # Create knowledge card embeddings table
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS knowledge_card_embeddings (
                    id SERIAL PRIMARY KEY,
                    card_id VARCHAR(50) NOT NULL,
                    card_type VARCHAR(50),
                    section_name VARCHAR(100),
                    embedding vector(:dimensions) NOT NULL,
                    content_text TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                """).bindparams(dimensions=self.dimensions))
                
                # Create index for knowledge card embeddings
                if self.index_type.upper() == "HNSW":
                    conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_knowledge_card_embeddings_hnsw 
                    ON knowledge_card_embeddings USING hnsw (embedding vector_l2_ops)
                    """))
                else:  # IVFFlat
                    conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_knowledge_card_embeddings_ivfflat 
                    ON knowledge_card_embeddings USING ivfflat (embedding vector_l2_ops)
                    """))
                
                conn.commit()
                print("✅ Vector tables initialized successfully")
        except SQLAlchemyError as e:
            print(f"❌ Error initializing vector tables: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize vector tables: {str(e)}"
            )
    
    def store_document_embedding(
        self, 
        document_id: str, 
        embedding: List[float], 
        document_type: str = "unknown",
        document_source: str = "",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Store a document embedding in the vector store"""
        if len(embedding) != self.dimensions:
            raise HTTPException(
                status_code=400,
                detail=f"Embedding dimension mismatch. Expected {self.dimensions}, got {len(embedding)}"
            )
        
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    INSERT INTO document_embeddings 
                    (document_id, document_type, document_source, embedding, metadata)
                    VALUES (:document_id, :document_type, :document_source, :embedding, :metadata)
                    ON CONFLICT (document_id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        document_type = EXCLUDED.document_type,
                        document_source = EXCLUDED.document_source,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id, document_id, created_at, updated_at
                    """
                ), {
                    "document_id": document_id,
                    "document_type": document_type,
                    "document_source": document_source,
                    "embedding": embedding,
                    "metadata": metadata or {}
                })
                
                conn.commit()
                return dict(result.fetchone())
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store document embedding: {str(e)}"
            )
    
    def store_knowledge_card_embedding(
        self, 
        card_id: str, 
        section_name: str, 
        embedding: List[float],
        card_type: str = "unknown",
        content_text: str = "",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Store a knowledge card section embedding in the vector store"""
        if len(embedding) != self.dimensions:
            raise HTTPException(
                status_code=400,
                detail=f"Embedding dimension mismatch. Expected {self.dimensions}, got {len(embedding)}"
            )
        
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    INSERT INTO knowledge_card_embeddings 
                    (card_id, card_type, section_name, embedding, content_text, metadata)
                    VALUES (:card_id, :card_type, :section_name, :embedding, :content_text, :metadata)
                    RETURNING id, card_id, section_name, created_at
                    """
                ), {
                    "card_id": card_id,
                    "card_type": card_type,
                    "section_name": section_name,
                    "embedding": embedding,
                    "content_text": content_text,
                    "metadata": metadata or {}
                })
                
                conn.commit()
                return dict(result.fetchone())
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store knowledge card embedding: {str(e)}"
            )
    
    def semantic_search_documents(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on documents using vector similarity"""
        if len(query_embedding) != self.dimensions:
            raise HTTPException(
                status_code=400,
                detail=f"Query embedding dimension mismatch. Expected {self.dimensions}, got {len(query_embedding)}"
            )
        
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT 
                        id, 
                        document_id, 
                        document_type, 
                        document_source, 
                        metadata,
                        1 - (embedding <=> :query_embedding) AS similarity_score
                    FROM document_embeddings
                    WHERE 1 - (embedding <=> :query_embedding) > :min_score
                    ORDER BY similarity_score DESC
                    LIMIT :limit
                    """
                ), {
                    "query_embedding": query_embedding,
                    "min_score": min_score,
                    "limit": limit
                })
                
                return [dict(row) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to perform semantic search: {str(e)}"
            )
    
    def semantic_search_knowledge_cards(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on knowledge card sections using vector similarity"""
        if len(query_embedding) != self.dimensions:
            raise HTTPException(
                status_code=400,
                detail=f"Query embedding dimension mismatch. Expected {self.dimensions}, got {len(query_embedding)}"
            )
        
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT 
                        id, 
                        card_id, 
                        card_type, 
                        section_name, 
                        content_text,
                        metadata,
                        1 - (embedding <=> :query_embedding) AS similarity_score
                    FROM knowledge_card_embeddings
                    WHERE 1 - (embedding <=> :query_embedding) > :min_score
                    ORDER BY similarity_score DESC
                    LIMIT :limit
                    """
                ), {
                    "query_embedding": query_embedding,
                    "min_score": min_score,
                    "limit": limit
                })
                
                return [dict(row) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to perform knowledge card semantic search: {str(e)}"
            )
    
    def hybrid_search(
        self, 
        query_embedding: List[float],
        text_query: str = "",
        limit: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector similarity and text search"""
        if len(query_embedding) != self.dimensions:
            raise HTTPException(
                status_code=400,
                detail=f"Query embedding dimension mismatch. Expected {self.dimensions}, got {len(query_embedding)}"
            )
        
        try:
            with engine.connect() as conn:
                # Combine vector similarity with text search
                result = conn.execute(
                    text("""
                    SELECT 
                        id, 
                        document_id, 
                        document_type, 
                        document_source, 
                        metadata,
                        1 - (embedding <=> :query_embedding) AS similarity_score,
                        ts_rank(
                            to_tsvector('english', document_source || ' ' || COALESCE(metadata->>'title', '')),
                            plainto_tsquery('english', :text_query)
                        ) AS text_score,
                        (1 - (embedding <=> :query_embedding)) * 0.7 + 
                        ts_rank(
                            to_tsvector('english', document_source || ' ' || COALESCE(metadata->>'title', '')),
                            plainto_tsquery('english', :text_query)
                        ) * 0.3 AS combined_score
                    FROM document_embeddings
                    WHERE 
                        1 - (embedding <=> :query_embedding) > :min_score
                        AND (:text_query = '' OR 
                            to_tsvector('english', document_source || ' ' || COALESCE(metadata->>'title', '')) @@ 
                            plainto_tsquery('english', :text_query))
                    ORDER BY combined_score DESC
                    LIMIT :limit
                    """
                ), {
                    "query_embedding": query_embedding,
                    "text_query": text_query,
                    "min_score": min_score,
                    "limit": limit
                })
                
                return [dict(row) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to perform hybrid search: {str(e)}"
            )
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            with engine.connect() as conn:
                # Get document embeddings stats
                doc_result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as document_count,
                        COUNT(DISTINCT document_type) as type_count
                    FROM document_embeddings
                """))
                
                # Get knowledge card embeddings stats
                card_result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as card_count,
                        COUNT(DISTINCT card_id) as unique_cards,
                        COUNT(DISTINCT section_name) as section_count
                    FROM knowledge_card_embeddings
                """))
                
                return {
                    "documents": dict(doc_result.fetchone()),
                    "knowledge_cards": dict(card_result.fetchone()),
                    "dimensions": self.dimensions,
                    "index_type": self.index_type
                }
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get embedding stats: {str(e)}"
            )
    
    def delete_document_embedding(self, document_id: str) -> bool:
        """Delete a document embedding from the vector store"""
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    DELETE FROM document_embeddings 
                    WHERE document_id = :document_id
                    """
                ), {"document_id": document_id})
                
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document embedding: {str(e)}"
            )
    
    def delete_knowledge_card_embeddings(self, card_id: str) -> bool:
        """Delete all embeddings for a knowledge card"""
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                    DELETE FROM knowledge_card_embeddings 
                    WHERE card_id = :card_id
                    """
                ), {"card_id": card_id})
                
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete knowledge card embeddings: {str(e)}"
            )


# Singleton instance
vector_store_service = VectorStoreService()
