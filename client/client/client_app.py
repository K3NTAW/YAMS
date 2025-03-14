import asyncio
import json
import os
import sys
import websockets
import uuid
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet
from PyQt6.QtWidgets import QApplication

# Add the client directory to the Python path
client_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if client_dir not in sys.path:
    sys.path.insert(0, client_dir)

from plugin_core.plugin_interface import PluginInterface
from plugin_core.plugin_loader import PluginLoader
from plugin_core.plugin_manager_ui import PluginManagerDialog
from client.gui import create_gui

def setup_plugins():
    """Setup the plugin system."""
    try:
        plugin_dir = os.path.join(client_dir, "plugin_core", "plugins")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create __init__.py files if they don't exist
        init_files = [
            os.path.join(client_dir, "plugin_core", "__init__.py"),
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
        self.server_url = os.getenv('SERVER_URL', 'ws://localhost:8765')
        
        # Initialize plugin system
        self.setup_plugin_system()
        
    def setup_plugin_system(self):
        """Setup the plugin system."""
        try:
            self.plugin_loader = setup_plugins()
        except Exception as e:
            print(f"Error setting up plugin system: {e}")

    async def connect_to_server(self):
        """Try to connect to the server."""
        try:
            async with websockets.connect(self.server_url) as websocket:
                # Send initial connection message
                await websocket.send(json.dumps({
                    "type": "connect",
                    "client_id": self.client_id
                }))
                
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    # Handle server messages here
                    print(f"Received message: {data}")
        except Exception as e:
            print(f"Server connection error: {e}")
            return False
        return True

def main():
    try:
        app = QApplication(sys.argv)
        client = DeviceClient()  # Remove offline mode parameter
        app, window = create_gui(client)
        window.show()
        return app.exec()
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
