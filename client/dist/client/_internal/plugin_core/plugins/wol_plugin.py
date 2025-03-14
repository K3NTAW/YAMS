from plugin_core.plugin_interface import PluginInterface
import socket
import struct

class WakeOnLanPlugin(PluginInterface):
    """Plugin for sending Wake-on-LAN magic packets."""
    
    def initialize(self, config):
        """Initialize the plugin."""
        print("Initializing Wake-on-LAN plugin")
        return True
    
    def execute(self, command, params):
        """Execute a command."""
        if command == "wake" and "mac" in params:
            try:
                self.send_magic_packet(params["mac"])
                return {"status": "success", "message": f"Sent WoL packet to {params['mac']}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Invalid command or missing MAC address"}
    
    def send_magic_packet(self, mac_address):
        """Send a Wake-on-LAN magic packet to wake up a computer."""
        # Validate MAC address format
        if len(mac_address.replace(':', '').replace('-', '')) != 12:
            raise ValueError("Invalid MAC address format")
            
        # Convert the MAC address to bytes
        mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
        
        # Create the magic packet
        magic = b'\xff' * 6 + mac_bytes * 16
        
        # Send the packet
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic, ('255.255.255.255', 9))
