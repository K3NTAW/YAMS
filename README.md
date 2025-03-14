# YAMS (Yet Another Management System)

A modern, plugin-based device management system built with Python and PyQt6. Features an extensible plugin architecture that allows users to add custom functionality through a user-friendly interface.

## Features

- 🔌 **Plugin System**: Easily extend functionality through plugins
  - Drag-and-drop plugin installation
  - User-friendly plugin management interface
  - Hot-reload support for plugins

- 🎨 **Modern UI**:
  - Dark/Light theme support
  - System tray integration
  - Responsive design

- 🔒 **Security**:
  - Encrypted communication
  - Plugin validation
  - Secure configuration management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/yams.git
cd yams
```

2. Install dependencies:
```bash
cd client
pip install -r requirements.txt
```

3. Run the application:
```bash
python client/client_app.py
```

## Creating Plugins

Plugins are Python modules that implement the `PluginInterface`. Here's a simple example:

```python
from plugin_core.plugin_interface import PluginInterface

class MyPlugin(PluginInterface):
    def initialize(self, config):
        return True
        
    def execute(self, command, params):
        return {"status": "success", "message": "Command executed"}

def setup_plugin():
    return MyPlugin()
```

### Plugin Installation

1. **Via GUI**:
   - Open the Plugin Manager
   - Drag and drop your .py plugin file
   - Or use the "Install Plugin" button to browse

2. **Manual Installation**:
   - Copy your plugin file to `client/plugin_core/plugins/`
   - Restart the application

## Development

### Requirements
- Python 3.9+
- PyQt6
- Additional dependencies listed in requirements.txt

### Project Structure
```
client/
├── client/           # Core application code
├── plugin_core/      # Plugin system
│   ├── plugins/      # Plugin directory
│   ├── interface.py  # Plugin interface
│   └── loader.py     # Plugin loader
├── requirements.txt  # Dependencies
└── setup.py         # Package configuration
```

### Running Tests
```bash
pytest
```

## Building for Distribution

Build a standalone executable:
```bash
pyinstaller client/client.spec
```

The executable will be created in the `dist` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security Considerations

- Plugins have full Python capabilities when loaded
- No sandboxing is currently implemented
- Review plugin code before installation
- Only install plugins from trusted sources

## License

[MIT License](LICENSE)

## Acknowledgments

- Built with PyQt6
- Uses Python's importlib for plugin loading
- Includes cryptography for secure communication
