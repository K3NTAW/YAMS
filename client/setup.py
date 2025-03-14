from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [
    ('assets/icons', ['assets/icons/app.icns']),
    ('extensions', ['extensions/__init__.py']),
    ('extensions/installed', ['extensions/installed/__init__.py']),
    ('src/extensions', ['src/extensions/__init__.py']),
    ('src/extensions/installed', ['src/extensions/installed/__init__.py'])
]
OPTIONS = {
    'argv_emulation': False,  
    'plist': {
        'CFBundleName': 'YAMS',
        'CFBundleDisplayName': 'YAMS',
        'CFBundleIdentifier': 'com.yams.client',
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'LSMinimumSystemVersion': '10.15',
        'NSHumanReadableCopyright': 'Copyright 2025 YAMS',
        'CFBundleIconFile': 'app.icns'
    },
    'packages': ['PyQt6', 'cryptography', 'websockets', 'dotenv', 'darkdetect', 'psutil'],
    'includes': ['cryptography', 'websockets', 'dotenv', 'darkdetect', 'psutil'],
    'excludes': [],
    'resources': ['assets', 'extensions', 'src/extensions'],
    'iconfile': 'assets/icons/app.icns',
    'strip': True,
    'optimize': 2
}

setup(
    name="yams-desktop",
    version="1.0.0",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    install_requires=[
        "PyQt6",
        "websockets",
        "python-dotenv",
        "cryptography",
        "darkdetect",
        "psutil",
    ],
    entry_points={
        'console_scripts': [
            'yams=src.main:main',
        ],
    }
)
