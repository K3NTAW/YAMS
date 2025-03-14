import sys
import os
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QSystemTrayIcon, QMenu, QMessageBox,
                            QStatusBar, QTabWidget, QGroupBox, QRadioButton, QLineEdit,
                            QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
                            QDialog, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QAction

class ServerListWidget(QListWidget):
    """Custom list widget that supports drag and drop of server names."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        
        # Add some default servers
        default_servers = {
            "Main Server": "ws://main.yams.com:8765",
            "Backup Server": "ws://backup.yams.com:8765",
            "Development": "ws://dev.yams.com:8765",
            "Local": "ws://localhost:8765"
        }
        
        for name, url in default_servers.items():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.addItem(item)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events for server names."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for server names."""
        text = event.mimeData().text()
        if text:
            item = self.itemAt(event.pos())
            if item:
                url = item.data(Qt.ItemDataRole.UserRole)
                self.parent().url_input.setText(url)
                self.parent().manual_radio.setChecked(False)
                self.parent().auto_radio.setChecked(True)
                self.parent().url_input.setReadOnly(True)

class PluginManagerDialog(QDialog):
    """Dialog for managing plugins with drag-and-drop support."""
    
    plugin_installed = pyqtSignal(str)  # Signal emitted when a plugin is installed
    
    def __init__(self, plugin_dir: str, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Plugin Manager')
        self.setMinimumSize(400, 300)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.setAcceptDrops(True)
        self.plugin_list.dragEnterEvent = self.dragEnterEvent
        self.plugin_list.dropEvent = self.dropEvent
        layout.addWidget(QLabel("Installed Plugins:"))
        layout.addWidget(self.plugin_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        install_btn = QPushButton("Install Plugin")
        install_btn.clicked.connect(self.install_plugin)
        button_layout.addWidget(install_btn)
        
        remove_btn = QPushButton("Remove Plugin")
        remove_btn.clicked.connect(self.remove_plugin)
        button_layout.addWidget(remove_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Load plugins
        self.refresh_plugin_list()
        
    def refresh_plugin_list(self):
        """Refresh the list of installed plugins."""
        self.plugin_list.clear()
        if os.path.exists(self.plugin_dir):
            for item in os.listdir(self.plugin_dir):
                item_path = os.path.join(self.plugin_dir, item)
                if os.path.isfile(item_path) and item.endswith('.py') and item != '__init__.py':
                    item = QListWidgetItem(item)
                    self.plugin_list.addItem(item)
    
    def install_plugin(self):
        """Install a plugin from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Plugin File",
            "",
            "Python Files (*.py)"
        )
        
        if file_path:
            self.install_plugin_file(file_path)
    
    def install_plugin_file(self, file_path: str) -> bool:
        """Install a plugin from the given file path."""
        try:
            filename = os.path.basename(file_path)
            
            # Check if it's __init__.py
            if filename == '__init__.py':
                QMessageBox.warning(
                    self,
                    "Invalid Plugin",
                    "Cannot install __init__.py as a plugin"
                )
                return False
            
            # Check if plugin already exists
            target_path = os.path.join(self.plugin_dir, filename)
            if os.path.exists(target_path):
                reply = QMessageBox.question(
                    self,
                    "Plugin Exists",
                    f"Plugin {filename} already exists. Replace it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return False
            
            # Create plugin directory if needed
            os.makedirs(self.plugin_dir, exist_ok=True)
            
            # Copy plugin file
            import shutil
            shutil.copy2(file_path, target_path)
            
            # Refresh list and emit signal
            self.refresh_plugin_list()
            self.plugin_installed.emit(filename)
            
            QMessageBox.information(
                self,
                "Success",
                f"Plugin {filename} installed successfully"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to install plugin: {str(e)}"
            )
            return False
    
    def remove_plugin(self):
        """Remove the selected plugin."""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            return
            
        filename = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove {filename}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(os.path.join(self.plugin_dir, filename))
                self.refresh_plugin_list()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Plugin {filename} removed successfully"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to remove plugin: {str(e)}"
                )
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for plugin installation."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if isinstance(file_path, str) and file_path.endswith('.py'):
                    event.acceptProposedAction()
                    return
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for plugin installation."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if isinstance(file_path, str) and file_path.endswith('.py'):
                self.install_plugin_file(file_path)

class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()
        self.init_tray_icon()
        self.server_status_timer = QTimer()
        self.server_status_timer.timeout.connect(self.check_server_status)
        self.server_status_timer.start(5000)  # Check every 5 seconds

    def init_tray_icon(self):
        """Initialize the system tray icon."""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'assets', 'icons', 'app.icns')
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(icon_path))
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Show/Hide action
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            # Add separator
            tray_menu.addSeparator()
            
            # Quit action
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(QApplication.instance().quit)
            tray_menu.addAction(quit_action)
            
            # Set the menu
            self.tray_icon.setContextMenu(tray_menu)
            
            # Show icon
            self.tray_icon.show()
            
            # Set window icon
            self.setWindowIcon(QIcon(icon_path))
            
            # Connect double click to show window
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
            
            # Show startup notification
            self.tray_icon.showMessage(
                "YAMS",
                "YAMS is running in the system tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

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
        self.auto_radio.toggled.connect(self.on_mode_changed)
        self.manual_radio.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.auto_radio)
        mode_layout.addWidget(self.manual_radio)
        server_group_layout.addLayout(mode_layout)

        # Server list (only visible in automatic mode)
        self.server_list = ServerListWidget(self)
        self.server_list.itemClicked.connect(self.on_server_selected)
        server_group_layout.addWidget(self.server_list)

        # Server URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Server URL:")
        self.url_input = QLineEdit()
        self.url_input.setText(self.client.server_url)
        self.url_input.setReadOnly(True)  # Initially readonly as automatic mode is default
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
        show_secret_btn = QPushButton("Show Secret")
        show_secret_btn.clicked.connect(self.toggle_secret_visibility)
        secret_layout.addWidget(secret_label)
        secret_layout.addWidget(self.secret_input)
        secret_layout.addWidget(show_secret_btn)
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
        self.manual_radio.setChecked(False)
        self.on_mode_changed()

    def on_mode_changed(self):
        """Handle server mode changes."""
        is_auto = self.auto_radio.isChecked()
        self.server_list.setVisible(is_auto)
        self.url_input.setReadOnly(is_auto)
        if not is_auto:
            self.url_input.clear()
            self.url_input.setPlaceholderText("Enter server URL (e.g., ws://localhost:8765)")
        else:
            # Reset to the first server in the list
            if self.server_list.count() > 0:
                first_item = self.server_list.item(0)
                self.url_input.setText(first_item.data(Qt.ItemDataRole.UserRole))

    def on_server_selected(self, item: QListWidgetItem):
        """Handle server selection from the list."""
        if item and self.auto_radio.isChecked():
            url = item.data(Qt.ItemDataRole.UserRole)
            self.url_input.setText(url)
            self.client.server_url = url

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

    def check_server_status(self):
        """Check server connection status."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            is_connected = loop.run_until_complete(self.client.connect_to_server())
            self.update_status(is_connected)
        finally:
            loop.close()

    def update_status(self, is_connected=False):
        """Update the status bar."""
        status_parts = []
        
        if hasattr(self.client, 'plugin_loader') and self.client.plugin_loader:
            plugins = self.client.plugin_loader.plugins
            status_parts.append(f'Plugins: {len(plugins)}')
        
        status_parts.append(f'Server: {"Online" if is_connected else "Offline"}')
        status_parts.append(f'Server URL: {self.client.server_url}')
        self.statusBar.showMessage(' | '.join(status_parts))

    def toggle_secret_visibility(self):
        """Toggle the visibility of the client secret with warning."""
        if self.secret_input.echoMode() == QLineEdit.EchoMode.Password:
            reply = QMessageBox.warning(
                self,
                "Security Warning",
                "The client secret is sensitive information that should be kept private.\n"
                "Only reveal it if you are in a secure environment.\n\n"
                "Do you want to show the secret?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.secret_input.setEchoMode(QLineEdit.EchoMode.Normal)
                sender = self.sender()
                if sender:
                    sender.setText("Hide Secret")
        else:
            self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
            sender = self.sender()
            if sender:
                sender.setText("Show Secret")

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing."""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            QMessageBox.information(
                self,
                "YAMS",
                "YAMS will keep running in the system tray. To quit the application, "
                "choose 'Quit' in the tray menu."
            )
            self.hide()
            event.ignore()
        else:
            event.accept()

def create_gui(client):
    """Create and return the GUI application and main window."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Set application icon based on platform
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
    if sys.platform == 'darwin':
        icon_path = os.path.join(resources_dir, 'app.icns')
    elif sys.platform == 'win32':
        icon_path = os.path.join(resources_dir, 'app.ico')
    else:  # Linux/Unix
        icon_path = os.path.join(resources_dir, 'app.png')
        
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow(client)
    return app, window