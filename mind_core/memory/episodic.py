"""
Episodic Memory - Memory of specific events and experiences.

This module implements memory for storing and recalling specific episodes,
events, and experiences with temporal context.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


class EpisodicMemory:
    """
    Implements episodic memory for events and experiences.
    
    Features:
    - Temporal tagging
    - Context storage
    - Event sequencing
    - Experiential recall
    """
    
    def __init__(self):
        """Initialize episodic memory."""
        self.logger = logging.getLogger("EpisodicMemory")
        
        self._episodes: List[Dict[str, Any]] = []
        self._event_index: Dict[str, List[int]] = {}
        self._timeline: List[datetime] = []
        
        self._episode_count = 0
        
        self.logger.info("Episodic memory initialized")
    
    def record_episode(self, event: str, context: Optional[Dict] = None,
                       emotional_valence: float = 0.0) -> int:
        """
        Record a new episode.
        
        Args:
            event: The event or experience
            context: Additional contextual information
            emotional_valence: Emotional tone (-1.0 to 1.0)
            
        Returns:
            Episode index
        """
        episode = {
            "id": self._episode_count,
            "event": event,
            "context": context or {},
            "timestamp": datetime.now(),
            "emotional_valence": max(-1.0, min(1.0, emotional_valence)),
            "recall_count": 0,
        }
        
        self._episodes.append(episode)
        self._timeline.append(episode["timestamp"])
        
        # Index by event type
        event_type = self._extract_event_type(event)
        if event_type not in self._event_index:
            self._event_index[event_type] = []
        self._event_index[event_type].append(self._episode_count)
        
        self._episode_count += 1
        self.logger.debug(f"Recorded episode {episode['id']}: {event[:50]}...")
        
        return episode["id"]
    
    def recall(self, episode_id: int) -> Optional[Dict]:
        """
        Recall a specific episode.
        
        Args:
            episode_id: ID of episode to recall
            
        Returns:
            Episode data or None
        """
        if episode_id < 0 or episode_id >= len(self._episodes):
            return None
        
        episode = self._episodes[episode_id]
        episode["recall_count"] += 1
        
        self.logger.debug(f"Recalled episode {episode_id}")
        return episode.copy()
    
    def search_by_time(self, start: datetime, end: datetime) -> List[Dict]:
        """
        Search episodes within a time range.
        
        Args:
            start: Start timestamp
            end: End timestamp
            
        Returns:
            List of matching episodes
        """
        results = [
            ep.copy() for ep in self._episodes
            if start <= ep["timestamp"] <= end
        ]
        
        self.logger.debug(f"Found {len(results)} episodes in time range")
        return results
    
    def search_by_emotion(self, valence_range: tuple) -> List[Dict]:
        """
        Search episodes by emotional valence.
        
        Args:
            valence_range: Tuple of (min, max) valence values
            
        Returns:
            List of matching episodes
        """
        min_val, max_val = valence_range
        results = [
            ep.copy() for ep in self._episodes
            if min_val <= ep["emotional_valence"] <= max_val
        ]
        
        self.logger.debug(f"Found {len(results)} episodes in emotion range")
        return results
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """
        Get most recent episodes.
        
        Args:
            count: Number of episodes to retrieve
            
        Returns:
            List of recent episodes
        """
        recent = self._episodes[-count:]
        return [ep.copy() for ep in reversed(recent)]
    
    def get_similar(self, episode_id: int) -> List[Dict]:
        """
        Find episodes similar to the given one.
        
        Args:
            episode_id: Reference episode ID
            
        Returns:
            List of similar episodes
        """
        if episode_id < 0 or episode_id >= len(self._episodes):
            return []
        
        reference = self._episodes[episode_id]
        event_type = self._extract_event_type(reference["event"])
        
        similar_ids = self._event_index.get(event_type, [])
        similar = [
            self._episodes[i].copy() for i in similar_ids
            if i != episode_id
        ]
        
        self.logger.debug(f"Found {len(similar)} similar episodes")
        return similar
    
    def _extract_event_type(self, event: str) -> str:
        """Extract event type from event description."""
        # Simple extraction - in production would use NLP
        words = event.lower().split()
        return words[0] if words else "unknown"
    
    def get_timeline(self) -> List[Dict]:
        """
        Get chronological timeline of episodes.
        
        Returns:
            List of episodes with timestamps
        """
        return [
            {"id": ep["id"], "timestamp": ep["timestamp"], "event": ep["event"]}
            for ep in self._episodes
        ]
    
    def consolidate(self, age_days: int = 30) -> Dict[str, Any]:
        """
        Consolidate old episodes.
        
        Args:
            age_days: Age threshold for consolidation
            
        Returns:
            Consolidation report
        """
        cutoff = datetime.now()
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=age_days)
        
        old_episodes = [
            ep for ep in self._episodes
            if ep["timestamp"] < cutoff and ep["recall_count"] == 0
        ]
        
        report = {
            "total_episodes": len(self._episodes),
            "consolidation_candidates": len(old_episodes),
            "age_threshold_days": age_days,
        }
        
        self.logger.info(f"Episodic consolidation: {report}")
        return report
    
    def clear(self) -> None:
        """Clear all episodes."""
        self._episodes.clear()
        self._event_index.clear()
        self._timeline.clear()
        self.logger.warning("Episodic memory cleared")
    
    def __len__(self) -> int:
        return len(self._episodes)
    
    def __repr__(self) -> str:
        return f"EpisodicMemory(episodes={len(self._episodes)})"
