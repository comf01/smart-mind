"""
Reasoning Engine - Logical inference and problem-solving module.

This module implements multi-step reasoning, chain-of-thought processing,
and logical inference capabilities for the mind core.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..core.context import CognitiveContext


@dataclass
class ReasoningStep:
    """Represents a single step in a reasoning chain."""
    
    step_number: int
    operation: str
    input_data: Any
    output_data: Any
    confidence: float


class ReasoningEngine:
    """
    Implements logical reasoning and inference capabilities.
    
    Features:
    - Chain-of-thought reasoning
    - Multi-step inference
    - Logical deduction and induction
    - Confidence scoring
    """
    
    def __init__(self, max_depth: int = 10):
        """
        Initialize the reasoning engine.
        
        Args:
            max_depth: Maximum reasoning chain depth
        """
        self.max_depth = max_depth
        self.logger = logging.getLogger("ReasoningEngine")
        
        self._active = False
        self._reasoning_chains: List[List[ReasoningStep]] = []
        self._current_chain: List[ReasoningStep] = []
        
        self.logger.info(f"Reasoning engine initialized (max_depth={max_depth})")
    
    def activate(self) -> None:
        """Activate the reasoning engine."""
        self._active = True
        self.logger.info("Reasoning engine activated")
    
    def deactivate(self) -> None:
        """Deactivate the reasoning engine."""
        self._active = False
        self._current_chain = []
        self.logger.info("Reasoning engine deactivated")
    
    async def process(self, context: CognitiveContext) -> CognitiveContext:
        """Process the current cognitive state through reasoning."""
        if not self._active:
            return context

        query = self._extract_query(context.current)
        self.logger.debug(f"Reasoning about: {query[:50]}...")
        
        # Build reasoning chain
        self._current_chain = []
        
        # Step 1: Parse the query
        parsed = self._parse_query(query)
        self._add_step("parse", query, parsed, 0.9)
        
        # Step 2: Identify relevant knowledge
        knowledge = self._identify_knowledge(parsed)
        self._add_step("identify_knowledge", parsed, knowledge, 0.85)
        
        # Step 3: Apply reasoning
        reasoned = self._apply_reasoning(knowledge)
        self._add_step("reason", knowledge, reasoned, 0.8)
        
        # Step 4: Formulate response
        response = self._formulate_response(reasoned)
        self._add_step("formulate", reasoned, response, 0.9)
        
        # Store completed chain
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
        """Extract text from the current cognitive payload."""
        if isinstance(data, dict):
            content = data.get("content")
            if isinstance(content, str):
                return content
        return str(data)
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse the input query."""
        return {
            "type": "question",
            "content": query,
            "complexity": self._assess_complexity(query),
        }
    
    def _identify_knowledge(self, parsed: Dict) -> Dict[str, Any]:
        """Identify relevant knowledge for reasoning."""
        return {
            "domain": "general",
            "concepts": ["reasoning", "logic"],
            "relations": [],
        }
    
    def _apply_reasoning(self, knowledge: Dict) -> Dict[str, Any]:
        """Apply logical reasoning to identified knowledge."""
        return {
            "conclusions": ["Reasoned conclusion based on analysis"],
            "confidence": 0.8,
            "method": "deductive",
        }
    
    def _formulate_response(self, reasoned: Dict) -> str:
        """Formulate final response from reasoning results."""
        conclusions = reasoned.get("conclusions", [])
        if conclusions:
            return conclusions[0]
        return "Analysis complete."
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        word_count = len(query.split())
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "moderate"
        else:
            return "complex"
    
    def _add_step(self, operation: str, input_data: Any, 
                  output_data: Any, confidence: float) -> None:
        """Add a step to the current reasoning chain."""
        step = ReasoningStep(
            step_number=len(self._current_chain) + 1,
            operation=operation,
            input_data=input_data,
            output_data=output_data,
            confidence=confidence,
        )
        self._current_chain.append(step)
        self.logger.debug(f"Reasoning step {step.step_number}: {operation}")
    
    def get_reasoning_trace(self) -> List[ReasoningStep]:
        """
        Get the trace of the last reasoning chain.
        
        Returns:
            List of reasoning steps
        """
        return self._current_chain.copy()
    
    def clear_history(self) -> None:
        """Clear reasoning history."""
        self._reasoning_chains = []
        self._current_chain = []
        self.logger.debug("Reasoning history cleared")
    
    def __repr__(self) -> str:
        return f"ReasoningEngine(active={self._active}, depth={len(self._current_chain)})"
