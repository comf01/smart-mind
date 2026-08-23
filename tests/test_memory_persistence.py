import asyncio

from mind_core import MindCore
from mind_core.memory.long_term import LongTermMemory
from mind_core.modules import ReasoningEngine


def test_long_term_memory_survives_reinstantiation(tmp_path):
    database_path = tmp_path / "memory.sqlite3"

    first = LongTermMemory(storage_path=str(database_path))
    assert first.is_persistent is True
    assert first.store(
        "capital_france",
        {"fact": "Paris is the capital of France."},
        category="geography",
    )

    second = LongTermMemory(storage_path=str(database_path))

    assert len(second) == 1
    assert second.retrieve("capital_france") == {
        "fact": "Paris is the capital of France."
    }
    assert second.get_categories() == ["geography"]


def test_mind_core_reuses_persisted_memory_after_restart(tmp_path):
    database_path = tmp_path / "mind.sqlite3"
    config = {
        "MEMORY_LIMIT": 100,
        "PERSISTENCE_PATH": str(database_path),
    }

    first = MindCore(name="PersistentMind", config=config)
    assert first.long_term_memory.store(
        "capital_france",
        "Paris is the capital of France.",
        category="geography",
    )

    restarted = MindCore(name="PersistentMind", config=config)
    restarted.register_module("reasoning", ReasoningEngine(max_depth=3))
    assert restarted.activate("reasoning")

    thought = asyncio.run(restarted.think("What is the capital of France?"))

    assert restarted.long_term_memory.is_persistent is True
    assert thought.context is not None
    assert thought.context.metadata["memory_retrieval"]["keys"] == [
        "capital_france"
    ]
    assert thought.context.metadata["verification"]["approved"] is True
    assert "Paris is the capital of France." in thought.content


def test_persistent_delete_survives_restart(tmp_path):
    database_path = tmp_path / "memory.sqlite3"

    first = LongTermMemory(storage_path=str(database_path))
    assert first.store("temporary", "remove me")
    assert first.delete("temporary")

    restarted = LongTermMemory(storage_path=str(database_path))
    assert restarted.retrieve("temporary") is None
    assert len(restarted) == 0
