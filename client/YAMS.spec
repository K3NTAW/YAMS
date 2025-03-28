# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['/Users/taawake2/projects/personal/YAMS/client/src/main.py'],
    pathex=['/Users/taawake2/projects/personal/YAMS/client'],
    binaries=[],
    datas=[
        ('/Users/taawake2/projects/personal/YAMS/client/src/ui/resources', 'ui/resources'),
        ('/Users/taawake2/projects/personal/YAMS/client/src/extensions', 'extensions'),
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
    hooksconfig={},
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
    icon='/Users/taawake2/projects/personal/YAMS/client/assets/icons/app.icns'
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
    icon='/Users/taawake2/projects/personal/YAMS/client/assets/icons/app.icns',
    bundle_identifier='com.yams.client',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'YAMS',
        'CFBundleDisplayName': 'YAMS',
        'CFBundleIdentifier': 'com.yams.client',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIconFile': 'app.icns',
        'LSMinimumSystemVersion': '10.12.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    }
)
