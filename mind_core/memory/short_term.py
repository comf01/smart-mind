"""
Short-Term Memory - Working memory for immediate cognitive processing.

This module implements a limited-capacity, fast-access memory system
for holding information currently being processed.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import deque


class ShortTermMemory:
    """
    Implements working memory with limited capacity.
    
    Features:
    - FIFO eviction policy
    - Priority-based retention
    - Fast access and retrieval
    - Capacity management
    """
    
    def __init__(self, limit: int = 1000):
        """
        Initialize short-term memory.
        
        Args:
            limit: Maximum number of items to store
        """
        self.limit = limit
        self.logger = logging.getLogger("ShortTermMemory")
        
        self._memory: deque = deque(maxlen=limit)
        self._priority_items: Dict[str, Any] = {}
        self._access_count = 0
        
        self.logger.info(f"Short-term memory initialized (limit={limit})")
    
    def add(self, item: Any, role: str = "general", priority: bool = False) -> None:
        """
        Add an item to short-term memory.
        
        Args:
            item: Item to store
            role: Role or context of the item
            priority: If True, store in priority section
        """
        memory_entry = {
            "content": item,
            "role": role,
            "timestamp": datetime.now(),
            "access_count": 0,
        }
        
        if priority:
            key = f"priority_{len(self._priority_items)}"
            self._priority_items[key] = memory_entry
            self.logger.debug(f"Priority item stored: {key}")
        else:
            self._memory.append(memory_entry)
            self.logger.debug(f"Item stored (role={role})")
            
            # Check capacity
            if len(self._memory) >= self.limit:
                self.logger.warning("Short-term memory at capacity")
    
    def get(self, index: int = -1) -> Optional[Any]:
        """
        Retrieve an item from memory.
        
        Args:
            index: Index of item (-1 for most recent)
            
        Returns:
            Retrieved item or None
        """
        if not self._memory:
            return None
        
        try:
            entry = self._memory[index]
            entry["access_count"] += 1
            self._access_count += 1
            return entry["content"]
        except IndexError:
            return None
    
    def search(self, role: str) -> List[Any]:
        """
        Search for items by role.
        
        Args:
            role: Role to search for
            
        Returns:
            List of matching items
        """
        results = [
            entry["content"] 
            for entry in self._memory 
            if entry.get("role") == role
        ]
        self.logger.debug(f"Search found {len(results)} items with role '{role}'")
        return results
    
    def clear(self) -> None:
        """Clear all non-priority items from memory."""
        self._memory.clear()
        self.logger.info("Short-term memory cleared")
    
    def clear_priority(self) -> None:
        """Clear priority items."""
        self._priority_items.clear()
        self.logger.info("Priority memory cleared")
    
    def consolidate_to_long_term(self) -> List[Dict]:
        """
        Identify items for consolidation to long-term memory.
        
        Returns:
            List of items ready for consolidation
        """
        # Items accessed multiple times are candidates
        candidates = [
            entry for entry in self._memory 
            if entry.get("access_count", 0) > 2
        ]
        
        self.logger.debug(f"Found {len(candidates)} items for consolidation")
        return candidates
    
    def __len__(self) -> int:
        """Return total items in memory."""
        return len(self._memory) + len(self._priority_items)
    
    def get_status(self) -> Dict[str, Any]:
        """Get memory status."""
        return {
            "current_size": len(self._memory),
            "priority_size": len(self._priority_items),
            "capacity": self.limit,
            "utilization": len(self._memory) / self.limit,
            "total_accesses": self._access_count,
        }
    
    def __repr__(self) -> str:
        return f"ShortTermMemory(size={len(self._memory)}/{self.limit})"
