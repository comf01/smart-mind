"""
Reasoning Engine - Planned execution with explicit verification.
"""

import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..core.context import CognitiveContext


@dataclass
class ReasoningStep:
    """Represents one executed operation in the reasoning loop."""

    step_number: int
    operation: str
    input_data: Any
    output_data: Any
    confidence: float


@dataclass
class PlanStep:
    """Represents one planned operation and its execution state."""

    step_number: int
    operation: str
    status: str = "pending"
    output: Any = None


@dataclass
class VerificationResult:
    """Result of verifying a candidate answer before adoption."""

    approved: bool
    confidence: float
    issues: List[str]


class Planner:
    """Create the smallest explicit plan needed for one reasoning cycle."""

    OPERATIONS = ("parse", "inspect_evidence", "synthesize")

    def build(self, query: str, max_depth: int) -> List[PlanStep]:
        depth = max(1, min(max_depth, len(self.OPERATIONS)))
        return [
            PlanStep(step_number=index, operation=operation)
            for index, operation in enumerate(self.OPERATIONS[:depth], start=1)
        ]


class Executor:
    """Execute a plan deterministically against the shared cognitive context."""

    def execute(
        self,
        context: CognitiveContext,
        query: str,
        plan: List[PlanStep],
    ) -> Tuple[Optional[str], float, Dict[str, Any], List[ReasoningStep]]:
        parsed: Optional[Dict[str, Any]] = None
        evidence: Dict[str, Any] = {"grounded_items": 0}
        candidate: Optional[str] = None
        confidence = 0.0
        trace: List[ReasoningStep] = []

        for step in plan:
            input_data: Any

            if step.operation == "parse":
                input_data = query
                output = {
                    "type": "question",
                    "content": query,
                    "complexity": self._assess_complexity(query),
                }
                parsed = output
                step_confidence = 0.95

            elif step.operation == "inspect_evidence":
                input_data = parsed or {"content": query}
                grounded = list(context.memories) + list(context.tool_results)
                output = {
                    "observations": len(context.observations),
                    "memories": len(context.memories),
                    "tool_results": len(context.tool_results),
                    "grounded_items": len(grounded),
                    "latest_grounded_item": grounded[-1] if grounded else None,
                }
                evidence = output
                step_confidence = 0.9

            elif step.operation == "synthesize":
                input_data = evidence
                source = evidence.get("latest_grounded_item")
                if evidence.get("grounded_items", 0) > 0:
                    candidate = f"Grounded context for '{query}': {source}"
                    confidence = 0.65
                else:
                    candidate = f"Insufficient grounded evidence to answer: {query}"
                    confidence = 0.2
                output = candidate
                step_confidence = confidence

            else:
                input_data = None
                output = None
                step_confidence = 0.0

            step.status = "completed"
            step.output = output
            trace.append(
                ReasoningStep(
                    step_number=step.step_number,
                    operation=step.operation,
                    input_data=input_data,
                    output_data=output,
                    confidence=step_confidence,
                )
            )

        return candidate, confidence, evidence, trace

    def _assess_complexity(self, query: str) -> str:
        word_count = len(query.split())
        if word_count < 5:
            return "simple"
        if word_count < 15:
            return "moderate"
        return "complex"


class Verifier:
    """Reject ungrounded or incomplete candidates before they become answers."""

    REQUIRED_OPERATIONS = {"parse", "inspect_evidence", "synthesize"}

    def verify(
        self,
        plan: List[PlanStep],
        candidate: Optional[str],
        confidence: float,
        evidence: Dict[str, Any],
    ) -> VerificationResult:
        issues: List[str] = []

        completed = {
            step.operation
            for step in plan
            if step.status == "completed"
        }
        missing = self.REQUIRED_OPERATIONS - completed
        if missing:
            issues.append("incomplete_plan")

        if not candidate:
            issues.append("missing_candidate")

        if evidence.get("grounded_items", 0) < 1:
            issues.append("no_grounded_evidence")

        approved = not issues
        verified_confidence = confidence if approved else min(confidence, 0.2)

        return VerificationResult(
            approved=approved,
            confidence=max(0.0, min(1.0, verified_confidence)),
            issues=issues,
        )


class ReasoningEngine:
    """Coordinate planning, execution, and verification for one thought cycle."""

    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.logger = logging.getLogger("ReasoningEngine")

        self._active = False
        self._reasoning_chains: List[List[ReasoningStep]] = []
        self._current_chain: List[ReasoningStep] = []

        self.planner = Planner()
        self.executor = Executor()
        self.verifier = Verifier()

        self.logger.info(
            f"Reasoning engine initialized (max_depth={max_depth})"
        )

    def activate(self) -> None:
        self._active = True
        self.logger.info("Reasoning engine activated")

    def deactivate(self) -> None:
        self._active = False
        self._current_chain = []
        self.logger.info("Reasoning engine deactivated")

    async def process(self, context: CognitiveContext) -> CognitiveContext:
        """Plan, execute, and verify before adopting a candidate answer."""
        if not self._active:
            return context

        query = self._extract_query(context.current)
        self.logger.debug(f"Reasoning about: {query[:50]}...")

        plan = self.planner.build(query, self.max_depth)
        context.add_trace(
            "Planner",
            "planned",
            {"operations": [step.operation for step in plan]},
        )

        candidate, confidence, evidence, trace = self.executor.execute(
            context,
            query,
            plan,
        )
        self._current_chain = trace
        self._reasoning_chains.append(trace.copy())
        context.plan = [asdict(step) for step in plan]
        context.add_trace(
            "Executor",
            "executed",
            {
                "completed_steps": len(trace),
                "candidate_created": candidate is not None,
            },
        )

        verification = self.verifier.verify(
            plan,
            candidate,
            confidence,
            evidence,
        )
        context.add_trace(
            "Verifier",
            "verified",
            {
                "approved": verification.approved,
                "issues": list(verification.issues),
                "confidence": verification.confidence,
            },
        )

        if verification.approved:
            response = candidate or "No verified answer available."
        else:
            response = candidate or "Reasoning plan incomplete; no verified answer available."

        context.hypotheses.append(
            {
                "candidate": candidate,
                "evidence": evidence,
                "verified": verification.approved,
                "issues": list(verification.issues),
                "confidence": verification.confidence,
            }
        )
        context.answer = response
        context.current = response
        context.uncertainty = 1.0 - verification.confidence
        context.metadata["verification"] = {
            "approved": verification.approved,
            "issues": list(verification.issues),
            "confidence": verification.confidence,
        }
        context.add_trace(
            self.__class__.__name__,
            "completed",
            {
                "approved": verification.approved,
                "plan_steps": len(plan),
            },
        )

        return context

    def _extract_query(self, data: Any) -> str:
        if isinstance(data, dict):
            content = data.get("content")
            if isinstance(content, str):
                return content
        return str(data)

    def get_reasoning_trace(self) -> List[ReasoningStep]:
        return self._current_chain.copy()

    def clear_history(self) -> None:
        self._reasoning_chains = []
        self._current_chain = []
        self.logger.debug("Reasoning history cleared")

    def __repr__(self) -> str:
        return (
            f"ReasoningEngine(active={self._active}, "
            f"depth={len(self._current_chain)})"
        )
