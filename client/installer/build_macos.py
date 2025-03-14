import os
import sys
import shutil
import plistlib
import py2app.build_app
from setuptools import setup

def setup_plugins():
    """Setup the plugin system."""
    try:
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

def build_macos_app():
    """Build macOS app bundle using py2app."""
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
        src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, src_dir)

        # Create Info.plist data
        info_plist = {
            'CFBundleName': 'YAMS',
            'CFBundleDisplayName': 'YAMS',
            'CFBundleIdentifier': 'com.yams.client',
            'CFBundleVersion': "1.0.0",
            'CFBundleShortVersionString': "1.0.0",
            'CFBundleIconFile': 'app.icns',
            'LSMinimumSystemVersion': "10.12.0",
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        }

        # py2app options
        options = {
            'py2app': {
                'argv_emulation': False,
                'packages': ['PyQt6', 'websockets', 'cryptography', 'dotenv'],
                'includes': ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
                'resources': ['resources', 'extensions'],
                'iconfile': 'resources/app.icns',
                'plist': info_plist,
                'frameworks': [],  # Add any required frameworks
                'excludes': ['tkinter', 'unittest'],
                'strip': True,
                'optimize': 2,
            }
        }

        # Setup configuration
        setup(
            name="YAMS",
            app=['src/main.py'],
            data_files=[],
            options=options,
            setup_requires=['py2app'],
        )

        print("Build completed successfully!")
        
        # Create DMG
        print("Creating DMG installer...")
        os.system(f'dmgbuild -s installer/dmg_settings.py "YAMS" dist/YAMS.dmg')
        
        return True
        
    except Exception as e:
        print(f"Build failed: {e}")
        return False

if __name__ == "__main__":
    success = build_macos_app()
    sys.exit(0 if success else 1)
