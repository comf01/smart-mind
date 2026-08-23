"""
Perception Module - Input processing and sensory interpretation.

This module handles the intake and initial processing of various input types,
converting raw data into structured information for cognitive processing.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class PerceptionModule:
    """
    Implements input perception and processing capabilities.
    
    Features:
    - Multi-modal input handling
    - Signal processing
    - Feature extraction
    - Attention mechanisms
    """
    
    def __init__(self):
        """Initialize the perception module."""
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
        
        self.logger.info("Perception module initialized")
    
    def activate(self) -> None:
        """Activate the perception module."""
        self._active = True
        self.logger.info("Perception module activated")
    
    def deactivate(self) -> None:
        """Deactivate the perception module."""
        self._active = False
        self._input_buffer = []
        self.logger.info("Perception module deactivated")
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Process incoming perceptual data.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Structured perceptual output
        """
        if not self._active:
            return {"raw": input_data}
        
        # Determine input type
        input_type = self._classify_input(input_data)
        
        # Apply attention filter
        if not self._should_attend(input_type):
            self.logger.debug(f"Ignoring input type: {input_type}")
            return {"ignored": True, "type": input_type}
        
        # Process based on type
        processed = self._process_by_type(input_data, input_type)
        
        self._processed_count += 1
        self.logger.debug(f"Processed {input_type} input")
        
        return processed
    
    def _classify_input(self, data: Any) -> str:
        """Classify the type of input."""
        if isinstance(data, str):
            return "text"
        elif isinstance(data, (int, float)):
            return "numeric"
        elif isinstance(data, dict):
            return "structured"
        elif isinstance(data, (list, tuple)):
            return "sequence"
        else:
            return "unknown"
    
    def _should_attend(self, input_type: str) -> bool:
        """Determine if attention should be given to this input type."""
        if self._attention_focus is None:
            return True
        
        return input_type == self._attention_focus
    
    def _process_by_type(self, data: Any, input_type: str) -> Dict[str, Any]:
        """Process data based on its type."""
        processors = {
            "text": self._process_text,
            "numeric": self._process_numeric,
            "structured": self._process_structured,
            "sequence": self._process_sequence,
        }
        
        processor = processors.get(input_type, self._process_unknown)
        return processor(data)
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process text input."""
        return {
            "type": "text",
            "content": text,
            "length": len(text),
            "words": len(text.split()),
            "timestamp": datetime.now(),
        }
    
    def _process_numeric(self, value: Union[int, float]) -> Dict[str, Any]:
        """Process numeric input."""
        return {
            "type": "numeric",
            "value": value,
            "magnitude": abs(value),
            "timestamp": datetime.now(),
        }
    
    def _process_structured(self, data: dict) -> Dict[str, Any]:
        """Process structured input."""
        return {
            "type": "structured",
            "keys": list(data.keys()),
            "size": len(data),
            "content": data,
            "timestamp": datetime.now(),
        }
    
    def _process_sequence(self, seq: Union[list, tuple]) -> Dict[str, Any]:
        """Process sequence input."""
        return {
            "type": "sequence",
            "length": len(seq),
            "types": [type(item).__name__ for item in seq],
            "content": list(seq),
            "timestamp": datetime.now(),
        }
    
    def _process_unknown(self, data: Any) -> Dict[str, Any]:
        """Process unknown input type."""
        return {
            "type": "unknown",
            "repr": repr(data),
            "timestamp": datetime.now(),
        }
    
    def set_attention(self, focus: Optional[str]) -> None:
        """
        Set attention focus.
        
        Args:
            focus: Input type to focus on, or None for broad attention
        """
        self._attention_focus = focus
        self.logger.debug(f"Attention set to: {focus or 'broad'}")
    
    def enable_channel(self, channel: str) -> None:
        """
        Enable a sensory channel.
        
        Args:
            channel: Channel name to enable
        """
        if channel in self._sensory_channels:
            self._sensory_channels[channel] = True
            self.logger.debug(f"Channel enabled: {channel}")
    
    def disable_channel(self, channel: str) -> None:
        """
        Disable a sensory channel.
        
        Args:
            channel: Channel name to disable
        """
        if channel in self._sensory_channels:
            self._sensory_channels[channel] = False
            self.logger.debug(f"Channel disabled: {channel}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get perception module status.
        
        Returns:
            Current status information
        """
        return {
            "active": self._active,
            "attention_focus": self._attention_focus,
            "channels": self._sensory_channels.copy(),
            "buffer_size": len(self._input_buffer),
            "processed_count": self._processed_count,
        }
    
    def __repr__(self) -> str:
        return f"PerceptionModule(active={self._active}, focus={self._attention_focus})"
