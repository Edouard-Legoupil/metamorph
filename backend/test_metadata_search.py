#!/usr/bin/env python3
"""
Test script to verify metadata-based search functionality.
This test focuses on the metadata filtering and reranking capabilities.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_bm25_metadata_methods():
    """Test BM25 metadata filtering and reranking methods."""
    try:
        from app.services.search_service import BM25
        
        print("🔍 Testing BM25 metadata methods...")
        
        # Create BM25 instance
        bm25 = BM25()
        
        # Add test documents with metadata
        test_docs = [
            ("doc1", "humanitarian crisis in Sudan", {
                "card_type": "KC-3",
                "status": "approved", 
                "created_at": datetime.now() - timedelta(days=10),
                "confidence_score": 0.9,
                "tags": ["humanitarian", "conflict"]
            }),
            ("doc2", "economic development in Kenya", {
                "card_type": "KC-6",
                "status": "draft",
                "created_at": datetime.now() - timedelta(days=100),
                "confidence_score": 0.6,
                "tags": ["economic", "development"]
            }),
            ("doc3", "refugee crisis management", {
                "card_type": "KC-3",
                "status": "approved",
                "created_at": datetime.now() - timedelta(days=5),
                "confidence_score": 0.8,
                "tags": ["humanitarian", "refugees"]
            })
        ]
        
        for doc_id, text, metadata in test_docs:
            bm25.add_document(doc_id, text, metadata)
        
        print("✅ Added 3 test documents with metadata")
        
        # Test metadata filtering
        print("\n🧪 Testing metadata filtering...")
        
        # Filter by card type
        filtered_by_type = bm25.filter_by_metadata({"card_type": "KC-3"})
        print(f"   Filter by card_type='KC-3': {filtered_by_type}")
        assert len(filtered_by_type) == 2, f"Expected 2 KC-3 docs, got {len(filtered_by_type)}"
        
        # Filter by status
        filtered_by_status = bm25.filter_by_metadata({"status": "approved"})
        print(f"   Filter by status='approved': {filtered_by_status}")
        assert len(filtered_by_status) == 2, f"Expected 2 approved docs, got {len(filtered_by_status)}"
        
        # Filter by date range
        ten_days_ago = datetime.now() - timedelta(days=10)
        filtered_by_date = bm25.filter_by_metadata({
            "created_at": {"gte": ten_days_ago}
        })
        print(f"   Filter by created_at >= 10 days ago: {filtered_by_date}")
        assert len(filtered_by_date) == 2, f"Expected 2 recent docs, got {len(filtered_by_date)}"
        
        # Filter by tags
        filtered_by_tags = bm25.filter_by_metadata({
            "tags": {"in": ["humanitarian"]}
        })
        print(f"   Filter by tags containing 'humanitarian': {filtered_by_tags}")
        assert len(filtered_by_tags) == 2, f"Expected 2 humanitarian docs, got {len(filtered_by_tags)}"
        
        print("✅ Metadata filtering tests passed!")
        
        # Test metadata reranking
        print("\n🧪 Testing metadata reranking...")
        
        # Create base scores (simulating BM25 results)
        base_scores = {
            "doc1": 1.5,
            "doc2": 1.6,
            "doc3": 1.4
        }
        
        print(f"   Base scores: {base_scores}")
        
        # Test confidence score boost
        confidence_boosted = bm25.rerank_by_metadata(base_scores, {"confidence_score": 0.3})
        print(f"   After confidence boost (0.3): {confidence_boosted}")
        
        # doc1 should be boosted the most (confidence 0.9)
        assert confidence_boosted["doc1"] > confidence_boosted["doc3"], "doc1 should have higher score than doc3"
        assert confidence_boosted["doc3"] > confidence_boosted["doc2"], "doc3 should have higher score than doc2"
        
        # Test recency boost
        recency_boosted = bm25.rerank_by_metadata(base_scores, {"created_at": 0.4})
        print(f"   After recency boost (0.4): {recency_boosted}")
        
        # doc3 should be boosted the most (created 5 days ago)
        assert recency_boosted["doc3"] > recency_boosted["doc1"], "doc3 should have higher recency score than doc1"
        assert recency_boosted["doc1"] > recency_boosted["doc2"], "doc1 should have higher recency score than doc2"
        
        # Test status boost
        status_boosted = bm25.rerank_by_metadata(base_scores, {"status": 0.5})
        print(f"   After status boost (0.5): {status_boosted}")
        
        # doc1 and doc3 should be boosted (both approved), doc2 should not
        assert status_boosted["doc1"] > base_scores["doc1"], "doc1 should be boosted"
        assert status_boosted["doc3"] > base_scores["doc3"], "doc3 should be boosted"
        assert status_boosted["doc2"] == base_scores["doc2"], "doc2 should not be boosted"
        
        # Test combined boosts
        combined_boosted = bm25.rerank_by_metadata(base_scores, {
            "confidence_score": 0.2,
            "created_at": 0.2,
            "status": 0.2
        })
        print(f"   After combined boosts: {combined_boosted}")
        
        # doc1 should win overall (high confidence, recent, approved)
        scores_sorted = sorted(combined_boosted.items(), key=lambda x: x[1], reverse=True)
        print(f"   Final ranking: {scores_sorted}")
        assert scores_sorted[0][0] == "doc1", "doc1 should be ranked first with combined boosts"
        
        print("✅ Metadata reranking tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ BM25 metadata test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_service_integration():
    """Test that search service properly uses metadata."""
    try:
        print("\n🔍 Testing search service metadata integration...")
        
        # Test that the search service methods accept metadata parameters
        from app.services.search_service import SearchService
        
        # Create a mock search service (we can't test full functionality without DB)
        service = SearchService()
        
        # Verify that bm25_search method signature includes metadata parameters
        import inspect
        sig = inspect.signature(service.bm25_search)
        params = list(sig.parameters.keys())
        
        print(f"   bm25_search parameters: {params}")
        assert "metadata_filters" in params, "bm25_search should accept metadata_filters"
        assert "metadata_weights" in params, "bm25_search should accept metadata_weights"
        
        # Verify advanced_search method signature
        sig = inspect.signature(service.advanced_search)
        params = list(sig.parameters.keys())
        
        print(f"   advanced_search parameters: {params}")
        assert "metadata_filters" in params, "advanced_search should accept metadata_filters"
        assert "metadata_weights" in params, "advanced_search should accept metadata_weights"
        
        print("✅ Search service metadata integration tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Search service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_models():
    """Test that endpoint models include metadata fields."""
    try:
        print("\n🔍 Testing endpoint models...")
        
        from app.api.v1.endpoints.advanced_search import BM25SearchRequest, AdvancedSearchRequest
        import inspect
        
        # Check BM25SearchRequest
        sig = inspect.signature(BM25SearchRequest)
        # For Pydantic models, we need to check the fields differently
        bm25_fields = BM25SearchRequest.__fields__.keys()
        print(f"   BM25SearchRequest fields: {list(bm25_fields)}")
        
        assert "metadata_filters" in bm25_fields, "BM25SearchRequest should have metadata_filters field"
        assert "metadata_weights" in bm25_fields, "BM25SearchRequest should have metadata_weights field"
        
        # Check AdvancedSearchRequest
        advanced_fields = AdvancedSearchRequest.__fields__.keys()
        print(f"   AdvancedSearchRequest fields: {list(advanced_fields)}")
        
        assert "metadata_filters" in advanced_fields, "AdvancedSearchRequest should have metadata_filters field"
        assert "metadata_weights" in advanced_fields, "AdvancedSearchRequest should have metadata_weights field"
        
        print("✅ Endpoint model tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all metadata search tests."""
    print("🧪 Testing Metadata-Based Search Functionality")
    print("=" * 60)
    
    tests = [
        test_bm25_metadata_methods,
        test_search_service_integration,
        test_endpoint_models
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Metadata Search Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    if all(results):
        print("\n🎉 All metadata search tests passed!")
        print("\n✅ Metadata-based search functionality is working correctly!")
        print("\n📋 Features implemented:")
        print("   • Metadata filtering (card_type, status, dates, tags, etc.)")
        print("   • Metadata-based reranking (confidence, recency, status, etc.)")
        print("   • Combined filtering and reranking")
        print("   • Integration with BM25 and hybrid search")
        print("   • Comprehensive API endpoints with metadata support")
        return 0
    else:
        print(f"\n💥 {total - passed} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())