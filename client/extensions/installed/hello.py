from extensions.interface import PluginInterface
from typing import Any, Dict, Optional

class HelloPlugin(PluginInterface):
    """A simple hello world plugin for testing."""
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        print("Hello plugin initialized")
        return True
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return "Hello World"
    
    def get_description(self) -> str:
        """Get the plugin description."""
        return "A simple plugin that says hello"
    
    def get_version(self) -> str:
        """Get the plugin version."""
        return "1.0.0"
    
    def execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a plugin command."""
        if command == "greet":
            name = args.get("name", "World") if args else "World"
            return f"Hello, {name}!"
        return "Unknown command"
    
    def get_commands(self) -> Dict[str, str]:
        """Get available commands."""
        return {
            "greet": "Say hello to someone. Args: name (optional)"
        }
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        print("Hello plugin cleaned up")
