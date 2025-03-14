from abc import ABC, abstractmethod
from typing import Dict, Any

class PluginInterface(ABC):
    """Base interface that all plugins must implement."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with the given configuration.
        
        Args:
            config: Configuration dictionary for the plugin
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
        
    @abstractmethod
    def execute(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command with the given parameters.
        
        Args:
            command: The command to execute
            params: Parameters for the command
            
        Returns:
            dict: Result of the command execution
        """
        pass
