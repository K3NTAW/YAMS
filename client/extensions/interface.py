from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class PluginInterface(ABC):
    """Base interface that all plugins must implement."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the plugin description."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get the plugin version."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a plugin command with optional arguments."""
        pass
    
    @abstractmethod
    def get_commands(self) -> Dict[str, str]:
        """Get a dictionary of available commands and their descriptions."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources when plugin is being unloaded."""
        pass
