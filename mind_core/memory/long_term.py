"""
Long-Term Memory - durable storage for knowledge and experiences.

The public API remains usable in pure in-memory mode. When ``storage_path``
is provided, entries are mirrored to SQLite and reloaded on construction so
memory survives process restarts without adding an external dependency.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class LongTermMemory:
    """Long-term memory with optional SQLite-backed durability."""

    _DATABASE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize long-term memory.

        Args:
            storage_path: Optional SQLite file path or directory. If a
                directory is provided, ``long_term_memory.sqlite3`` is used.
                If omitted, memory remains process-local.
        """
        self.storage_path = storage_path
        self.logger = logging.getLogger("LongTermMemory")

        self._knowledge_base: Dict[str, Any] = {}
        self._semantic_network: Dict[str, List[str]] = {}
        self._storage_count = 0
        self._database_path: Optional[Path] = None

        if storage_path:
            self._database_path = self._resolve_database_path(storage_path)
            self._initialize_storage()
            self._load_from_storage()

        location = str(self._database_path) if self._database_path else "memory"
        self.logger.info(f"Long-term memory initialized (path={location})")

    @property
    def is_persistent(self) -> bool:
        """Return whether this instance is backed by durable storage."""
        return self._database_path is not None

    @property
    def database_path(self) -> Optional[str]:
        """Return the resolved SQLite path when persistence is enabled."""
        return str(self._database_path) if self._database_path else None

    def store(self, key: str, data: Any, category: str = "general") -> bool:
        """Store or replace a memory entry."""
        try:
            created_at = datetime.now()
            serialized = self._serialize_data(data)

            if self._database_path:
                with self._connect() as connection:
                    connection.execute(
                        """
                        INSERT INTO memories
                            (key, data_json, category, created_at, accessed_at, access_count)
                        VALUES (?, ?, ?, ?, NULL, 0)
                        ON CONFLICT(key) DO UPDATE SET
                            data_json = excluded.data_json,
                            category = excluded.category,
                            created_at = excluded.created_at,
                            accessed_at = NULL,
                            access_count = 0
                        """,
                        (key, serialized, category, created_at.isoformat()),
                    )

            previous = self._knowledge_base.get(key)
            if previous:
                self._remove_from_semantic_index(
                    key,
                    previous.get("category", "general"),
                )

            entry = {
                "key": key,
                "data": data,
                "category": category,
                "created_at": created_at,
                "accessed_at": None,
                "access_count": 0,
            }
            self._knowledge_base[key] = entry
            self._add_to_semantic_index(key, category)

            self._storage_count += 1
            self.logger.debug(f"Stored '{key}' in category '{category}'")
            return True

        except Exception as exc:
            self.logger.error(f"Failed to store '{key}': {exc}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data by key and persist access metadata when enabled."""
        if key not in self._knowledge_base:
            self.logger.debug(f"Key '{key}' not found")
            return None

        entry = self._knowledge_base[key]
        accessed_at = datetime.now()
        access_count = int(entry.get("access_count", 0)) + 1

        if self._database_path:
            try:
                with self._connect() as connection:
                    connection.execute(
                        """
                        UPDATE memories
                        SET accessed_at = ?, access_count = ?
                        WHERE key = ?
                        """,
                        (accessed_at.isoformat(), access_count, key),
                    )
            except Exception as exc:
                self.logger.error(f"Failed to persist access for '{key}': {exc}")
                return None

        entry["accessed_at"] = accessed_at
        entry["access_count"] = access_count
        self.logger.debug(f"Retrieved '{key}' (access #{access_count})")
        return entry["data"]

    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search memory entries by case-insensitive substring."""
        results = []

        for key, entry in self._knowledge_base.items():
            if category and entry.get("category") != category:
                continue

            content_str = str(entry.get("data", ""))
            if query.lower() in content_str.lower():
                results.append({
                    "key": key,
                    "data": entry["data"],
                    "category": entry.get("category"),
                    "relevance": self._calculate_relevance(query, entry),
                })

        results.sort(key=lambda item: item["relevance"], reverse=True)
        self.logger.debug(f"Search found {len(results)} matches for '{query}'")
        return results

    def delete(self, key: str) -> bool:
        """Delete a memory from both the live index and durable storage."""
        if key not in self._knowledge_base:
            return False

        if self._database_path:
            try:
                with self._connect() as connection:
                    connection.execute("DELETE FROM memories WHERE key = ?", (key,))
            except Exception as exc:
                self.logger.error(f"Failed to delete persisted '{key}': {exc}")
                return False

        entry = self._knowledge_base.pop(key)
        self._remove_from_semantic_index(key, entry.get("category", "general"))
        self.logger.debug(f"Deleted '{key}'")
        return True

    def get_categories(self) -> List[str]:
        """Get all categories."""
        return list(self._semantic_network.keys())

    def get_by_category(self, category: str) -> List[Dict]:
        """Get all entries in a category."""
        entries = []
        for key in self._semantic_network.get(category, []):
            if key in self._knowledge_base:
                entries.append(self._knowledge_base[key])
        return entries

    def _calculate_relevance(self, query: str, entry: Dict) -> float:
        """Calculate simple recency and access-frequency relevance."""
        score = entry.get("access_count", 0) * 0.1

        created = entry.get("created_at")
        if created:
            age_days = (datetime.now() - created).days
            score += max(0, 1.0 - age_days / 365)

        return score

    def consolidate(self) -> Dict[str, Any]:
        """Return a consolidation report without mutating memories."""
        old_items = [
            key
            for key, entry in self._knowledge_base.items()
            if entry.get("access_count", 0) == 0
        ]

        report = {
            "total_entries": len(self._knowledge_base),
            "categories": len(self._semantic_network),
            "consolidation_candidates": len(old_items),
            "timestamp": datetime.now(),
            "persistent": self.is_persistent,
        }
        self.logger.info(f"Consolidation complete: {report}")
        return report

    def export(self) -> str:
        """Export the live memory index as JSON."""
        return json.dumps(self._knowledge_base, default=str, ensure_ascii=False)

    def clear(self) -> None:
        """Clear all long-term memory, including durable storage."""
        if self._database_path:
            with self._connect() as connection:
                connection.execute("DELETE FROM memories")

        self._knowledge_base.clear()
        self._semantic_network.clear()
        self.logger.warning("Long-term memory cleared")

    def _resolve_database_path(self, storage_path: str) -> Path:
        path = Path(storage_path).expanduser()
        if path.suffix.lower() in self._DATABASE_SUFFIXES:
            database_path = path
        else:
            database_path = path / "long_term_memory.sqlite3"

        database_path.parent.mkdir(parents=True, exist_ok=True)
        return database_path

    def _connect(self) -> sqlite3.Connection:
        if self._database_path is None:
            raise RuntimeError("Persistent storage is not enabled")
        return sqlite3.connect(str(self._database_path), timeout=5.0)

    def _initialize_storage(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    key TEXT PRIMARY KEY,
                    data_json TEXT NOT NULL,
                    category TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    accessed_at TEXT,
                    access_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def _load_from_storage(self) -> None:
        self._knowledge_base.clear()
        self._semantic_network.clear()

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT key, data_json, category, created_at, accessed_at, access_count
                FROM memories
                ORDER BY created_at ASC
                """
            ).fetchall()

        for key, data_json, category, created_at, accessed_at, access_count in rows:
            entry = {
                "key": key,
                "data": self._deserialize_data(data_json),
                "category": category,
                "created_at": datetime.fromisoformat(created_at),
                "accessed_at": (
                    datetime.fromisoformat(accessed_at) if accessed_at else None
                ),
                "access_count": int(access_count),
            }
            self._knowledge_base[key] = entry
            self._add_to_semantic_index(key, category)

        self.logger.debug(f"Loaded {len(rows)} persisted memories")

    def _serialize_data(self, data: Any) -> str:
        return json.dumps(data, ensure_ascii=False, default=str)

    def _deserialize_data(self, payload: str) -> Any:
        return json.loads(payload)

    def _add_to_semantic_index(self, key: str, category: str) -> None:
        keys = self._semantic_network.setdefault(category, [])
        if key not in keys:
            keys.append(key)

    def _remove_from_semantic_index(self, key: str, category: str) -> None:
        keys = self._semantic_network.get(category)
        if not keys:
            return
        if key in keys:
            keys.remove(key)
        if not keys:
            self._semantic_network.pop(category, None)

    def __len__(self) -> int:
        return len(self._knowledge_base)

    def __repr__(self) -> str:
        mode = "sqlite" if self.is_persistent else "memory"
        return (
            f"LongTermMemory(entries={len(self._knowledge_base)}, "
            f"categories={len(self._semantic_network)}, mode='{mode}')"
        )
