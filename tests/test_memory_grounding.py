import asyncio

import pytest

from mind_core import MindCore
from mind_core.modules import PerceptionModule, ReasoningEngine


def _build_mind() -> MindCore:
    mind = MindCore(name="MemoryGrounding", config={"MEMORY_LIMIT": 100})
    mind.initialize()
    mind.register_module("perception", PerceptionModule())
    mind.register_module("reasoning", ReasoningEngine(max_depth=3))
    assert mind.activate("perception")
    assert mind.activate("reasoning")
    return mind


def test_relevant_long_term_memory_grounds_reasoning():
    mind = _build_mind()
    mind.long_term_memory.store(
        "france-capital",
        "Paris is the capital of France.",
        category="facts",
    )

    thought = asyncio.run(mind.think("What is the capital of France?"))

    assert len(thought.context.memories) == 1
    assert thought.context.memories[0]["key"] == "france-capital"
    assert thought.context.memories[0]["match_score"] == pytest.approx(1.0)
    assert thought.context.metadata["memory_retrieval"]["count"] == 1
    assert thought.context.metadata["verification"]["approved"] is True
    assert thought.confidence == pytest.approx(0.65)
    assert "Paris is the capital of France." in thought.content


def test_partial_but_wrong_memory_does_not_ground_reasoning():
    mind = _build_mind()
    mind.long_term_memory.store(
        "germany-capital",
        "Berlin is the capital of Germany.",
        category="facts",
    )

    thought = asyncio.run(mind.think("What is the capital of France?"))

    assert thought.context.memories == []
    assert thought.context.metadata["memory_retrieval"]["count"] == 0
    assert thought.context.metadata["verification"]["approved"] is False
    assert "no_grounded_evidence" in thought.context.metadata["verification"]["issues"]
    assert thought.confidence == pytest.approx(0.2)
