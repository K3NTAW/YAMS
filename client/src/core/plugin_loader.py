import os
import sys
import importlib.util
import shutil
from typing import Dict, Any, Optional
from PyQt6.QtCore import QSettings

class PluginLoader:
    """Handles loading and managing plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugin_directories = set()
        self.settings = QSettings('Codeium', 'YAMS')
        
    def add_plugin_directory(self, directory: str) -> None:
        """Add a directory to search for plugins."""
        if os.path.isdir(directory):
            self.plugin_directories.add(directory)
            # Add to Python path if not already there
            if directory not in sys.path:
                sys.path.append(directory)
    
    def load_plugins(self) -> None:
        """Load all plugins from registered directories."""
        # Clear existing plugins
        for plugin in self.plugins.values():
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
        self.plugins.clear()
        
        # Clear module cache for plugins
        for module_name in list(sys.modules.keys()):
            if any(directory in str(sys.modules[module_name]) for directory in self.plugin_directories):
                del sys.modules[module_name]
        
        # Reload all plugins
        for directory in self.plugin_directories:
            self._load_plugins_from_directory(directory)
            
        # Set active states from settings
        for plugin_name, plugin in self.plugins.items():
            active = self.settings.value(f'plugins/{plugin_name}/active', True, type=bool)
            if hasattr(plugin, '_active'):
                plugin._active = active
    
    def _load_plugins_from_directory(self, directory: str) -> None:
        """Load plugins from a specific directory."""
        try:
            # Look for Python files that might be plugins
            for filename in os.listdir(directory):
                if filename.endswith('.py') and not filename.startswith('__'):
                    plugin_path = os.path.join(directory, filename)
                    self._load_plugin_from_file(plugin_path)
        except Exception as e:
            print(f"Error loading plugins from {directory}: {e}")
    
    def _load_plugin_from_file(self, plugin_path: str) -> None:
        """Load a plugin from a specific file."""
        try:
            # Get module name from filename
            module_name = os.path.splitext(os.path.basename(plugin_path))[0]
            
            # Load module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                print(f"Failed to load spec for {plugin_path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for plugin class
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    hasattr(item, 'initialize') and 
                    hasattr(item, 'cleanup') and
                    hasattr(item, 'is_active') and
                    hasattr(item, 'get_commands') and
                    hasattr(item, 'execute_command') and
                    hasattr(item, 'get_metadata')):
                    
                    # Create plugin instance
                    plugin = item()
                    metadata = plugin.get_metadata()
                    plugin_name = metadata.get('name', item_name)
                    
                    # Store plugin
                    self.plugins[plugin_name] = plugin
                    print(f"Loaded plugin: {plugin_name}")
                    break
            
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def execute_command(self, plugin_name: str, command: str, *args, **kwargs) -> bool:
        """Execute a command on a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin and hasattr(plugin, 'is_active') and plugin.is_active():
            return plugin.execute_command(command, *args, **kwargs)
        return False
    
    def set_plugin_active(self, plugin_name: str, active: bool) -> bool:
        """Set a plugin's active state."""
        plugin = self.plugins.get(plugin_name)
        if plugin and hasattr(plugin, '_active'):
            # Save state to settings
            self.settings.setValue(f'plugins/{plugin_name}/active', active)
            self.settings.sync()  # Force save settings
            
            # Update plugin state
            plugin._active = active
            return True
        return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin by name."""
        try:
            # Find the plugin file
            plugin = self.plugins.get(plugin_name)
            if not plugin:
                return False
                
            for directory in self.plugin_directories:
                module_name = plugin.__class__.__module__
                expected_file = f"{module_name}.py"
                plugin_path = os.path.join(directory, expected_file)
                
                if os.path.exists(plugin_path):
                    # Cleanup plugin
                    if hasattr(plugin, 'cleanup'):
                        plugin.cleanup()
                    
                    # Remove from plugins dict
                    del self.plugins[plugin_name]
                    
                    # Remove module from sys.modules
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                    
                    # Remove the file
                    os.remove(plugin_path)
                    return True
            return False
        except Exception as e:
            print(f"Error uninstalling plugin {plugin_name}: {e}")
            return False
            
    def install_plugin(self, source_path: str, target_directory: str) -> bool:
        """Install a plugin from source path to target directory."""
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_directory, exist_ok=True)
            
            # Copy plugin file
            filename = os.path.basename(source_path)
            target_path = os.path.join(target_directory, filename)
            
            shutil.copy2(source_path, target_path)
            
            # Add directory to plugin directories if not already added
            self.add_plugin_directory(target_directory)
            
            # Reload plugins
            self.load_plugins()
            return True
        except Exception as e:
            print(f"Error installing plugin from {source_path}: {e}")
            return False
