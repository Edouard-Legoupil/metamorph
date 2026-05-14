"""
Search Service implementing BM25 ranking and hybrid search capabilities.

This service provides advanced search functionality including:
- BM25 ranking for keyword-based search
- Semantic search using vector embeddings
- Hybrid search combining BM25 and semantic scores
- Search across knowledge cards, wiki blocks, and documents
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import re
from app.database import get_db
from app.models.sql.knowledge_card import KnowledgeCard, WikiBlock
from app.models.sql.website import Website
from app.services.vector_store import vector_store_service


class BM25:
    """BM25 ranking algorithm implementation."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len = {}
        self.avg_doc_len = 0
        self.doc_freq = defaultdict(int)
        self.term_freq = defaultdict(lambda: defaultdict(int))
        self.idf = {}
        self.corpus_size = 0
    
    def add_document(self, doc_id: str, text: str):
        """Add a document to the BM25 index."""
        terms = self._tokenize(text)
        self.doc_len[doc_id] = len(terms)
        self.corpus_size += 1
        
        # Update document frequency and term frequency
        for term in set(terms):  # Use set to count unique terms
            self.doc_freq[term] += 1
            self.term_freq[term][doc_id] += 1
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Basic tokenization: lowercase, remove punctuation, split on whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()
    
    def _calculate_avg_doc_len(self):
        """Calculate average document length."""
        if not self.doc_len:
            return 0
        self.avg_doc_len = sum(self.doc_len.values()) / len(self.doc_len)
    
    def _calculate_idf(self):
        """Calculate inverse document frequency for all terms."""
        if not self.doc_freq:
            return
        for term, freq in self.doc_freq.items():
            self.idf[term] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
    
    def calculate_scores(self, query: str) -> Dict[str, float]:
        """Calculate BM25 scores for a query."""
        if not self.doc_len:
            return {}
        
        # Calculate average document length and IDF if not already done
        if self.avg_doc_len == 0:
            self._calculate_avg_doc_len()
        if not self.idf:
            self._calculate_idf()
        
        query_terms = self._tokenize(query)
        scores = defaultdict(float)
        
        for term in query_terms:
            if term not in self.term_freq:
                continue
            
            # Term frequency in query
            qf = query_terms.count(term)
            
            for doc_id, tf in self.term_freq[term].items():
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (self.doc_len[doc_id] / self.avg_doc_len))
                term_score = (numerator / denominator) * self.idf[term]
                scores[doc_id] += term_score
        
        return scores


class SearchService:
    """Advanced search service combining BM25 and semantic search."""
    
    def __init__(self):
        self.bm25 = BM25()
        self._initialize_search_index()
    
    def _initialize_search_index(self):
        """Initialize the search index with data from the database."""
        try:
            db = next(get_db())
            
            # Index knowledge cards
            knowledge_cards = db.query(KnowledgeCard).all()
            for card in knowledge_cards:
                search_text = f"{card.title} {card.card_type} {card.domain}"
                self.bm25.add_document(f"card_{card.id}", search_text)
                
                # Index wiki blocks for this card
                blocks = db.query(WikiBlock).filter(WikiBlock.card_id == card.id).all()
                for block in blocks:
                    block_text = f"{block.section_name} {block.content}"
                    self.bm25.add_document(f"block_{block.id}", block_text)
            
            # Index websites
            websites = db.query(Website).all()
            for website in websites:
                website_text = f"{website.url} {website.title} {website.description}"
                self.bm25.add_document(f"website_{website.id}", website_text)
                
        except Exception as e:
            print(f"Error initializing search index: {e}")
    
    def bm25_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform BM25 search on indexed content."""
        scores = self.bm25.calculate_scores(query)
        
        # Sort by score descending
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top results
        top_results = sorted_results[:limit]
        
        # Format results
        results = []
        for doc_id, score in top_results:
            doc_type, doc_id_only = doc_id.split('_', 1)
            results.append({
                'id': doc_id,
                'type': doc_type,
                'score': score,
                'document_id': doc_id_only
            })
        
        return results
    
    def semantic_search(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using vector embeddings."""
        try:
            # Use the existing vector store service for semantic search
            results = vector_store_service.semantic_search_knowledge_cards(
                query_embedding=query_embedding,
                limit=limit,
                min_score=0.1
            )
            return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def hybrid_search(self, query: str, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Perform hybrid search combining BM25 and semantic search."""
        # Get BM25 results
        bm25_results = self.bm25_search(query, limit * 2)  # Get more BM25 results for hybrid ranking
        
        # Get semantic results
        semantic_results = self.semantic_search(query_embedding, limit * 2)
        
        # Combine and re-rank results
        combined_results = []
        
        # Create a mapping of document IDs to their scores
        score_map = {}
        
        # Add BM25 results
        for result in bm25_results:
            doc_id = result['id']
            score_map[doc_id] = {
                'bm25_score': result['score'],
                'semantic_score': 0,
                'data': result
            }
        
        # Add semantic results
        for result in semantic_results:
            doc_id = result.get('id', result.get('document_id', ''))
            if doc_id:
                if doc_id not in score_map:
                    score_map[doc_id] = {
                        'bm25_score': 0,
                        'semantic_score': result.get('score', 0),
                        'data': result
                    }
                else:
                    score_map[doc_id]['semantic_score'] = result.get('score', 0)
        
        # Calculate combined scores and sort
        for doc_id, scores in score_map.items():
            # Simple weighted combination (can be adjusted)
            combined_score = scores['bm25_score'] * 0.4 + scores['semantic_score'] * 0.6
            combined_results.append({
                'id': doc_id,
                'combined_score': combined_score,
                'bm25_score': scores['bm25_score'],
                'semantic_score': scores['semantic_score'],
                'data': scores['data']
            })
        
        # Sort by combined score descending
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_results[:limit]
    
    def advanced_search(self, query: str, query_embedding: Optional[List[float]] = None, 
                       search_type: str = "hybrid", limit: int = 10) -> Dict[str, Any]:
        """Perform advanced search with configurable search type."""
        results = []
        
        if search_type == "bm25" or search_type == "hybrid":
            bm25_results = self.bm25_search(query, limit if search_type == "bm25" else limit * 2)
            results.extend(bm25_results)
        
        if search_type == "semantic" or search_type == "hybrid":
            if query_embedding:
                semantic_results = self.semantic_search(query_embedding, limit if search_type == "semantic" else limit * 2)
                results = semantic_results if search_type == "semantic" else results
        
        # If hybrid and we have both types of results, perform hybrid ranking
        if search_type == "hybrid" and query_embedding:
            results = self.hybrid_search(query, query_embedding, limit)
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "search_type": search_type,
            "message": f"Found {len(results)} results using {search_type} search"
        }


# Initialize the search service
search_service = SearchService()