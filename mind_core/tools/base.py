"""
Base Tool - Abstract base class for tool integrations.

This module defines the interface that all external tool adapters must implement,
ensuring consistent integration with the mind core.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """
    Abstract base class for external tool integration.
    
    All tool implementations must inherit from this class and implement
    the required methods for consistent integration.
    
    Features:
    - Standardized interface
    - API key management
    - Error handling
    - Execution metrics
    """
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        """
        Initialize the base tool.
        
        Args:
            name: Unique identifier for the tool
            api_key: API key for authentication (optional)
        """
        self.name = name
        self.api_key = api_key
        self.logger = logging.getLogger(f"Tool.{name}")
        
        # Metrics
        self._execution_count = 0
        self._error_count = 0
        self._last_execution = None
        
        self.logger.info(f"Tool '{name}' initialized")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool's primary function.
        
        This method must be implemented by all subclasses.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Execution result
            
        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def validate_api_key(self) -> bool:
        """
        Validate the API key.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            self.logger.warning(f"Tool '{self.name}' has no API key")
            return False
        
        # Basic validation - subclasses should override
        if len(self.api_key) < 10:
            self.logger.warning(f"Tool '{self.name}' API key seems too short")
            return False
        
        self.logger.debug(f"Tool '{self.name}' API key validated")
        return True
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set or update the API key.
        
        Args:
            api_key: New API key
        """
        self.api_key = api_key
        self.logger.debug(f"Tool '{self.name}' API key updated")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get tool execution metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "name": self.name,
            "execution_count": self._execution_count,
            "error_count": self._error_count,
            "success_rate": self._calculate_success_rate(),
            "last_execution": self._last_execution,
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate."""
        if self._execution_count == 0:
            return 1.0
        
        errors = self._error_count
        total = self._execution_count
        return (total - errors) / total
    
    def _record_execution(self, success: bool = True) -> None:
        """
        Record an execution event.
        
        Args:
            success: Whether execution was successful
        """
        from datetime import datetime
        self._execution_count += 1
        self._last_execution = datetime.now()
        
        if not success:
            self._error_count += 1
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
