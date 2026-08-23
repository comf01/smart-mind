import asyncio

import pytest

from mind_core import CognitiveContext, MindCore
from mind_core.core import ConsciousnessModule
from mind_core.modules import LearningModule, PerceptionModule, ReasoningEngine


def test_pipeline_preserves_shared_cognitive_context():
    mind = MindCore(name="Test", config={"MEMORY_LIMIT": 100})
    mind.initialize()

    mind.register_module("perception", PerceptionModule())
    mind.register_module("reasoning", ReasoningEngine(max_depth=5))
    mind.register_module("learning", LearningModule())
    mind.register_module("consciousness", ConsciousnessModule(mind_name="Test"))

    for name in ("perception", "reasoning", "learning", "consciousness"):
        assert mind.activate(name)

    thought = asyncio.run(mind.think("What is intelligence?"))

    assert isinstance(thought.context, CognitiveContext)
    assert thought.context.input == "What is intelligence?"
    assert thought.context.answer == thought.content
    assert thought.context.observations
    assert thought.context.hypotheses
    assert thought.confidence == pytest.approx(0.2)
    assert thought.context.metadata["verification"]["approved"] is False
    assert "no_grounded_evidence" in thought.context.metadata["verification"]["issues"]
    assert [event["module"] for event in thought.context.trace] == [
        "LongTermMemory",
        "PerceptionModule",
        "Planner",
        "Executor",
        "Verifier",
        "ReasoningEngine",
        "LearningModule",
        "ConsciousnessModule",
    ]


def test_pipeline_rejects_module_that_breaks_contract():
    class BadModule:
        def activate(self):
            pass

        async def process(self, context):
            return "not-a-context"

    mind = MindCore(name="ContractTest", config={"MEMORY_LIMIT": 100})
    mind.register_module("bad", BadModule())
    assert mind.activate("bad")

    with pytest.raises(TypeError, match="must return CognitiveContext"):
        asyncio.run(mind.think("test"))
