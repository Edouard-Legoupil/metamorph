"""Unit tests for Vector Store Service"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.vector_store import VectorStoreService
from fastapi import HTTPException


def test_vector_store_initialization():
    """Test VectorStoreService initialization"""
    # Mock the database connection and extension check
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1,)  # Extension exists
        
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.commit.return_value = None
        
        mock_connect.return_value = mock_conn
        
        # Initialize the service
        service = VectorStoreService()
        
        assert service.dimensions == 384
        assert service.index_type == "HNSW"
        assert service.hnsw_m == 16


def test_store_document_embedding():
    """Test storing document embedding"""
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = {
            "id": 1,
            "document_id": "test-doc-1",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.commit.return_value = None
        
        mock_connect.return_value = mock_conn
        
        service = VectorStoreService()
        
        # Test valid embedding
        embedding = [0.1] * 384  # Correct dimensions
        result = service.store_document_embedding(
            document_id="test-doc-1",
            embedding=embedding,
            document_type="PDF",
            document_source="http://example.com/test.pdf"
        )
        
        assert result["document_id"] == "test-doc-1"
        assert result["id"] == 1


def test_store_document_embedding_dimension_mismatch():
    """Test dimension mismatch error"""
    service = VectorStoreService()
    
    # Test wrong dimensions
    embedding = [0.1] * 100  # Wrong dimensions
    
    with pytest.raises(HTTPException) as exc_info:
        service.store_document_embedding(
            document_id="test-doc-1",
            embedding=embedding,
            document_type="PDF"
        )
    
    assert exc_info.value.status_code == 400
    assert "dimension mismatch" in str(exc_info.value.detail)


def test_semantic_search_documents():
    """Test semantic search on documents"""
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            {
                "id": 1,
                "document_id": "test-doc-1",
                "document_type": "PDF",
                "document_source": "http://example.com/test.pdf",
                "metadata": {"title": "Test Document"},
                "similarity_score": 0.95
            }
        ]
        
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        
        mock_connect.return_value = mock_conn
        
        service = VectorStoreService()
        
        # Test search
        embedding = [0.1] * 384
        results = service.semantic_search_documents(
            query_embedding=embedding,
            limit=10,
            min_score=0.1
        )
        
        assert len(results) == 1
        assert results[0]["document_id"] == "test-doc-1"
        assert results[0]["similarity_score"] == 0.95


def test_hybrid_search():
    """Test hybrid search combining vector and text"""
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            {
                "id": 1,
                "document_id": "test-doc-1",
                "document_type": "PDF",
                "document_source": "http://example.com/test.pdf",
                "metadata": {"title": "Test Document"},
                "similarity_score": 0.95,
                "text_score": 0.85,
                "combined_score": 0.92
            }
        ]
        
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        
        mock_connect.return_value = mock_conn
        
        service = VectorStoreService()
        
        # Test hybrid search
        embedding = [0.1] * 384
        results = service.hybrid_search(
            query_embedding=embedding,
            text_query="test query",
            limit=10,
            min_score=0.1
        )
        
        assert len(results) == 1
        assert results[0]["combined_score"] == 0.92


def test_get_embedding_stats():
    """Test getting vector store statistics"""
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        
        # Mock document stats
        doc_result = MagicMock()
        doc_result.fetchone.return_value = {
            "document_count": 100,
            "type_count": 5
        }
        
        # Mock knowledge card stats
        card_result = MagicMock()
        card_result.fetchone.return_value = {
            "card_count": 50,
            "unique_cards": 20,
            "section_count": 30
        }
        
        mock_conn.execute.side_effect = [doc_result, card_result]
        mock_conn.__enter__.return_value = mock_conn
        
        mock_connect.return_value = mock_conn
        
        service = VectorStoreService()
        
        stats = service.get_embedding_stats()
        
        assert stats["documents"]["document_count"] == 100
        assert stats["documents"]["type_count"] == 5
        assert stats["knowledge_cards"]["card_count"] == 50
        assert stats["dimensions"] == 384


def test_delete_document_embedding():
    """Test deleting document embedding"""
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1  # One row deleted
        
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.commit.return_value = None
        
        mock_connect.return_value = mock_conn
        
        service = VectorStoreService()
        
        # Test deletion
        success = service.delete_document_embedding("test-doc-1")
        assert success is True


def test_delete_nonexistent_document():
    """Test deleting non-existent document"""
    with patch('app.services.vector_store.engine.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 0  # No rows deleted
        
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.commit.return_value = None
        
        mock_connect.return_value = mock_conn
        
        service = VectorStoreService()
        
        # Test deletion of non-existent document
        success = service.delete_document_embedding("nonexistent-doc")
        assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
