import importlib
import os
import sys
from typing import Dict, Any, Optional

class PluginLoader:
    """A class to handle loading and managing plugins."""
    
    def __init__(self, plugin_dir: str):
        """Initialize the plugin loader.
        
        Args:
            plugin_dir: Directory containing the plugins
        """
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        """Load all plugins from the plugin directory."""
        try:
            # Add plugin directory to Python path if not already there
            if self.plugin_dir not in sys.path:
                sys.path.append(self.plugin_dir)
            
            # Look for Python files in the plugin directory
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    plugin_name = filename[:-3]  # Remove .py extension
                    try:
                        # Import the plugin module
                        plugin_module = importlib.import_module(plugin_name)
                        if hasattr(plugin_module, 'setup_plugin'):
                            plugin = plugin_module.setup_plugin()
                            self.plugins[plugin_name] = plugin
                    except Exception as e:
                        print(f"Error loading plugin {plugin_name}: {e}")
        except Exception as e:
            print(f"Error loading plugins: {e}")
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a plugin by name.
        
        Args:
            name: Name of the plugin to get
            
        Returns:
            The plugin instance if found, None otherwise
        """
        return self.plugins.get(name)
    
    def list_plugins(self) -> Dict[str, Any]:
        """Get a dictionary of all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return self.plugins.copy()
