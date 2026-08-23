"""Shared cognitive contract for the Mind Core processing pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class CognitiveContext:
    """State passed between every cognitive module during one thought cycle."""

    input: Any
    current: Any = None
    observations: List[Dict[str, Any]] = field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    memories: List[Any] = field(default_factory=list)
    plan: List[Any] = field(default_factory=list)
    tool_results: List[Any] = field(default_factory=list)
    uncertainty: float = 1.0
    answer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.current is None:
            self.current = self.input
        self.uncertainty = max(0.0, min(1.0, float(self.uncertainty)))

    def add_trace(
        self,
        module: str,
        event: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append an auditable event without replacing the shared context."""
        self.trace.append(
            {
                "module": module,
                "event": event,
                "details": details or {},
                "timestamp": datetime.now().isoformat(),
            }
        )

    def snapshot(self) -> Dict[str, Any]:
        """Return a shallow serializable-friendly view of the current state."""
        return {
            "input": self.input,
            "current": self.current,
            "observations": list(self.observations),
            "hypotheses": list(self.hypotheses),
            "memories": list(self.memories),
            "plan": list(self.plan),
            "tool_results": list(self.tool_results),
            "uncertainty": self.uncertainty,
            "answer": self.answer,
            "metadata": dict(self.metadata),
            "trace": list(self.trace),
        }


@runtime_checkable
class CognitiveModule(Protocol):
    """Minimal contract required for modules participating in the pipeline."""

    async def process(self, context: CognitiveContext) -> CognitiveContext:
        """Read and enrich the shared context, then return that same contract."""
        ...
