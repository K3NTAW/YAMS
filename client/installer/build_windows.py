import os
import sys
import shutil
import PyInstaller.__main__

def setup_plugins():
    """Setup the plugin system."""
    try:
        # Get the base directory
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extensions", "installed")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create __init__.py files if they don't exist
        init_files = [
            os.path.join(os.path.dirname(plugin_dir), "__init__.py"),
            os.path.join(plugin_dir, "__init__.py")
        ]
        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write("# Plugin package initialization\n")
                    
    except Exception as e:
        print(f"Error setting up plugins: {e}")
        return False
    return True

def build_windows_executable():
    """Build Windows executable using PyInstaller."""
    try:
        # Clean previous builds
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
            
        # Setup plugin system
        if not setup_plugins():
            print("Failed to setup plugin system")
            return False
            
        # Add the src directory to the Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        # PyInstaller arguments
        args = [
            'src/main.py',  # Your main script
            '--name=YAMS',  # Name of the executable
            '--windowed',   # Windows subsystem executable (no console)
            '--icon=assets/icons/app.ico',  # Application icon
            '--add-data=assets;assets',  # Include assets directory
            '--hidden-import=PyQt6.QtCore',
            '--hidden-import=PyQt6.QtGui',
            '--hidden-import=PyQt6.QtWidgets',
            '--hidden-import=websockets',
            '--hidden-import=cryptography',
            '--hidden-import=dotenv',
            # Add directories to include
            '--add-data=extensions;extensions',
            '--add-data=src/core;core',
            '--add-data=src/ui;ui',
            # Exclude unnecessary files
            '--exclude-module=tkinter',
            '--exclude-module=unittest',
            '--clean',  # Clean PyInstaller cache
            '--noconfirm',  # Replace output directory without confirmation
        ]
        
        PyInstaller.__main__.run(args)
        print("Build completed successfully!")
        return True
        
    except Exception as e:
        print(f"Build failed: {e}")
        return False

if __name__ == "__main__":
    success = build_windows_executable()
    sys.exit(0 if success else 1)
