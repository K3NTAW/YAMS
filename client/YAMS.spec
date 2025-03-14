# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Add the project root to the Python path
root_dir = os.path.dirname(os.path.abspath(SPECPATH))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Collect all required modules
hidden_imports = [
    'PyQt6.sip',
    'cryptography',
    'websockets',
    'darkdetect',
    'psutil'
] + collect_submodules('plugin_core')

# Collect all data files
datas = [
    ('resources/app.svg', 'resources'),
    ('resources/app.icns', 'resources'),
    ('plugin_core/plugins/*.py', 'plugin_core/plugins'),
]

a = Analysis(
    ['client/client_app.py'],
    pathex=[root_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app.icns'
)

app = BUNDLE(
    exe,
    name='YAMS.app',
    icon='resources/app.icns',
    bundle_identifier='com.yams.client',
    info_plist={
        'LSMinimumSystemVersion': '10.12',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleName': 'YAMS',
        'CFBundleDisplayName': 'YAMS',
        'CFBundleIdentifier': 'com.yams.client',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'NSRequiresAquaSystemAppearance': False,  # Enable dark mode support
    }
)
