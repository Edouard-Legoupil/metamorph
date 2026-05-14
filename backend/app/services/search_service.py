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
from datetime import datetime
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
        self.metadata = {}  # Store metadata for each document
    
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a document to the BM25 index with optional metadata."""
        terms = self._tokenize(text)
        self.doc_len[doc_id] = len(terms)
        self.corpus_size += 1
        
        # Store metadata if provided
        if metadata:
            self.metadata[doc_id] = metadata
        
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
    
    def filter_by_metadata(self, metadata_filters: Dict[str, Any]) -> List[str]:
        """Filter documents by metadata criteria."""
        if not metadata_filters or not self.metadata:
            return list(self.doc_len.keys())
        
        filtered_docs = []
        
        for doc_id, doc_metadata in self.metadata.items():
            match = True
            
            for key, value in metadata_filters.items():
                if key not in doc_metadata:
                    match = False
                    break
                    
                if isinstance(value, dict):
                    # Handle range queries (e.g., {"created_at": {"gte": "2023-01-01"}})
                    if "gte" in value and doc_metadata[key] < value["gte"]:
                        match = False
                        break
                    if "lte" in value and doc_metadata[key] > value["lte"]:
                        match = False
                        break
                    if "in" in value and doc_metadata[key] not in value["in"]:
                        match = False
                        break
                elif doc_metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered_docs.append(doc_id)
        
        return filtered_docs
    
    def rerank_by_metadata(self, doc_scores: Dict[str, float], metadata_weights: Dict[str, float]) -> Dict[str, float]:
        """Rerank documents based on metadata weights."""
        if not metadata_weights or not self.metadata:
            return doc_scores
        
        reranked_scores = {}
        
        for doc_id, score in doc_scores.items():
            if doc_id not in self.metadata:
                reranked_scores[doc_id] = score
                continue
            
            metadata_boost = 1.0
            doc_metadata = self.metadata[doc_id]
            
            # Apply metadata-based boosts
            for metadata_key, weight in metadata_weights.items():
                if metadata_key in doc_metadata:
                    metadata_value = doc_metadata[metadata_key]
                    
                    # Different boost strategies based on metadata type
                    if metadata_key == "confidence_score":
                        # Higher confidence = higher boost (0-2x range)
                        metadata_boost += weight * (metadata_value or 0) * 2
                    elif metadata_key == "created_at":
                        # More recent = higher boost (decay over time)
                        if isinstance(metadata_value, datetime):
                            days_old = (datetime.now() - metadata_value).days
                            recency_boost = max(0, 1 - (days_old / 365))  # 1x boost for recent, 0 for >1 year old
                            metadata_boost += weight * recency_boost
                    elif metadata_key == "status":
                        # Approved cards get higher boost
                        if metadata_value == "approved":
                            metadata_boost += weight * 1.5
                        elif metadata_value == "draft":
                            metadata_boost += weight * 0.5
                    elif metadata_key == "card_type":
                        # Different card types can have different base weights
                        card_type_weights = {
                            "KC-1": 1.2,  # Donor Intelligence
                            "KC-2": 1.1,  # Field Context
                            "KC-3": 1.3,  # Outcome Evidence
                            "KC-4": 1.0,  # Partner Capacity
                            "KC-5": 1.4,  # Track Record
                            "KC-6": 1.2   # Crisis Political Economy
                        }
                        metadata_boost += weight * card_type_weights.get(metadata_value, 1.0)
                    elif metadata_key == "tags":
                        # More tags = slightly higher boost
                        if isinstance(metadata_value, list):
                            metadata_boost += weight * min(0.2, len(metadata_value) * 0.05)
            
            reranked_scores[doc_id] = score * metadata_boost
        
        return reranked_scores


class SearchService:
    """Advanced search service combining BM25 and semantic search."""
    
    def __init__(self):
        self.bm25 = BM25()
        self._initialize_search_index()
    
    def _initialize_search_index(self):
        """Initialize the search index with data from the database including metadata."""
        try:
            db = next(get_db())
            
            # Index knowledge cards with metadata
            knowledge_cards = db.query(KnowledgeCard).all()
            for card in knowledge_cards:
                search_text = f"{card.title} {card.card_type} {card.domain}"
                
                # Extract comprehensive metadata
                card_metadata = {
                    'card_type': card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type),
                    'domain': card.domain,
                    'status': card.status.value if hasattr(card.status, 'value') else str(card.status),
                    'created_at': card.created_at,
                    'updated_at': card.updated_at,
                    'created_by': card.created_by,
                    'confidence_score': card.confidence_score,
                    'tags': card.tags,
                    'version': card.version,
                    'validity_start': card.validity_start,
                    'validity_end': card.validity_end,
                    'source_count': len(card.source_websites or []) + len(card.source_documents or [])
                }
                
                self.bm25.add_document(f"card_{card.id}", search_text, card_metadata)
                
                # Index wiki blocks for this card with metadata
                blocks = db.query(WikiBlock).filter(WikiBlock.card_id == card.id).all()
                for block in blocks:
                    block_text = f"{block.section_name} {block.content}"
                    
                    block_metadata = {
                        'card_id': block.card_id,
                        'section_name': block.section_name,
                        'block_type': block.block_type.value if hasattr(block.block_type, 'value') else str(block.block_type),
                        'verification_state': block.verification_state.value if hasattr(block.verification_state, 'value') else str(block.verification_state),
                        'confidence_score': block.confidence_score,
                        'created_at': block.created_at,
                        'created_by': block.created_by,
                        'is_live': block.is_live,
                        'word_count': len(block.content.split()),
                        'maintenance_tags': block.maintenance_tags
                    }
                    
                    self.bm25.add_document(f"block_{block.id}", block_text, block_metadata)
            
            # Index websites with metadata
            websites = db.query(Website).all()
            for website in websites:
                website_text = f"{website.url} {website.title} {website.description}"
                
                website_metadata = {
                    'url': website.url,
                    'domain': website.domain,
                    'status': website.status.value if hasattr(website.status, 'value') else str(website.status),
                    'created_at': website.created_at,
                    'updated_at': website.updated_at,
                    'last_scraped_at': website.last_scraped_at,
                    'total_files_discovered': website.total_files_discovered,
                    'total_files_ingested': website.total_files_ingested,
                    'scrape_frequency': website.scrape_frequency
                }
                
                self.bm25.add_document(f"website_{website.id}", website_text, website_metadata)
                
        except Exception as e:
            print(f"Error initializing search index: {e}")
    
    def bm25_search(self, query: str, limit: int = 10, metadata_filters: Optional[Dict[str, Any]] = None, metadata_weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Perform BM25 search on indexed content with optional metadata filtering and reranking."""
        scores = self.bm25.calculate_scores(query)
        
        # Apply metadata filtering if provided
        if metadata_filters:
            filtered_docs = self.bm25.filter_by_metadata(metadata_filters)
            scores = {doc_id: score for doc_id, score in scores.items() if doc_id in filtered_docs}
        
        # Apply metadata reranking if provided
        if metadata_weights:
            scores = self.bm25.rerank_by_metadata(scores, metadata_weights)
        
        # Sort by score descending
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top results
        top_results = sorted_results[:limit]
        
        # Format results with metadata
        results = []
        for doc_id, score in top_results:
            doc_type, doc_id_only = doc_id.split('_', 1)
            result = {
                'id': doc_id,
                'type': doc_type,
                'score': score,
                'document_id': doc_id_only
            }
            
            # Include metadata if available
            if doc_id in self.bm25.metadata:
                result['metadata'] = self.bm25.metadata[doc_id]
            
            results.append(result)
        
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
                       search_type: str = "hybrid", limit: int = 10,
                       metadata_filters: Optional[Dict[str, Any]] = None,
                       metadata_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Perform advanced search with configurable search type and optional metadata filtering/reranking."""
        results = []
        
        if search_type == "bm25" or search_type == "hybrid":
            bm25_results = self.bm25_search(
                query, 
                limit if search_type == "bm25" else limit * 2,
                metadata_filters=metadata_filters,
                metadata_weights=metadata_weights if search_type == "bm25" else None
            )
            results.extend(bm25_results)
        
        if search_type == "semantic" or search_type == "hybrid":
            if query_embedding:
                semantic_results = self.semantic_search(query_embedding, limit if search_type == "semantic" else limit * 2)
                results = semantic_results if search_type == "semantic" else results
        
        # If hybrid and we have both types of results, perform hybrid ranking
        if search_type == "hybrid" and query_embedding:
            # For hybrid search, apply metadata filtering to the combined results
            if metadata_filters:
                filtered_doc_ids = self.bm25.filter_by_metadata(metadata_filters)
                results = [r for r in results if r['id'] in filtered_doc_ids]
            
            # Apply metadata reranking to hybrid results
            if metadata_weights:
                # Extract scores and apply metadata boosts
                doc_scores = {r['id']: r.get('score', 0) for r in results}
                boosted_scores = self.bm25.rerank_by_metadata(doc_scores, metadata_weights)
                
                # Update results with boosted scores
                for result in results:
                    result['score'] = boosted_scores[result['id']]
                
                # Re-sort by boosted scores
                results.sort(key=lambda x: x['score'], reverse=True)
                results = results[:limit]
            else:
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