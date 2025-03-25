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
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QTimer
from client.src.ui.auth_window import LoginWindow

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

from client.src.ui.main_window import MainWindow

def main():
    try:
        app = QApplication(sys.argv)
        
        # Show login window first
        login = LoginWindow()
        if login.exec() == QDialog.DialogCode.Accepted:
            # Only create and show main window after successful login
            window = MainWindow({
                'id': login.user_id,
                'username': login.username,
                'client_id': login.client_id,
                'client_secret': login.client_secret
            })
            window.show()
            return app.exec()
        else:
            return 0  # User closed login window
            
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
