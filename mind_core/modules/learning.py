"""Experience recorder operating on the shared cognitive context."""

import logging
from typing import Any, Dict, List
from datetime import datetime

from ..core.context import CognitiveContext


class LearningModule:
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.logger = logging.getLogger("LearningModule")
        self._active = False
        self._experiences: List[Dict] = []
        self._patterns: Dict[str, Any] = {}
        self._performance_history: List[float] = []
        self._total_learnings = 0
        self._adaptation_count = 0

    def activate(self) -> None:
        self._active = True

    def deactivate(self) -> None:
        self._active = False

    async def process(self, context: CognitiveContext) -> CognitiveContext:
        if not self._active:
            return context

        self._record_experience(
            {
                "input": context.input,
                "answer": context.answer,
                "uncertainty": context.uncertainty,
                "trace_length": len(context.trace),
            }
        )
        self._detect_patterns()
        context.add_trace(self.__class__.__name__, "experience_recorded")
        return context

    def learn(self, experience: Dict[str, Any], outcome: float) -> None:
        learning_record = {
            "experience": experience,
            "outcome": outcome,
            "timestamp": datetime.now(),
        }
        self._experiences.append(learning_record)
        self._performance_history.append(outcome)
        self._total_learnings += 1
        if outcome > 0.8:
            self._reinforce_patterns(experience)
        elif outcome < 0.3:
            self._adjust_patterns(experience)

    def get_performance(self) -> float:
        if not self._performance_history:
            return 0.0
        recent = self._performance_history[-10:]
        return sum(recent) / len(recent)

    def _record_experience(self, data: Any) -> None:
        self._experiences.append(
            {
                "data": data,
                "timestamp": datetime.now(),
                "context": self._extract_context(data),
            }
        )
        if len(self._experiences) > 1000:
            self._experiences = self._experiences[-500:]

    def _detect_patterns(self) -> None:
        if len(self._experiences) < 10:
            return
        pass

    def _reinforce_patterns(self, experience: Dict) -> None:
        self._adaptation_count += 1

    def _adjust_patterns(self, experience: Dict) -> None:
        self._adaptation_count += 1

    def _extract_context(self, data: Any) -> Dict[str, Any]:
        return {
            "type": type(data).__name__,
            "size": len(str(data)) if hasattr(data, "__len__") else 1,
        }

    def consolidate_knowledge(self) -> Dict[str, Any]:
        return {
            "total_experiences": len(self._experiences),
            "patterns_identified": len(self._patterns),
            "performance": self.get_performance(),
            "adaptations": self._adaptation_count,
        }

    def clear_memory(self) -> None:
        self._experiences = []
        self._patterns = {}
        self._performance_history = []

    def __repr__(self) -> str:
        return f"LearningModule(active={self._active}, learnings={self._total_learnings})"
