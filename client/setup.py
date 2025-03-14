from setuptools import setup, find_packages

setup(
    name="plugin-device-mgmt",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
        "websockets",
        "python-dotenv",
        "cryptography",
    ],
    entry_points={
        'console_scripts': [
            'device-manager=client.client_app:main',
        ],
    },
)
