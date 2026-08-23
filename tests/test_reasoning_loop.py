import asyncio

import pytest

from mind_core import CognitiveContext
from mind_core.modules import ReasoningEngine


def test_reasoning_loop_plans_executes_and_verifies_grounded_candidate():
    engine = ReasoningEngine(max_depth=3)
    engine.activate()

    context = CognitiveContext(
        input="What is intelligence?",
        memories=["Intelligence adapts behavior toward goals."],
    )

    result = asyncio.run(engine.process(context))

    assert [step["operation"] for step in result.plan] == [
        "parse",
        "inspect_evidence",
        "synthesize",
    ]
    assert all(step["status"] == "completed" for step in result.plan)
    assert result.metadata["verification"]["approved"] is True
    assert result.metadata["verification"]["issues"] == []
    assert result.answer == (
        "Grounded context for 'What is intelligence?': "
        "Intelligence adapts behavior toward goals."
    )
    assert result.uncertainty == pytest.approx(0.35)
    assert [step.operation for step in engine.get_reasoning_trace()] == [
        "parse",
        "inspect_evidence",
        "synthesize",
    ]


def test_reasoning_loop_rejects_ungrounded_candidate():
    engine = ReasoningEngine(max_depth=3)
    engine.activate()

    result = asyncio.run(
        engine.process(CognitiveContext(input="What is intelligence?"))
    )

    verification = result.metadata["verification"]
    assert verification["approved"] is False
    assert "no_grounded_evidence" in verification["issues"]
    assert result.answer == (
        "Insufficient grounded evidence to answer: What is intelligence?"
    )
    assert result.uncertainty == pytest.approx(0.8)
