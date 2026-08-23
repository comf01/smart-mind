"""
Mind Core Engine - The central processing unit of the super-intelligent mind.

This module orchestrates all cognitive processes, manages modules,
handles tool integration, and maintains the overall state of the mind.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from ..security.credentials import CredentialManager
from ..memory.short_term import ShortTermMemory
from ..memory.long_term import LongTermMemory


@dataclass
class Thought:
    """Represents a single thought or cognitive process result."""
    
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def response(self) -> str:
        """Return the content as a response string."""
        return self.content


class MindCore:
    """
    The central engine of the super-intelligent mind.
    
    This class manages:
    - Cognitive module activation and coordination
    - Tool integration via secure API keys
    - Memory systems (short-term and long-term)
    - Asynchronous processing of thoughts
    - Self-monitoring and meta-cognition
    """
    
    def __init__(self, name: str = "Core", config: Optional[Dict] = None):
        """
        Initialize the Mind Core.
        
        Args:
            name: Identifier for this mind instance
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        
        # Set up logging
        self.logger = logging.getLogger(f"MindCore.{name}")
        log_level = self.config.get("LOG_LEVEL", "INFO")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Initialize credential manager for secure API key handling
        self.credential_manager = CredentialManager()
        
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory(
            limit=self.config.get("MEMORY_LIMIT", 10000)
        )
        self.long_term_memory = LongTermMemory()
        
        # Module registry
        self._modules: Dict[str, Any] = {}
        self._active_modules: List[str] = []
        
        # Tool registry
        self._tools: Dict[str, Any] = {}
        
        # State tracking
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
        """
        Initialize all core systems and prepare the mind for operation.
        """
        if self._initialized:
            self.logger.warning("Mind Core already initialized")
            return
        
        self.logger.info("Initializing Mind Core systems...")
        
        # Load any persisted state
        self._load_state()
        
        self._initialized = True
        self.logger.info("Mind Core initialization complete")
    
    def activate(self, module_name: str) -> bool:
        """
        Activate a cognitive module.
        
        Args:
            module_name: Name of the module to activate
            
        Returns:
            True if activation successful, False otherwise
        """
        if module_name not in self._modules:
            self.logger.error(f"Module '{module_name}' not found")
            return False
        
        if module_name in self._active_modules:
            self.logger.warning(f"Module '{module_name}' already active")
            return True
        
        try:
            module = self._modules[module_name]
            if hasattr(module, 'activate'):
                module.activate()
            
            self._active_modules.append(module_name)
            self.logger.info(f"Module '{module_name}' activated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate module '{module_name}': {e}")
            self._metrics["errors"] += 1
            return False
    
    def deactivate(self, module_name: str) -> bool:
        """
        Deactivate a cognitive module.
        
        Args:
            module_name: Name of the module to deactivate
            
        Returns:
            True if deactivation successful, False otherwise
        """
        if module_name not in self._active_modules:
            self.logger.warning(f"Module '{module_name}' not active")
            return True
        
        try:
            module = self._modules[module_name]
            if hasattr(module, 'deactivate'):
                module.deactivate()
            
            self._active_modules.remove(module_name)
            self.logger.info(f"Module '{module_name}' deactivated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate module '{module_name}': {e}")
            self._metrics["errors"] += 1
            return False
    
    def register_module(self, name: str, module: Any) -> None:
        """
        Register a cognitive module.
        
        Args:
            name: Unique identifier for the module
            module: Module instance
        """
        self._modules[name] = module
        self.logger.debug(f"Module '{name}' registered")
    
    def integrate_tool(self, tool_name: str, api_key: str, **kwargs) -> bool:
        """
        Integrate an external tool with secure API key management.
        
        Args:
            tool_name: Name/identifier for the tool
            api_key: API key for authentication
            **kwargs: Additional tool configuration
            
        Returns:
            True if integration successful, False otherwise
        """
        try:
            # Store API key securely
            encrypted_key = self.credential_manager.encrypt(api_key)
            self.credential_manager.store_credential(tool_name, encrypted_key)
            
            # Create tool instance (simplified - in practice would use factory)
            from .tool_adapter import ToolAdapter
            tool = ToolAdapter(tool_name, api_key, **kwargs)
            self._tools[tool_name] = tool
            
            self.logger.info(f"Tool '{tool_name}' integrated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to integrate tool '{tool_name}': {e}")
            self._metrics["errors"] += 1
            return False
    
    async def think(self, query: str, depth: int = 1) -> Thought:
        """
        Process a thought or query through active cognitive modules.
        
        Args:
            query: The input query or thought to process
            depth: Reasoning depth level
            
        Returns:
            Thought object containing the response
        """
        start_time = datetime.now()
        self._thought_count += 1
        
        # Store in short-term memory
        self.short_term_memory.add(query, role="input")
        
        # Process through active modules
        result = query
        for module_name in self._active_modules:
            try:
                module = self._modules[module_name]
                if hasattr(module, 'process'):
                    result = await module.process(result)
            except Exception as e:
                self.logger.warning(f"Module '{module_name}' failed: {e}")
                self._metrics["errors"] += 1
        
        # Create thought object
        thought = Thought(
            content=result,
            confidence=self._calculate_confidence(),
            metadata={
                "depth": depth,
                "modules_used": self._active_modules.copy(),
                "processing_time": (datetime.now() - start_time).total_seconds(),
            }
        )
        
        # Store in memory
        self.short_term_memory.add(result, role="output")
        self._metrics["thoughts_processed"] += 1
        
        self.logger.debug(f"Thought processed: {query[:50]}...")
        return thought
    
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use an integrated tool.
        
        Args:
            tool_name: Name of the tool to use
            **kwargs: Tool-specific arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self._tools:
            self.logger.error(f"Tool '{tool_name}' not found")
            raise ValueError(f"Tool '{tool_name}' not integrated")
        
        try:
            # Retrieve secure API key
            encrypted_key = self.credential_manager.retrieve_credential(tool_name)
            api_key = self.credential_manager.decrypt(encrypted_key)
            
            tool = self._tools[tool_name]
            result = tool.execute(api_key=api_key, **kwargs)
            
            self._metrics["tool_calls"] += 1
            self.logger.debug(f"Tool '{tool_name}' executed")
            return result
            
        except Exception as e:
            self.logger.error(f"Tool '{tool_name}' execution failed: {e}")
            self._metrics["errors"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retrieve performance metrics.
        
        Returns:
            Dictionary of current metrics
        """
        metrics = self._metrics.copy()
        metrics["uptime"] = (datetime.now() - metrics["uptime"]).total_seconds()
        metrics["active_modules"] = len(self._active_modules)
        metrics["registered_tools"] = len(self._tools)
        metrics["memory_usage"] = len(self.short_term_memory)
        return metrics
    
    def introspect(self) -> Dict[str, Any]:
        """
        Perform self-monitoring and meta-cognitive analysis.
        
        Returns:
            Current state and self-analysis
        """
        return {
            "name": self.name,
            "initialized": self._initialized,
            "active_modules": self._active_modules.copy(),
            "available_modules": list(self._modules.keys()),
            "integrated_tools": list(self._tools.keys()),
            "metrics": self.get_metrics(),
            "consciousness_level": self._assess_consciousness(),
        }
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score for a thought."""
        # Simplified implementation
        base_confidence = 0.7
        module_bonus = len(self._active_modules) * 0.05
        return min(base_confidence + module_bonus, 1.0)
    
    def _assess_consciousness(self) -> str:
        """Assess current consciousness level."""
        if len(self._active_modules) >= 3:
            return "high"
        elif len(self._active_modules) >= 1:
            return "medium"
        else:
            return "low"
    
    def _load_state(self) -> None:
        """Load persisted state from storage."""
        # Implementation for state persistence
        pass
    
    def _save_state(self) -> None:
        """Save current state to storage."""
        # Implementation for state persistence
        pass
    
    def __repr__(self) -> str:
        return f"MindCore(name='{self.name}', modules={len(self._active_modules)}, tools={len(self._tools)})"
