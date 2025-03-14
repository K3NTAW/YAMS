import os
import importlib.util
import inspect
from typing import Dict, List, Optional, Type
from .plugin_interface import PluginInterface

class PluginLoader:
    """Handles loading and managing plugins."""
    
    def __init__(self, plugin_dir: str):
        """Initialize the plugin loader.
        
        Args:
            plugin_dir: Directory containing plugin files
        """
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginInterface] = {}
        self.load_plugins()
    
    def load_plugins(self) -> None:
        """Load all plugins from the plugin directory."""
        self.plugins.clear()
        
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return
            
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                plugin_path = os.path.join(self.plugin_dir, filename)
                self.load_plugin(plugin_path)
    
    def load_plugin(self, plugin_path: str) -> Optional[PluginInterface]:
        """Load a single plugin from the given path.
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            Optional[PluginInterface]: Loaded plugin instance or None if loading failed
        """
        try:
            # Get module name from filename
            module_name = os.path.splitext(os.path.basename(plugin_path))[0]
            
            # Load module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            for item_name, item in inspect.getmembers(module):
                if (inspect.isclass(item) and 
                    issubclass(item, PluginInterface) and 
                    item != PluginInterface):
                    # Initialize plugin
                    plugin = item()
                    if plugin.initialize({}):
                        self.plugins[module_name] = plugin
                        return plugin
            
            return None
            
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            return None
    
    def get_plugins(self) -> Dict[str, PluginInterface]:
        """Get all loaded plugins.
        
        Returns:
            Dict[str, PluginInterface]: Dictionary of plugin names to plugin instances
        """
        return self.plugins
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get a specific plugin by name.
        
        Args:
            name: Name of the plugin
            
        Returns:
            Optional[PluginInterface]: Plugin instance or None if not found
        """
        return self.plugins.get(name)
