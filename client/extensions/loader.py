import os
import sys
import importlib.util
from typing import Dict, Any, Optional
from .interface import PluginInterface

class PluginLoader:
    """Plugin loader for dynamically loading and managing plugins."""
    
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}
        self.load_plugins()
    
    def load_plugins(self) -> None:
        """Load all plugins from the plugin directory."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return

        # Ensure plugin directory is in Python path
        if self.plugin_dir not in sys.path:
            sys.path.append(self.plugin_dir)

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                plugin_name = filename[:-3]  # Remove .py extension
                try:
                    plugin = self.load_plugin(plugin_name, os.path.join(self.plugin_dir, filename))
                    if plugin:
                        self.plugins[plugin_name] = plugin
                except Exception as e:
                    print(f"Error loading plugin {plugin_name}: {e}")

    def load_plugin(self, plugin_name: str, plugin_path: str) -> Optional[Any]:
        """Load a single plugin by name and path."""
        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class (class that implements PluginInterface)
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, PluginInterface) and 
                    item != PluginInterface):
                    return item()

            print(f"No valid plugin class found in {plugin_name}")
            return None

        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return None

    def get_plugins(self) -> Dict[str, Any]:
        """Get all loaded plugins."""
        return self.plugins

    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a specific plugin by name."""
        return self.plugins.get(name)

    def install_plugin(self, source_path: str) -> bool:
        """Install a new plugin from a file."""
        try:
            if not os.path.exists(source_path):
                print(f"Plugin file not found: {source_path}")
                return False

            filename = os.path.basename(source_path)
            if filename == '__init__.py':
                print("Cannot install __init__.py as a plugin")
                return False

            target_path = os.path.join(self.plugin_dir, filename)
            
            # Create plugin directory if it doesn't exist
            os.makedirs(self.plugin_dir, exist_ok=True)

            # Copy plugin file
            import shutil
            shutil.copy2(source_path, target_path)

            # Try to load the plugin
            plugin_name = filename[:-3]
            plugin = self.load_plugin(plugin_name, target_path)
            if plugin:
                self.plugins[plugin_name] = plugin
                return True
            
            # If loading fails, remove the copied file
            os.remove(target_path)
            return False

        except Exception as e:
            print(f"Failed to install plugin: {e}")
            return False

    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin by name."""
        try:
            if plugin_name not in self.plugins:
                return False

            plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
            if os.path.exists(plugin_path):
                os.remove(plugin_path)

            del self.plugins[plugin_name]
            return True

        except Exception as e:
            print(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
