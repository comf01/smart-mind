"""Reasoning scaffold operating on the shared cognitive context."""

import logging
from typing import Any, Dict, List
from dataclasses import dataclass

from ..core.context import CognitiveContext


@dataclass
class ReasoningStep:
    step_number: int
    operation: str
    input_data: Any
    output_data: Any
    confidence: float


class ReasoningEngine:
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.logger = logging.getLogger("ReasoningEngine")
        self._active = False
        self._reasoning_chains: List[List[ReasoningStep]] = []
        self._current_chain: List[ReasoningStep] = []

    def activate(self) -> None:
        self._active = True

    def deactivate(self) -> None:
        self._active = False
        self._current_chain = []

    async def process(self, context: CognitiveContext) -> CognitiveContext:
        if not self._active:
            return context

        query = self._extract_query(context.current)
        self._current_chain = []

        parsed = self._parse_query(query)
        self._add_step("parse", query, parsed, 0.9)
        knowledge = self._identify_knowledge(parsed)
        self._add_step("identify_knowledge", parsed, knowledge, 0.85)
        reasoned = self._apply_reasoning(knowledge)
        self._add_step("reason", knowledge, reasoned, 0.8)
        response = self._formulate_response(reasoned)
        self._add_step("formulate", reasoned, response, 0.9)

        self._reasoning_chains.append(self._current_chain.copy())
        context.hypotheses.append(reasoned)
        context.answer = response
        context.current = response
        confidence = float(reasoned.get("confidence", 0.0))
        context.uncertainty = max(0.0, min(1.0, 1.0 - confidence))
        context.add_trace(
            self.__class__.__name__,
            "reasoned",
            {"steps": len(self._current_chain), "confidence": confidence},
        )
        return context

    def _extract_query(self, data: Any) -> str:
        if isinstance(data, dict):
            content = data.get("content")
            if isinstance(content, str):
                return content
        return str(data)

    def _parse_query(self, query: str) -> Dict[str, Any]:
        return {
            "type": "question",
            "content": query,
            "complexity": self._assess_complexity(query),
        }

    def _identify_knowledge(self, parsed: Dict) -> Dict[str, Any]:
        return {"domain": "general", "concepts": ["reasoning", "logic"], "relations": []}

    def _apply_reasoning(self, knowledge: Dict) -> Dict[str, Any]:
        return {
            "conclusions": ["Reasoned conclusion based on analysis"],
            "confidence": 0.8,
            "method": "deductive",
        }

    def _formulate_response(self, reasoned: Dict) -> str:
        conclusions = reasoned.get("conclusions", [])
        return conclusions[0] if conclusions else "Analysis complete."

    def _assess_complexity(self, query: str) -> str:
        word_count = len(query.split())
        if word_count < 5:
            return "simple"
        if word_count < 15:
            return "moderate"
        return "complex"

    def _add_step(
        self,
        operation: str,
        input_data: Any,
        output_data: Any,
        confidence: float,
    ) -> None:
        self._current_chain.append(
            ReasoningStep(
                step_number=len(self._current_chain) + 1,
                operation=operation,
                input_data=input_data,
                output_data=output_data,
                confidence=confidence,
            )
        )

    def get_reasoning_trace(self) -> List[ReasoningStep]:
        return self._current_chain.copy()

    def clear_history(self) -> None:
        self._reasoning_chains = []
        self._current_chain = []

    def __repr__(self) -> str:
        return f"ReasoningEngine(active={self._active}, depth={len(self._current_chain)})"
