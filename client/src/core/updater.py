import os
import sys
import json
import shutil
import tempfile
import requests
import semver
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

class AutoUpdater(QObject):
    update_available = pyqtSignal(str)  # Signal emitted when update is available
    update_progress = pyqtSignal(int)   # Signal emitted during download
    update_error = pyqtSignal(str)      # Signal emitted on error
    
    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = semver.Version.parse(current_version)
        self.update_url = update_url
        self.update_info = None
        
    def check_for_updates(self):
        """Check if a new version is available."""
        try:
            response = requests.get(f"{self.update_url}/latest.json")
            response.raise_for_status()
            
            self.update_info = response.json()
            latest_version = semver.Version.parse(self.update_info['version'])
            
            if latest_version > self.current_version:
                self.update_available.emit(self.update_info['version'])
                return True
        except Exception as e:
            self.update_error.emit(f"Update check failed: {str(e)}")
        return False
    
    def download_update(self):
        """Download and install the update."""
        if not self.update_info:
            self.update_error.emit("No update information available")
            return False
            
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download the update
                response = requests.get(
                    f"{self.update_url}/{self.update_info['filename']}", 
                    stream=True
                )
                response.raise_for_status()
                
                # Get total file size
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                downloaded = 0
                
                # Download path
                download_path = os.path.join(temp_dir, self.update_info['filename'])
                
                # Download the file
                with open(download_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        downloaded += len(data)
                        f.write(data)
                        if total_size:
                            progress = int((downloaded / total_size) * 100)
                            self.update_progress.emit(progress)
                
                # Verify checksum if provided
                if 'checksum' in self.update_info:
                    if not self._verify_checksum(download_path, self.update_info['checksum']):
                        self.update_error.emit("Update file verification failed")
                        return False
                
                # Install the update
                self._install_update(download_path)
                return True
                
        except Exception as e:
            self.update_error.emit(f"Update download failed: {str(e)}")
            return False
    
    def _verify_checksum(self, file_path, expected_checksum):
        """Verify the downloaded file's checksum."""
        import hashlib
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest() == expected_checksum
    
    def _install_update(self, update_path):
        """Install the downloaded update."""
        # Mount the DMG
        import subprocess
        
        try:
            # Mount the DMG
            mount_point = tempfile.mkdtemp()
            subprocess.run(['hdiutil', 'attach', update_path, '-mountpoint', mount_point], check=True)
            
            # Get the app bundle path
            app_name = "YAMS.app"
            mounted_app = os.path.join(mount_point, app_name)
            
            if not os.path.exists(mounted_app):
                raise Exception(f"Could not find {app_name} in the mounted DMG")
            
            # Get the current app's path
            current_app = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Replace the current app with the new version
            if os.path.exists(current_app):
                shutil.rmtree(current_app)
            shutil.copytree(mounted_app, current_app)
            
            # Unmount the DMG
            subprocess.run(['hdiutil', 'detach', mount_point], check=True)
            
            # Show success message
            QMessageBox.information(
                None,
                "Update Successful",
                "The application has been updated successfully. Please restart to apply the changes."
            )
            
        except Exception as e:
            raise Exception(f"Failed to install update: {str(e)}")
        finally:
            # Cleanup
            if os.path.exists(mount_point):
                try:
                    subprocess.run(['hdiutil', 'detach', mount_point], check=True)
                except:
                    pass
                os.rmdir(mount_point)
