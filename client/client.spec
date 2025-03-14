# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['client/client_app.py'],
    pathex=['.'],  # Add current directory to Python path
    binaries=[],
    datas=[
        ('config/servers.json', 'config'),
        ('plugin_core', 'plugin_core'),  # Copy entire plugin_core directory
    ],
    hiddenimports=[
        'websockets',
        'cryptography',
        'dotenv',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'darkdetect',
        'qrainbowstyle',
        'plugin_core',
        'plugin_core.plugin_loader',
        'plugin_core.plugin_interface',
        'plugin_core.plugins',
        'plugin_core.plugins.hello',
        'plugin_core.plugins.wol_plugin'
    ],
    hookspath=['.'],  # Add current directory to hookspath
    hooksconfig={},
    runtime_hooks=['runtime-hook.py'],  # Add our runtime hook
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='device_manager_client',
    debug=True,  # Enable debug mode
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='client',
)
