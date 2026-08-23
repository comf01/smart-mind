"""Conservative lexical retrieval over LongTermMemory."""

import math
import re
from typing import Any, Dict, List, Set

from .long_term import LongTermMemory


class LexicalMemoryRetriever:
    """Return only memories with sufficient lexical overlap to ground reasoning."""

    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "how", "in", "is", "it", "of", "on", "or", "that", "the", "this",
        "to", "was", "were", "what", "when", "where", "which", "who", "why",
        "ما", "ماذا", "من", "هو", "هي", "هل", "في", "على", "إلى", "الى",
        "عن", "مع", "هذا", "هذه", "ذلك", "تلك", "الذي", "التي", "أو", "او",
    }

    def __init__(
        self,
        memory: LongTermMemory,
        limit: int = 1,
        min_coverage: float = 0.6,
    ) -> None:
        self.memory = memory
        self.limit = max(1, int(limit))
        self.min_coverage = max(0.0, min(1.0, float(min_coverage)))

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve the best sufficiently matching memory entries for a query."""
        terms = self._tokenize(query)
        if not terms:
            return []

        candidates: Dict[str, Dict[str, Any]] = {}
        for term in terms:
            for result in self.memory.search(term):
                key = str(result.get("key"))
                candidate = candidates.setdefault(
                    key,
                    {"result": result, "hits": set()},
                )
                candidate["hits"].add(term)

        minimum_hits = max(1, math.ceil(len(terms) * self.min_coverage))
        ranked: List[Dict[str, Any]] = []

        for candidate in candidates.values():
            hits: Set[str] = candidate["hits"]
            if len(hits) < minimum_hits:
                continue

            result = dict(candidate["result"])
            result["match_score"] = len(hits) / len(terms)
            ranked.append(result)

        ranked.sort(
            key=lambda item: (
                item.get("match_score", 0.0),
                item.get("relevance", 0.0),
            ),
            reverse=True,
        )
        return ranked[: self.limit]

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[^\W_]+", str(text).casefold(), flags=re.UNICODE)
        seen = set()
        useful = []
        for token in tokens:
            if len(token) < 2 or token in self.STOPWORDS or token in seen:
                continue
            seen.add(token)
            useful.append(token)
        return useful
