from plugin_core.plugin_interface import PluginInterface

class HelloPlugin(PluginInterface):
    """A simple hello world plugin."""
    
    def __init__(self):
        super().__init__()
        self.name = "Hello"
        self.description = "A simple hello world plugin"
        self.version = "1.0.0"
        self.enabled = False
        
    def initialize(self, config):
        """Initialize the plugin."""
        print("Initializing Hello plugin")
        self.enabled = True
        return True
    
    def execute(self, command, params):
        """Execute a command."""
        if not self.enabled:
            return {"status": "error", "message": "Plugin is not enabled"}
            
        if command == "hello":
            return {"message": "Hello from the plugin!"}
        return {"error": "Unknown command"}
        
    def cleanup(self):
        """Clean up any resources used by the plugin."""
        self.enabled = False
        return True
