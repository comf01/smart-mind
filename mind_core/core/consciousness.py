"""
Consciousness Module - Self-awareness and meta-cognition capabilities.

This module provides the mind with introspective abilities, self-monitoring,
and awareness of its own cognitive processes.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime


class ConsciousnessModule:
    """
    Implements self-awareness and meta-cognitive functions.
    
    Features:
    - Self-monitoring of cognitive states
    - Awareness of active processes
    - Introspective analysis
    - Identity maintenance
    """
    
    def __init__(self, mind_name: str = "Core"):
        """
        Initialize the consciousness module.
        
        Args:
            mind_name: Name of the associated mind instance
        """
        self.mind_name = mind_name
        self.logger = logging.getLogger(f"Consciousness.{mind_name}")
        
        # Self-model
        self._self_model: Dict[str, Any] = {
            "identity": mind_name,
            "created_at": datetime.now(),
            "capabilities": [],
            "limitations": [],
        }
        
        # Awareness state
        self._awareness_level = 0.0
        self._active_processes: List[str] = []
        self._introspection_history: List[Dict] = []
        
        # Meta-cognitive state
        self._confidence_threshold = 0.7
        self._uncertainty_alerts = True
        
        self._active = False
        self.logger.info("Consciousness module initialized")
    
    def activate(self) -> None:
        """Activate the consciousness module."""
        self._active = True
        self._awareness_level = 0.8
        self.logger.info("Consciousness module activated")
    
    def deactivate(self) -> None:
        """Deactivate the consciousness module."""
        self._active = False
        self._awareness_level = 0.0
        self.logger.info("Consciousness module deactivated")
    
    async def process(self, input_data: Any) -> Any:
        """
        Process input through consciousness lens.
        
        Args:
            input_data: Data to process
            
        Returns:
            Processed data with meta-cognitive annotations
        """
        if not self._active:
            return input_data
        
        # Add self-awareness metadata
        if isinstance(input_data, dict):
            input_data["_consciousness"] = {
                "awareness_level": self._awareness_level,
                "timestamp": datetime.now(),
                "self_model_version": "1.0",
            }
        
        # Monitor for uncertainty
        self._check_uncertainty(input_data)
        
        return input_data
    
    def introspect(self) -> Dict[str, Any]:
        """
        Perform deep introspection of current state.
        
        Returns:
            Comprehensive self-analysis report
        """
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
        self.logger.debug("Introspection completed")
        
        return report
    
    def update_self_model(self, capability: str, add: bool = True) -> None:
        """
        Update the self-model with new capabilities or limitations.
        
        Args:
            capability: Capability to add/remove
            add: If True, add to capabilities; if False, add to limitations
        """
        if add:
            if capability not in self._self_model["capabilities"]:
                self._self_model["capabilities"].append(capability)
        else:
            if capability not in self._self_model["limitations"]:
                self._self_model["limitations"].append(capability)
        
        self.logger.debug(f"Self-model updated: {capability} (added={add})")
    
    def register_process(self, process_name: str) -> None:
        """
        Register an active cognitive process.
        
        Args:
            process_name: Name of the process
        """
        if process_name not in self._active_processes:
            self._active_processes.append(process_name)
            self.logger.debug(f"Process registered: {process_name}")
    
    def unregister_process(self, process_name: str) -> None:
        """
        Unregister a completed cognitive process.
        
        Args:
            process_name: Name of the process
        """
        if process_name in self._active_processes:
            self._active_processes.remove(process_name)
            self.logger.debug(f"Process unregistered: {process_name}")
    
    def _check_uncertainty(self, data: Any) -> None:
        """
        Check for signs of uncertainty in processed data.
        
        Args:
            data: Data to analyze
        """
        if not self._uncertainty_alerts:
            return
        
        # Simple uncertainty detection
        if isinstance(data, dict) and data.get("confidence", 1.0) < self._confidence_threshold:
            self.logger.warning(f"Low confidence detected: {data.get('confidence')}")
            self.update_self_model("uncertainty_detection")
    
    def get_awareness_level(self) -> float:
        """
        Get current awareness level.
        
        Returns:
            Awareness level (0.0 to 1.0)
        """
        return self._awareness_level
    
    def set_awareness_level(self, level: float) -> None:
        """
        Set awareness level.
        
        Args:
            level: Level between 0.0 and 1.0
        """
        self._awareness_level = max(0.0, min(1.0, level))
        self.logger.debug(f"Awareness level set to: {self._awareness_level}")
    
    def __repr__(self) -> str:
        return f"ConsciousnessModule(name='{self.mind_name}', awareness={self._awareness_level:.2f})"
