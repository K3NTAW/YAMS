import os
import sys

# Add plugin_core directory to Python path at runtime
plugin_core_dir = os.path.join(os.path.dirname(sys.argv[0]), 'plugin_core')
if plugin_core_dir not in sys.path:
    sys.path.insert(0, plugin_core_dir)
