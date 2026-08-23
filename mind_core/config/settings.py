"""
Settings - Configuration management for the mind core.

This module handles loading, validating, and providing access to configuration
settings from environment variables and configuration files.
"""

import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path


class Settings:
    """
    Manages configuration settings for the mind core.
    
    Features:
    - Environment variable loading
    - Default values
    - Type validation
    - Hot reloading support
    """
    
    # Default configuration
    DEFAULTS = {
        "MIND_NAME": "Core",
        "MEMORY_LIMIT": 10000,
        "REASONING_DEPTH": 10,
        "TOOL_TIMEOUT": 30,
        "LOG_LEVEL": "INFO",
        "ENCRYPTION_ENABLED": True,
        "MAX_CONCURRENT_THOUGHTS": 5,
        "PERSISTENCE_PATH": "./mind_data",
    }
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize settings.
        
        Args:
            env_file: Path to .env file (optional)
        """
        self.logger = logging.getLogger("Settings")
        self._config: Dict[str, Any] = {}
        
        # Load defaults
        self._config.update(self.DEFAULTS)
        
        # Load from .env file if provided
        if env_file:
            self._load_env_file(env_file)
        
        # Override with environment variables
        self._load_from_environment()
        
        self.logger.info("Settings initialized")
    
    def _load_env_file(self, path: str) -> None:
        """Load settings from a .env file."""
        env_path = Path(path)
        
        if not env_path.exists():
            self.logger.warning(f"Env file not found: {path}")
            return
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # Try to convert to appropriate type
                        self._config[key] = self._convert_value(value)
            
            self.logger.debug(f"Loaded settings from {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load env file: {e}")
    
    def _load_from_environment(self) -> None:
        """Load settings from environment variables."""
        for key in self.DEFAULTS.keys():
            env_value = os.environ.get(key)
            if env_value:
                self._config[key] = self._convert_value(env_value)
                self.logger.debug(f"Loaded {key} from environment")
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        # Boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # String
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        value = self._config.get(key, default)
        
        if value is None and key in self.DEFAULTS:
            return self.DEFAULTS[key]
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self.logger.debug(f"Set {key} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all settings
        """
        return self._config.copy()
    
    def get_safe(self) -> Dict[str, Any]:
        """
        Get non-sensitive configuration values.
        
        Returns:
            Dictionary of safe-to-log settings
        """
        sensitive_keys = ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN']
        
        return {
            k: v for k, v in self._config.items()
            if not any(s in k.upper() for s in sensitive_keys)
        }
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid
        """
        errors = []
        
        # Check required settings
        if not self.get("MIND_NAME"):
            errors.append("MIND_NAME is required")
        
        # Check value ranges
        memory_limit = self.get("MEMORY_LIMIT")
        if memory_limit < 100:
            errors.append("MEMORY_LIMIT must be at least 100")
        
        tool_timeout = self.get("TOOL_TIMEOUT")
        if tool_timeout < 1:
            errors.append("TOOL_TIMEOUT must be at least 1")
        
        if errors:
            for error in errors:
                self.logger.error(f"Validation error: {error}")
            return False
        
        self.logger.debug("Configuration validated successfully")
        return True
    
    def reload(self) -> None:
        """Reload configuration from environment."""
        self._config.update(self.DEFAULTS)
        self._load_from_environment()
        self.logger.info("Configuration reloaded")
    
    def __repr__(self) -> str:
        safe_config = {k: v for k, v in self._config.items() 
                      if not any(s in k.upper() for s in ['KEY', 'SECRET', 'PASSWORD'])}
        return f"Settings({len(safe_config)} items)"
