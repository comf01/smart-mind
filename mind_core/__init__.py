"""
Mind Core - Super-Intelligent Mind System
==========================================

A modular, extensible core architecture for an advanced AI mind system
with seamless tool integration via API keys.
"""

from .core.context import CognitiveContext, CognitiveModule
from .core.engine import MindCore, Thought
from .core.consciousness import ConsciousnessModule
from .modules.reasoning import ReasoningEngine
from .modules.learning import LearningModule
from .memory.short_term import ShortTermMemory
from .memory.long_term import LongTermMemory
from .tools.base import BaseTool

__version__ = "1.0.0"
__author__ = "Mind Core Team"
__all__ = [
    "CognitiveContext",
    "CognitiveModule",
    "MindCore",
    "Thought",
    "ConsciousnessModule",
    "ReasoningEngine",
    "LearningModule",
    "ShortTermMemory",
    "LongTermMemory",
    "BaseTool",
]
