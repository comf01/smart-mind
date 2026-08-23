"""
Learning Module - Adaptive learning and improvement capabilities.

This module enables the mind to learn from experiences, adapt its behavior,
and continuously improve its performance over time.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.context import CognitiveContext


class LearningModule:
    """
    Implements adaptive learning capabilities.
    
    Features:
    - Experience-based learning
    - Pattern recognition
    - Performance optimization
    - Knowledge consolidation
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """
        Initialize the learning module.
        
        Args:
            learning_rate: Rate of learning adaptation
        """
        self.learning_rate = learning_rate
        self.logger = logging.getLogger("LearningModule")
        
        self._active = False
        self._experiences: List[Dict] = []
        self._patterns: Dict[str, Any] = {}
        self._performance_history: List[float] = []
        
        # Learning metrics
        self._total_learnings = 0
        self._adaptation_count = 0
        
        self.logger.info(f"Learning module initialized (rate={learning_rate})")
    
    def activate(self) -> None:
        """Activate the learning module."""
        self._active = True
        self.logger.info("Learning module activated")
    
    def deactivate(self) -> None:
        """Deactivate the learning module."""
        self._active = False
        self.logger.info("Learning module deactivated")
    
    async def process(self, context: CognitiveContext) -> CognitiveContext:
        """Record experience while preserving the shared cognitive context."""
        if not self._active:
            return context
        
        # Learn from the current thought state
        self._record_experience({
            "input": context.input,
            "answer": context.answer,
            "uncertainty": context.uncertainty,
            "trace_length": len(context.trace),
        })
        
        # Look for patterns
        self._detect_patterns()
        context.add_trace(self.__class__.__name__, "experience_recorded")
        
        return context
    
    def learn(self, experience: Dict[str, Any], outcome: float) -> None:
        """
        Learn from an experience.
        
        Args:
            experience: Experience data
            outcome: Outcome score (0.0 to 1.0)
        """
        learning_record = {
            "experience": experience,
            "outcome": outcome,
            "timestamp": datetime.now(),
        }
        
        self._experiences.append(learning_record)
        self._performance_history.append(outcome)
        self._total_learnings += 1
        
        # Update patterns based on outcome
        if outcome > 0.8:
            self._reinforce_patterns(experience)
        elif outcome < 0.3:
            self._adjust_patterns(experience)
        
        self.logger.debug(f"Learned from experience (outcome={outcome:.2f})")
    
    def get_performance(self) -> float:
        """
        Get current performance metric.
        
        Returns:
            Average performance score
        """
        if not self._performance_history:
            return 0.0
        
        recent = self._performance_history[-10:]  # Last 10 experiences
        return sum(recent) / len(recent)
    
    def _record_experience(self, data: Any) -> None:
        """Record an experience for learning."""
        experience = {
            "data": data,
            "timestamp": datetime.now(),
            "context": self._extract_context(data),
        }
        self._experiences.append(experience)
        
        # Limit stored experiences
        if len(self._experiences) > 1000:
            self._experiences = self._experiences[-500:]
    
    def _detect_patterns(self) -> None:
        """Detect patterns in experiences."""
        if len(self._experiences) < 10:
            return
        
        # Simple pattern detection
        # In production, this would use ML algorithms
        pass
    
    def _reinforce_patterns(self, experience: Dict) -> None:
        """Reinforce successful patterns."""
        self._adaptation_count += 1
        self.logger.debug("Patterns reinforced")
    
    def _adjust_patterns(self, experience: Dict) -> None:
        """Adjust patterns based on poor outcomes."""
        self._adaptation_count += 1
        self.logger.debug("Patterns adjusted")
    
    def _extract_context(self, data: Any) -> Dict[str, Any]:
        """Extract contextual information from data."""
        return {
            "type": type(data).__name__,
            "size": len(str(data)) if hasattr(data, '__len__') else 1,
        }
    
    def consolidate_knowledge(self) -> Dict[str, Any]:
        """
        Consolidate learned knowledge.
        
        Returns:
            Consolidated knowledge summary
        """
        return {
            "total_experiences": len(self._experiences),
            "patterns_identified": len(self._patterns),
            "performance": self.get_performance(),
            "adaptations": self._adaptation_count,
        }
    
    def clear_memory(self) -> None:
        """Clear learning memory."""
        self._experiences = []
        self._patterns = {}
        self._performance_history = []
        self.logger.info("Learning memory cleared")
    
    def __repr__(self) -> str:
        return f"LearningModule(active={self._active}, learnings={self._total_learnings})"
