"""Meta-cognitive monitor operating on the shared cognitive context."""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .context import CognitiveContext


class ConsciousnessModule:
    def __init__(self, mind_name: str = "Core"):
        self.mind_name = mind_name
        self.logger = logging.getLogger(f"Consciousness.{mind_name}")
        self._self_model: Dict[str, Any] = {
            "identity": mind_name,
            "created_at": datetime.now(),
            "capabilities": [],
            "limitations": [],
        }
        self._awareness_level = 0.0
        self._active_processes: List[str] = []
        self._introspection_history: List[Dict] = []
        self._confidence_threshold = 0.7
        self._uncertainty_alerts = True
        self._active = False

    def activate(self) -> None:
        self._active = True
        self._awareness_level = 0.8

    def deactivate(self) -> None:
        self._active = False
        self._awareness_level = 0.0

    async def process(self, context: CognitiveContext) -> CognitiveContext:
        if not self._active:
            return context

        context.metadata["metacognition"] = {
            "awareness_level": self._awareness_level,
            "timestamp": datetime.now().isoformat(),
            "self_model_version": "1.0",
        }
        self._check_uncertainty(context)
        context.add_trace(
            self.__class__.__name__,
            "monitored",
            {"uncertainty": context.uncertainty},
        )
        return context

    def introspect(self) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.now(),
            "identity": self._self_model["identity"],
            "awareness_level": self._awareness_level,
            "active_processes": self._active_processes.copy(),
            "self_model": self._self_model.copy(),
            "meta_state": {
                "confidence_threshold": self._confidence_threshold,
                "uncertainty_monitoring": self._uncertainty_alerts,
            },
        }
        self._introspection_history.append(report)
        return report

    def update_self_model(self, capability: str, add: bool = True) -> None:
        target = "capabilities" if add else "limitations"
        if capability not in self._self_model[target]:
            self._self_model[target].append(capability)

    def register_process(self, process_name: str) -> None:
        if process_name not in self._active_processes:
            self._active_processes.append(process_name)

    def unregister_process(self, process_name: str) -> None:
        if process_name in self._active_processes:
            self._active_processes.remove(process_name)

    def _check_uncertainty(self, context: CognitiveContext) -> None:
        if not self._uncertainty_alerts:
            return
        confidence = 1.0 - context.uncertainty
        if confidence < self._confidence_threshold:
            self.logger.warning(f"Low confidence detected: {confidence:.2f}")
            self.update_self_model("uncertainty_detection")

    def get_awareness_level(self) -> float:
        return self._awareness_level

    def set_awareness_level(self, level: float) -> None:
        self._awareness_level = max(0.0, min(1.0, level))

    def __repr__(self) -> str:
        return f"ConsciousnessModule(name='{self.mind_name}', awareness={self._awareness_level:.2f})"
