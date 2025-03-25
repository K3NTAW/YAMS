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
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'cryptography',
    'websockets',
    'darkdetect',
    'psutil',
    'yaml',
    'json',
    'asyncio',
    'aiohttp',
    'ssl',
    'logging'
]

# Collect all data files
datas = [
    ('assets/icons/app.svg', 'assets/icons'),
    ('assets/icons/app.icns', 'assets/icons'),
    ('extensions/installed/*.py', 'extensions/installed'),
    ('src/ui/*.py', 'src/ui'),
    ('src/core/*.py', 'src/core'),
    ('src/*.py', 'src'),
]

# Add PyQt6 plugins
qt_plugins = collect_data_files('PyQt6', include_py_files=True)
datas.extend(qt_plugins)

a = Analysis(
    ['src/main.py'],
    pathex=[root_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.Qt3D', 'PyQt6.QtBluetooth', 'PyQt6.QtWebEngine'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unwanted Qt plugins
qt_plugin_filters = [
    'qmltooling',
    'sceneparsers',
    'renderplugins',
    'renderers',
    'qml',
    'webview',
    'sqldrivers',
    'multimedia',
]

binaries_to_keep = []
for binary in a.binaries:
    should_keep = True
    for filter_term in qt_plugin_filters:
        if filter_term in binary[0].lower():
            should_keep = False
            break
    if should_keep:
        binaries_to_keep.append(binary)
a.binaries = binaries_to_keep

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YAMS',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app.icns'
)

app = BUNDLE(
    exe,
    name='YAMS.app',
    icon='assets/icons/app.icns',
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
