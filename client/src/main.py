import asyncio
import json
import os
import sys
import websockets
import uuid
import warnings
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

# Suppress macOS TSM warnings
os.environ['QT_MAC_WANTS_LAYER'] = '1'
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Version information
__version__ = "1.0.0"
UPDATE_URL = "https://updates.yams.com"  # Replace with your actual update server

# Add the src directory to the Python path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from extensions.interface import PluginInterface
from extensions.loader import PluginLoader
from extensions.manager import PluginManagerDialog
from ui.main_window import create_gui
from core.updater import AutoUpdater

def setup_plugins():
    """Setup the plugin system."""
    try:
        plugin_dir = os.path.join(src_dir, "extensions", "installed")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create __init__.py files if they don't exist
        init_files = [
            os.path.join(src_dir, "extensions", "__init__.py"),
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
        
        # Initialize auto-updater
        self.updater = AutoUpdater(__version__, UPDATE_URL)
        self.updater.update_available.connect(self.on_update_available)
        self.updater.update_error.connect(lambda msg: print(f"Update error: {msg}"))
        
        # Check for updates periodically
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(3600000)  # Check every hour
        
    def setup_plugin_system(self):
        """Setup the plugin system."""
        try:
            self.plugin_loader = setup_plugins()
        except Exception as e:
            print(f"Error setting up plugin system: {e}")

    def check_for_updates(self):
        """Check for application updates."""
        try:
            self.updater.check_for_updates()
        except Exception as e:
            print(f"Update check failed: {e}")

    def on_update_available(self, version):
        """Handle available updates."""
        reply = QMessageBox.question(
            None,
            "Update Available",
            f"Version {version} is available. Would you like to update now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.updater.download_update()

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
                    print(f"Received message: {data}")
        except Exception as e:
            print(f"Server connection error: {e}")
            return False
        return True

def main():
    try:
        app = QApplication(sys.argv)
        client = DeviceClient()
        app, window = create_gui(client)
        window.show()
        
        # Initial update check
        client.check_for_updates()
        
        return app.exec()
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
