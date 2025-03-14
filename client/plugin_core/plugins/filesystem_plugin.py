from plugin_core.plugin_interface import PluginInterface
import os
import json
from typing import Dict, Any

class FileSystemPlugin(PluginInterface):
    """Plugin for interacting with the local file system."""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin."""
        print("Initializing FileSystem plugin")
        return True
    
    def execute(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command.
        
        Supported commands:
        - list_dir: List contents of a directory
        - get_info: Get information about a file/directory
        """
        try:
            if command == "list_dir":
                return self._list_directory(params.get("path", "."))
            elif command == "get_info":
                return self._get_file_info(params.get("path", "."))
            else:
                return {"status": "error", "message": "Unknown command"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _list_directory(self, path: str) -> Dict[str, Any]:
        """List contents of a directory."""
        if not os.path.exists(path):
            return {"status": "error", "message": "Path does not exist"}
            
        try:
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                items.append({
                    "name": item,
                    "is_dir": os.path.isdir(full_path),
                    "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None
                })
            return {
                "status": "success",
                "items": items,
                "path": path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_file_info(self, path: str) -> Dict[str, Any]:
        """Get detailed information about a file or directory."""
        if not os.path.exists(path):
            return {"status": "error", "message": "Path does not exist"}
            
        try:
            stat = os.stat(path)
            return {
                "status": "success",
                "info": {
                    "name": os.path.basename(path),
                    "path": path,
                    "size": stat.st_size,
                    "is_dir": os.path.isdir(path),
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "accessed": stat.st_atime,
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
