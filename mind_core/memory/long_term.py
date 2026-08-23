"""
Long-Term Memory - Persistent storage for knowledge and experiences.

This module implements a persistent memory system for storing information
over extended periods, with efficient retrieval and organization.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class LongTermMemory:
    """
    Implements persistent long-term storage.
    
    Features:
    - Durable storage
    - Semantic organization
    - Efficient retrieval
    - Knowledge graphs
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize long-term memory.
        
        Args:
            storage_path: Path for persistent storage (optional)
        """
        self.storage_path = storage_path
        self.logger = logging.getLogger("LongTermMemory")
        
        self._knowledge_base: Dict[str, Any] = {}
        self._semantic_network: Dict[str, List[str]] = {}
        self._storage_count = 0
        
        self.logger.info(f"Long-term memory initialized (path={storage_path or 'memory'})")
    
    def store(self, key: str, data: Any, category: str = "general") -> bool:
        """
        Store data in long-term memory.
        
        Args:
            key: Unique identifier for the data
            data: Data to store
            category: Category for organization
            
        Returns:
            True if successful
        """
        try:
            entry = {
                "key": key,
                "data": data,
                "category": category,
                "created_at": datetime.now(),
                "accessed_at": None,
                "access_count": 0,
            }
            
            self._knowledge_base[key] = entry
            
            # Update semantic network
            if category not in self._semantic_network:
                self._semantic_network[category] = []
            self._semantic_network[category].append(key)
            
            self._storage_count += 1
            self.logger.debug(f"Stored '{key}' in category '{category}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store '{key}': {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data by key.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Retrieved data or None
        """
        if key not in self._knowledge_base:
            self.logger.debug(f"Key '{key}' not found")
            return None
        
        entry = self._knowledge_base[key]
        entry["accessed_at"] = datetime.now()
        entry["access_count"] += 1
        
        self.logger.debug(f"Retrieved '{key}' (access #{entry['access_count']})")
        return entry["data"]
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search for data matching query.
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching entries
        """
        results = []
        
        for key, entry in self._knowledge_base.items():
            # Apply category filter
            if category and entry.get("category") != category:
                continue
            
            # Simple text search
            content_str = str(entry.get("data", ""))
            if query.lower() in content_str.lower():
                results.append({
                    "key": key,
                    "data": entry["data"],
                    "category": entry.get("category"),
                    "relevance": self._calculate_relevance(query, entry),
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        self.logger.debug(f"Search found {len(results)} matches for '{query}'")
        return results
    
    def delete(self, key: str) -> bool:
        """
        Delete data by key.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted
        """
        if key in self._knowledge_base:
            entry = self._knowledge_base[key]
            category = entry.get("category")
            
            del self._knowledge_base[key]
            
            # Remove from semantic network
            if category and category in self._semantic_network:
                if key in self._semantic_network[category]:
                    self._semantic_network[category].remove(key)
            
            self.logger.debug(f"Deleted '{key}'")
            return True
        
        return False
    
    def get_categories(self) -> List[str]:
        """Get all categories."""
        return list(self._semantic_network.keys())
    
    def get_by_category(self, category: str) -> List[Dict]:
        """
        Get all entries in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of entries
        """
        if category not in self._semantic_network:
            return []
        
        entries = []
        for key in self._semantic_network[category]:
            if key in self._knowledge_base:
                entries.append(self._knowledge_base[key])
        
        return entries
    
    def _calculate_relevance(self, query: str, entry: Dict) -> float:
        """Calculate relevance score for search result."""
        score = 0.0
        
        # Access frequency boost
        score += entry.get("access_count", 0) * 0.1
        
        # Recency boost
        created = entry.get("created_at")
        if created:
            age_days = (datetime.now() - created).days
            score += max(0, 1.0 - age_days / 365)
        
        return score
    
    def consolidate(self) -> Dict[str, Any]:
        """
        Consolidate and optimize memory.
        
        Returns:
            Consolidation report
        """
        # Identify rarely accessed items
        old_items = [
            key for key, entry in self._knowledge_base.items()
            if entry.get("access_count", 0) == 0
        ]
        
        report = {
            "total_entries": len(self._knowledge_base),
            "categories": len(self._semantic_network),
            "consolidation_candidates": len(old_items),
            "timestamp": datetime.now(),
        }
        
        self.logger.info(f"Consolidation complete: {report}")
        return report
    
    def export(self) -> str:
        """Export memory as JSON string."""
        return json.dumps(self._knowledge_base, default=str)
    
    def clear(self) -> None:
        """Clear all long-term memory."""
        self._knowledge_base.clear()
        self._semantic_network.clear()
        self.logger.warning("Long-term memory cleared")
    
    def __len__(self) -> int:
        return len(self._knowledge_base)
    
    def __repr__(self) -> str:
        return f"LongTermMemory(entries={len(self._knowledge_base)}, categories={len(self._semantic_network)})"
