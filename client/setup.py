from setuptools import setup, find_packages

setup(
    name="yams-client",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.4.0',
        'websockets>=10.4',
        'python-dotenv>=1.0.0',
        'mysql-connector-python>=8.0.32',
        'bcrypt>=4.0.1',
        'darkdetect>=0.8.0',
        'cryptography>=40.0.0',
        'requests>=2.28.0',
        'psutil>=5.9.0',
        'semver>=3.0.0',
    ],
    python_requires='>=3.9',
)
