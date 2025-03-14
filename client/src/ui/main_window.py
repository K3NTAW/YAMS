import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QSystemTrayIcon, QMenu, QMessageBox,
                            QStatusBar, QTabWidget, QGroupBox, QRadioButton, QLineEdit,
                            QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from extensions.manager import PluginManagerDialog

class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()
        self.server_status_timer = QTimer()
        self.server_status_timer.timeout.connect(self.check_server_status)
        self.server_status_timer.start(5000)  # Check every 5 seconds

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('YAMS Device Manager')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Plugin Manager tab
        plugin_tab = QWidget()
        plugin_layout = QVBoxLayout(plugin_tab)
        
        # Plugin manager button
        manage_plugins_btn = QPushButton('Manage Plugins', self)
        manage_plugins_btn.clicked.connect(self.show_plugin_manager)
        plugin_layout.addWidget(manage_plugins_btn)

        # Plugin list
        self.plugin_list = QTreeWidget()
        self.plugin_list.setHeaderLabels(['Plugin', 'Status'])
        self.refresh_plugin_list()
        plugin_layout.addWidget(self.plugin_list)
        
        tabs.addTab(plugin_tab, "Plugins")

        # Server tab
        server_tab = QWidget()
        server_layout = QVBoxLayout(server_tab)

        # Server Configuration
        server_group = QGroupBox("Server Configuration")
        server_group_layout = QVBoxLayout()

        # Connection mode
        mode_layout = QHBoxLayout()
        self.auto_radio = QRadioButton("Automatic")
        self.manual_radio = QRadioButton("Manual")
        mode_layout.addWidget(self.auto_radio)
        mode_layout.addWidget(self.manual_radio)
        server_group_layout.addLayout(mode_layout)

        # Server URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Server URL:")
        self.url_input = QLineEdit()
        self.url_input.setText(self.client.server_url)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        server_group_layout.addLayout(url_layout)

        # Client Configuration
        client_group = QGroupBox("Client Configuration")
        client_layout = QVBoxLayout()

        # Client ID
        id_layout = QHBoxLayout()
        id_label = QLabel("Client ID:")
        self.id_input = QLineEdit()
        self.id_input.setText(self.client.client_id)
        self.id_input.setReadOnly(True)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        client_layout.addLayout(id_layout)

        # Client Secret
        secret_layout = QHBoxLayout()
        secret_label = QLabel("Client Secret:")
        self.secret_input = QLineEdit()
        self.secret_input.setText(self.client.client_secret)
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        secret_layout.addWidget(secret_label)
        secret_layout.addWidget(self.secret_input)
        client_layout.addLayout(secret_layout)

        client_group.setLayout(client_layout)
        server_group.setLayout(server_group_layout)

        server_layout.addWidget(server_group)
        server_layout.addWidget(client_group)
        server_layout.addStretch()

        tabs.addTab(server_tab, "Server")

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status()

        # Set initial server mode
        self.auto_radio.setChecked(True)

    def show_plugin_manager(self):
        """Show the plugin manager dialog."""
        if hasattr(self.client, 'plugin_loader') and self.client.plugin_loader:
            dialog = PluginManagerDialog(self.client.plugin_loader.plugin_dir, self)
            if dialog.exec():
                self.refresh_plugin_list()
                self.update_status()
        else:
            QMessageBox.warning(self, "Error", "Plugin system is not available")

    def refresh_plugin_list(self):
        """Refresh the list of installed plugins."""
        self.plugin_list.clear()
        if hasattr(self.client, 'plugin_loader') and self.client.plugin_loader:
            plugins = self.client.plugin_loader.plugins
            for name, plugin in plugins.items():
                item = QTreeWidgetItem(self.plugin_list)
                item.setText(0, name)
                item.setText(1, 'Loaded')
                self.plugin_list.addTopLevelItem(item)

    async def check_server_status(self):
        """Check server connection status."""
        is_connected = await self.client.connect_to_server()
        self.update_status(is_connected)

    def update_status(self, is_connected=False):
        """Update the status bar."""
        status_parts = []
        
        if hasattr(self.client, 'plugin_loader') and self.client.plugin_loader:
            plugins = self.client.plugin_loader.plugins
            status_parts.append(f'Plugins: {len(plugins)}')
        
        status_parts.append(f'Server: {"Online" if is_connected else "Offline"}')
        status_parts.append(f'Server URL: {self.client.server_url}')
        self.statusBar.showMessage(' | '.join(status_parts))

def create_gui(client):
    """Create and return the GUI application and main window."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'app.icns')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow(client)
    return app, window