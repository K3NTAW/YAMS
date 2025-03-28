import os
import sys
import shutil
import subprocess

def setup_plugins():
    """Setup the plugin system."""
    try:
        # Create plugin directories
        plugin_dirs = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "extensions"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "extensions", "installed"),
        ]
        for plugin_dir in plugin_dirs:
            os.makedirs(plugin_dir, exist_ok=True)
            init_file = os.path.join(plugin_dir, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write("# Plugin package initialization\n")
                    
    except Exception as e:
        print(f"Error setting up plugins: {e}")
        return False
    return True

def build_macos_app():
    """Build macOS app bundle using PyInstaller."""
    try:
        # Clean previous builds
        for dir_to_clean in ['build', 'dist']:
            if os.path.exists(dir_to_clean):
                shutil.rmtree(dir_to_clean)
            
        # Setup plugin system
        if not setup_plugins():
            print("Failed to setup plugin system")
            return False

        # Get absolute paths
        client_dir = os.path.dirname(os.path.dirname(__file__))
        src_dir = os.path.join(client_dir, 'src')
        main_py = os.path.join(src_dir, 'main.py')
        icon_file = os.path.join(client_dir, 'assets', 'icons', 'app.icns')
        resources_dir = os.path.join(src_dir, 'ui', 'resources')
        extensions_dir = os.path.join(src_dir, 'extensions')

        # Create spec file
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_py}'],
    pathex=['{client_dir}'],
    binaries=[],
    datas=[
        ('{resources_dir}', 'ui/resources'),
        ('{extensions_dir}', 'extensions'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'websockets',
        'cryptography',
        'dotenv',
        'darkdetect',
        'psutil',
        'mysql.connector'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['PySide6', 'tkinter', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YAMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_file}'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YAMS'
)

app = BUNDLE(
    coll,
    name='YAMS.app',
    icon='{icon_file}',
    bundle_identifier='com.yams.client',
    version='1.0.0',
    info_plist={{
        'CFBundleName': 'YAMS',
        'CFBundleDisplayName': 'YAMS',
        'CFBundleIdentifier': 'com.yams.client',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIconFile': 'app.icns',
        'LSMinimumSystemVersion': '10.12.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    }}
)
'''

        # Write spec file
        spec_file = os.path.join(client_dir, 'YAMS.spec')
        with open(spec_file, 'w') as f:
            f.write(spec_content)

        # Build command
        cmd = [
            'pyinstaller',
            '--noconfirm',
            '--clean',
            spec_file
        ]

        print("Building app bundle...")
        subprocess.run(cmd, check=True, cwd=client_dir)

        print("Build completed successfully!")
        
        # Create DMG
        print("Creating DMG installer...")
        dmg_settings = os.path.join(os.path.dirname(__file__), 'dmg_settings.py')
        subprocess.run(['dmgbuild', '-s', dmg_settings, 'YAMS', 'dist/YAMS.dmg'], check=True, cwd=client_dir)
        
        return True
        
    except Exception as e:
        print(f"Build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Change to the client directory
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    success = build_macos_app()
    sys.exit(0 if success else 1)
