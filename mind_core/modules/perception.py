"""Perception module that enriches the shared cognitive context."""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..core.context import CognitiveContext


class PerceptionModule:
    def __init__(self):
        self.logger = logging.getLogger("PerceptionModule")
        self._active = False
        self._input_buffer: List[Dict] = []
        self._attention_focus: Optional[str] = None
        self._sensory_channels: Dict[str, bool] = {
            "text": True,
            "audio": False,
            "visual": False,
            "data": True,
        }
        self._processed_count = 0

    def activate(self) -> None:
        self._active = True

    def deactivate(self) -> None:
        self._active = False
        self._input_buffer = []

    async def process(self, context: CognitiveContext) -> CognitiveContext:
        if not self._active:
            return context

        input_data = context.current
        input_type = self._classify_input(input_data)
        if not self._should_attend(input_type):
            context.add_trace(self.__class__.__name__, "ignored", {"type": input_type})
            return context

        processed = self._process_by_type(input_data, input_type)
        context.observations.append(processed)
        context.current = processed
        context.add_trace(
            self.__class__.__name__,
            "perceived",
            {"type": input_type},
        )
        self._processed_count += 1
        return context

    def _classify_input(self, data: Any) -> str:
        if isinstance(data, str):
            return "text"
        if isinstance(data, (int, float)):
            return "numeric"
        if isinstance(data, dict):
            return "structured"
        if isinstance(data, (list, tuple)):
            return "sequence"
        return "unknown"

    def _should_attend(self, input_type: str) -> bool:
        return self._attention_focus is None or input_type == self._attention_focus

    def _process_by_type(self, data: Any, input_type: str) -> Dict[str, Any]:
        processors = {
            "text": self._process_text,
            "numeric": self._process_numeric,
            "structured": self._process_structured,
            "sequence": self._process_sequence,
        }
        return processors.get(input_type, self._process_unknown)(data)

    def _process_text(self, text: str) -> Dict[str, Any]:
        return {
            "type": "text",
            "content": text,
            "length": len(text),
            "words": len(text.split()),
            "timestamp": datetime.now(),
        }

    def _process_numeric(self, value: Union[int, float]) -> Dict[str, Any]:
        return {
            "type": "numeric",
            "value": value,
            "magnitude": abs(value),
            "timestamp": datetime.now(),
        }

    def _process_structured(self, data: dict) -> Dict[str, Any]:
        return {
            "type": "structured",
            "keys": list(data.keys()),
            "size": len(data),
            "content": data,
            "timestamp": datetime.now(),
        }

    def _process_sequence(self, seq: Union[list, tuple]) -> Dict[str, Any]:
        return {
            "type": "sequence",
            "length": len(seq),
            "types": [type(item).__name__ for item in seq],
            "content": list(seq),
            "timestamp": datetime.now(),
        }

    def _process_unknown(self, data: Any) -> Dict[str, Any]:
        return {"type": "unknown", "repr": repr(data), "timestamp": datetime.now()}

    def set_attention(self, focus: Optional[str]) -> None:
        self._attention_focus = focus

    def enable_channel(self, channel: str) -> None:
        if channel in self._sensory_channels:
            self._sensory_channels[channel] = True

    def disable_channel(self, channel: str) -> None:
        if channel in self._sensory_channels:
            self._sensory_channels[channel] = False

    def get_status(self) -> Dict[str, Any]:
        return {
            "active": self._active,
            "attention_focus": self._attention_focus,
            "channels": self._sensory_channels.copy(),
            "buffer_size": len(self._input_buffer),
            "processed_count": self._processed_count,
        }

    def __repr__(self) -> str:
        return f"PerceptionModule(active={self._active}, focus={self._attention_focus})"
