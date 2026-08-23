"""Mind Core Engine - central orchestration for cognitive processing."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .context import CognitiveContext
from ..security.credentials import CredentialManager
from ..memory.short_term import ShortTermMemory
from ..memory.long_term import LongTermMemory


@dataclass
class Thought:
    """Represents the externally visible result of one cognitive cycle."""

    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[CognitiveContext] = None

    @property
    def response(self) -> str:
        return self.content


class MindCore:
    """Coordinates modules, memory, tools, and the shared cognitive context."""

    def __init__(self, name: str = "Core", config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}

        self.logger = logging.getLogger(f"MindCore.{name}")
        log_level = self.config.get("LOG_LEVEL", "INFO")
        self.logger.setLevel(getattr(logging, log_level))

        self.credential_manager = CredentialManager()
        self.short_term_memory = ShortTermMemory(
            limit=self.config.get("MEMORY_LIMIT", 10000)
        )
        self.long_term_memory = LongTermMemory()

        self._modules: Dict[str, Any] = {}
        self._active_modules: List[str] = []
        self._tools: Dict[str, Any] = {}
        self._initialized = False
        self._thought_count = 0
        self._metrics: Dict[str, Any] = {
            "thoughts_processed": 0,
            "tool_calls": 0,
            "errors": 0,
            "uptime": datetime.now(),
        }

        self.logger.info(f"Mind Core '{name}' initialized")

    def initialize(self) -> None:
        if self._initialized:
            self.logger.warning("Mind Core already initialized")
            return
        self._load_state()
        self._initialized = True

    def activate(self, module_name: str) -> bool:
        if module_name not in self._modules:
            self.logger.error(f"Module '{module_name}' not found")
            return False
        if module_name in self._active_modules:
            return True
        try:
            module = self._modules[module_name]
            if hasattr(module, "activate"):
                module.activate()
            self._active_modules.append(module_name)
            return True
        except Exception as exc:
            self.logger.error(f"Failed to activate module '{module_name}': {exc}")
            self._metrics["errors"] += 1
            return False

    def deactivate(self, module_name: str) -> bool:
        if module_name not in self._active_modules:
            return True
        try:
            module = self._modules[module_name]
            if hasattr(module, "deactivate"):
                module.deactivate()
            self._active_modules.remove(module_name)
            return True
        except Exception as exc:
            self.logger.error(f"Failed to deactivate module '{module_name}': {exc}")
            self._metrics["errors"] += 1
            return False

    def register_module(self, name: str, module: Any) -> None:
        self._modules[name] = module

    def integrate_tool(self, tool_name: str, api_key: str, **kwargs) -> bool:
        try:
            encrypted_key = self.credential_manager.encrypt(api_key)
            self.credential_manager.store_credential(tool_name, encrypted_key)
            from .tool_adapter import ToolAdapter

            tool = ToolAdapter(tool_name, api_key, **kwargs)
            self._tools[tool_name] = tool
            return True
        except Exception as exc:
            self.logger.error(f"Failed to integrate tool '{tool_name}': {exc}")
            self._metrics["errors"] += 1
            return False

    async def think(self, query: Any, depth: int = 1) -> Thought:
        """Process a query through modules using one CognitiveContext instance."""
        start_time = datetime.now()
        self._thought_count += 1
        self.short_term_memory.add(query, role="input")

        context = CognitiveContext(
            input=query,
            current=query,
            metadata={"depth": depth},
        )

        for module_name in self._active_modules:
            module = self._modules[module_name]
            if not hasattr(module, "process"):
                context.add_trace(module_name, "skipped", {"reason": "no process method"})
                continue

            try:
                processed = await module.process(context)
            except Exception as exc:
                self._metrics["errors"] += 1
                context.add_trace(module_name, "error", {"error": str(exc)})
                self.logger.error(f"Module '{module_name}' failed: {exc}")
                raise

            if not isinstance(processed, CognitiveContext):
                self._metrics["errors"] += 1
                raise TypeError(
                    f"Module '{module_name}' violated the cognitive contract: "
                    "process() must return CognitiveContext"
                )
            context = processed

        content = context.answer if context.answer is not None else str(context.current)
        thought = Thought(
            content=content,
            confidence=self._calculate_confidence(context),
            metadata={
                "depth": depth,
                "modules_used": self._active_modules.copy(),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "trace_length": len(context.trace),
            },
            context=context,
        )

        self.short_term_memory.add(content, role="output")
        self._metrics["thoughts_processed"] += 1
        return thought

    def use_tool(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not integrated")
        try:
            encrypted_key = self.credential_manager.retrieve_credential(tool_name)
            api_key = self.credential_manager.decrypt(encrypted_key)
            result = self._tools[tool_name].execute(api_key=api_key, **kwargs)
            self._metrics["tool_calls"] += 1
            return result
        except Exception:
            self._metrics["errors"] += 1
            raise

    def get_metrics(self) -> Dict[str, Any]:
        metrics = self._metrics.copy()
        metrics["uptime"] = (datetime.now() - metrics["uptime"]).total_seconds()
        metrics["active_modules"] = len(self._active_modules)
        metrics["registered_tools"] = len(self._tools)
        metrics["memory_usage"] = len(self.short_term_memory)
        return metrics

    def introspect(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initialized": self._initialized,
            "active_modules": self._active_modules.copy(),
            "available_modules": list(self._modules.keys()),
            "integrated_tools": list(self._tools.keys()),
            "metrics": self.get_metrics(),
            "consciousness_level": self._assess_consciousness(),
        }

    def _calculate_confidence(self, context: CognitiveContext) -> float:
        return max(0.0, min(1.0, 1.0 - context.uncertainty))

    def _assess_consciousness(self) -> str:
        if len(self._active_modules) >= 3:
            return "high"
        if len(self._active_modules) >= 1:
            return "medium"
        return "low"

    def _load_state(self) -> None:
        pass

    def _save_state(self) -> None:
        pass

    def __repr__(self) -> str:
        return (
            f"MindCore(name='{self.name}', modules={len(self._active_modules)}, "
            f"tools={len(self._tools)})"
        )
