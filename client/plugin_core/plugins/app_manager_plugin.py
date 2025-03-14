from plugin_core.plugin_interface import PluginInterface
import subprocess
import os
import psutil
from typing import Dict, Any, List

class AppManagerPlugin(PluginInterface):
    """Plugin for managing applications on the local system."""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin."""
        print("Initializing AppManager plugin")
        return True
    
    def execute(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command.
        
        Supported commands:
        - start_app: Launch an application
        - list_running: List running applications
        - kill_app: Terminate an application
        """
        try:
            if command == "start_app":
                return self._start_application(params.get("path"))
            elif command == "list_running":
                return self._list_running_apps()
            elif command == "kill_app":
                return self._kill_application(params.get("pid"))
            else:
                return {"status": "error", "message": "Unknown command"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _start_application(self, app_path: str) -> Dict[str, Any]:
        """Start an application."""
        if not app_path:
            return {"status": "error", "message": "Application path not provided"}
            
        if not os.path.exists(app_path):
            return {"status": "error", "message": "Application does not exist"}
            
        try:
            # For macOS apps
            if app_path.endswith('.app'):
                subprocess.Popen(['open', app_path])
            else:
                # For regular executables
                subprocess.Popen([app_path])
                
            return {
                "status": "success",
                "message": f"Started application: {app_path}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _list_running_apps(self) -> Dict[str, Any]:
        """List all running applications."""
        try:
            running_apps = []
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    pinfo = proc.info
                    if pinfo['exe']:  # Only include processes with executable paths
                        running_apps.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'path': pinfo['exe'],
                            'cmdline': pinfo['cmdline']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            return {
                "status": "success",
                "apps": running_apps
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _kill_application(self, pid: int) -> Dict[str, Any]:
        """Terminate an application by its PID."""
        if not pid:
            return {"status": "error", "message": "PID not provided"}
            
        try:
            process = psutil.Process(pid)
            process.terminate()
            return {
                "status": "success",
                "message": f"Terminated process with PID: {pid}"
            }
        except psutil.NoSuchProcess:
            return {"status": "error", "message": f"No process found with PID: {pid}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
