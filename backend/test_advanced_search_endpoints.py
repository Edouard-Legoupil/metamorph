#!/usr/bin/env python3
"""
Test script to verify advanced search endpoints are properly configured.
This test focuses on endpoint structure and doesn't require database connectivity.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_endpoints_structure():
    """Test that the advanced search endpoints have the correct structure."""
    try:
        print("🔍 Analyzing advanced search endpoints structure...")
        
        # Read the advanced_search.py file
        with open('app/api/v1/endpoints/advanced_search.py', 'r') as f:
            content = f.read()
        
        # Check for expected endpoint definitions
        expected_endpoints = [
            '@router.post("/bm25"',
            '@router.post("/semantic"', 
            '@router.post("/hybrid"',
            '@router.post("/advanced"',
            '@router.get("/health"',
            '@router.post("/reindex"'
        ]
        
        found_endpoints = []
        for endpoint in expected_endpoints:
            if endpoint in content:
                found_endpoints.append(endpoint)
                print(f"✅ Found: {endpoint}")
            else:
                print(f"❌ Missing: {endpoint}")
        
        if len(found_endpoints) == len(expected_endpoints):
            print(f"\n🎉 All {len(expected_endpoints)} expected endpoints found!")
            return True
        else:
            print(f"\n⚠️  Only {len(found_endpoints)}/{len(expected_endpoints)} endpoints found")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing endpoints: {e}")
        return False

def test_router_registration():
    """Test that the router is properly registered in main.py."""
    try:
        print("\n🔍 Checking router registration in main.py...")
        
        # Read the main.py file
        with open('app/main.py', 'r') as f:
            content = f.read()
        
        # Check for import
        import_check = "from app.api.v1.endpoints.advanced_search import router as advanced_search_router"
        if import_check in content:
            print("✅ Found router import")
        else:
            print("❌ Missing router import")
            return False
        
        # Check for router inclusion
        include_check = "app.include_router(advanced_search_router, prefix=\"/api/v1\")"
        if include_check in content:
            print("✅ Found router inclusion")
        else:
            print("❌ Missing router inclusion")
            return False
            
        print("🎉 Router registration is complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking router registration: {e}")
        return False

def test_pydantic_models():
    """Test that the required Pydantic models are defined."""
    try:
        print("\n🔍 Checking Pydantic models...")
        
        # Read the advanced_search.py file
        with open('app/api/v1/endpoints/advanced_search.py', 'r') as f:
            content = f.read()
        
        expected_models = [
            'class BM25SearchRequest(BaseModel):',
            'class SemanticSearchRequest(BaseModel):',
            'class HybridSearchRequest(BaseModel):',
            'class AdvancedSearchRequest(BaseModel):'
        ]
        
        found_models = []
        for model in expected_models:
            if model in content:
                found_models.append(model)
                print(f"✅ Found: {model}")
            else:
                print(f"❌ Missing: {model}")
        
        if len(found_models) == len(expected_models):
            print(f"🎉 All {len(expected_models)} expected models found!")
            return True
        else:
            print(f"⚠️  Only {len(found_models)}/{len(expected_models)} models found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Pydantic models: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Advanced Search Implementation")
    print("=" * 50)
    
    tests = [
        test_endpoints_structure,
        test_router_registration, 
        test_pydantic_models
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    if all(results):
        print("\n🎉 All tests passed! Advanced search implementation is complete.")
        return 0
    else:
        print(f"\n💥 {total - passed} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())