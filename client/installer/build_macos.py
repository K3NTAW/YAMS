import os
import sys
import json
import subprocess
from datetime import datetime

def setup_plugin_dirs():
    """Set up plugin directories."""
    print("Setting up plugin directories...")
    plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extensions", "installed")
    os.makedirs(plugin_dir, exist_ok=True)
    
    # Create __init__.py files
    init_files = [
        os.path.join(os.path.dirname(plugin_dir), "__init__.py"),
        os.path.join(plugin_dir, "__init__.py")
    ]
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# Plugin package initialization\n")

def build_app():
    """Build the app using py2app."""
    print("Building application bundle...")
    
    # Remove old build artifacts
    if os.path.exists('build'):
        subprocess.run(['rm', '-rf', 'build'])
    if os.path.exists('dist'):
        subprocess.run(['rm', '-rf', 'dist'])
    
    # Build the app
    subprocess.run([
        'python3', 'setup.py', 'py2app',
        '--packages=PyQt6',
        '--includes=cryptography,websockets,dotenv,darkdetect,psutil'
    ], check=True)

def build_dmg():
    """Build the DMG installer."""
    print("Creating DMG installer...")
    
    # DMG settings
    settings = {
        'filename': 'YAMS.dmg',
        'volume_name': 'YAMS Installer',
        'format': 'UDBZ',
        'size': '200M',
        'files': ['dist/YAMS.app'],
        'symlinks': {'Applications': '/Applications'},
        'icon_size': 128,
        'window_rect': ((100, 100), (500, 400)),
        'icon_locations': {
            'YAMS.app': (100, 100),
            'Applications': (400, 100)
        },
        'background': 'assets/images/installer_background.png'
    }
    
    # Create DMG
    import dmgbuild
    dmgbuild.build_dmg(
        'dist/YAMS.dmg',
        'YAMS Installer',
        settings
    )
    
    # Calculate checksum
    import hashlib
    sha256_hash = hashlib.sha256()
    with open('dist/YAMS.dmg', "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    checksum = sha256_hash.hexdigest()
    
    # Create update info file
    with open('dist/latest.json', 'w') as f:
        json.dump({
            'version': get_version(),
            'filename': 'YAMS.dmg',
            'checksum': checksum,
            'release_date': datetime.now().isoformat(),
            'release_notes': 'New version available'
        }, f, indent=2)

def get_version():
    """Get the current version from the client."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from main import __version__
    return __version__

def main():
    try:
        setup_plugin_dirs()
        build_app()
        build_dmg()
        print("Build completed successfully!")
    except Exception as e:
        print(f"Build failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
