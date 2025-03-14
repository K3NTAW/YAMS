import asyncio
import json
import os
import sys
import websockets
import uuid
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet

# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from plugin_core.plugin_interface import PluginInterface
from plugin_core.plugin_loader import PluginLoader
from client.gui import create_gui

def setup_plugins():
    """Setup the plugin system."""
    try:
        plugin_dir = os.path.join(root_dir, "plugin_core", "plugins")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create __init__.py files if they don't exist
        init_files = [
            os.path.join(root_dir, "plugin_core", "__init__.py"),
            os.path.join(plugin_dir, "__init__.py")
        ]
        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write("# Plugin package initialization\n")

        return PluginLoader(plugin_dir)
    except Exception as e:
        print(f"Error setting up plugins: {e}")
        return None

class DeviceClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Load or generate client configuration
        self.client_id = os.getenv('CLIENT_ID') or str(uuid.uuid4())
        self.client_secret = os.getenv('CLIENT_SECRET') or Fernet.generate_key().decode()
        
        # Load server configuration
        self.server_url = 'ws://localhost:8765'
        
        # Initialize plugin system
        self.setup_plugin_system()
        
    def setup_plugin_system(self):
        """Setup the plugin system."""
        try:
            self.plugin_loader = setup_plugins()
        except Exception as e:
            print(f"Error setting up plugin system: {e}")

def main():
    try:
        client = DeviceClient()
        app, window = create_gui(client)  # Unpack both app and window
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
