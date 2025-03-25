from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSystemTrayIcon, QMenu,
                             QDialog, QMessageBox, QStackedWidget, QListWidget,
                             QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QTabWidget, QGroupBox, QRadioButton, QLineEdit,
                             QToolBar, QStyle, QCheckBox, QStatusBar, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QAction
from client.src.ui.auth_window import LoginWindow
from client.src.ui.theme import ModernSidebarButton, ModernTabWidget, COLORS
from client.src.core.database import DatabaseManager
import sys
import os
import asyncio

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
        
        # Apply theme from parent window
        if parent and hasattr(parent, 'is_dark_mode'):
            ThemeManager.apply_theme(self, parent.is_dark_mode)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Plugin Manager')
        self.setMinimumSize(400, 300)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.setAcceptDrops(True)
        self.plugin_list.dragEnterEvent = self.dragEnterEvent
        self.plugin_list.dropEvent = self.dropEvent
        layout.addWidget(QLabel("Installed Plugins:"))
        layout.addWidget(self.plugin_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
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
        self.user_id = None
        self.username = None
        self.client_id = None
        self.client_secret = None
        self.db = DatabaseManager()
        self.settings = QSettings('Codeium', 'YAMS')
        self.init_ui()
        self.show_login()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('YAMS')
        self.setMinimumSize(1000, 600)
        
        # Set window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['sidebar']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(8)
        
        # Add logo/title at the top of sidebar
        title_label = QLabel('YAMS')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['primary']};
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }}
        """)
        sidebar_layout.addWidget(title_label)
        
        # Create sidebar buttons
        self.dashboard_btn = ModernSidebarButton('Dashboard')
        self.dashboard_btn.setChecked(True)
        self.devices_btn = ModernSidebarButton('Devices')
        self.plugins_btn = ModernSidebarButton('Plugins')
        self.settings_btn = ModernSidebarButton('Settings')
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.devices_btn)
        sidebar_layout.addWidget(self.plugins_btn)
        sidebar_layout.addWidget(self.settings_btn)
        
        # Add stretch to push profile to bottom
        sidebar_layout.addStretch()
        
        # Add profile button at bottom
        self.profile_btn = ModernSidebarButton('Profile')
        sidebar_layout.addWidget(self.profile_btn)
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['background']};
                padding: 20px;
            }}
        """)
        
        # Create content pages
        self.dashboard_page = ModernTabWidget()
        self.devices_page = ModernTabWidget()
        self.plugins_page = ModernTabWidget()
        self.settings_page = ModernTabWidget()
        self.profile_page = ModernTabWidget()
        
        # Add pages to stack
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.devices_page)
        self.content_stack.addWidget(self.plugins_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.profile_page)
        
        # Connect button signals
        self.dashboard_btn.clicked.connect(lambda: self.show_page(0))
        self.devices_btn.clicked.connect(lambda: self.show_page(1))
        self.plugins_btn.clicked.connect(lambda: self.show_page(2))
        self.settings_btn.clicked.connect(lambda: self.show_page(3))
        self.profile_btn.clicked.connect(lambda: self.show_page(4))
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)
        
        # Initialize system tray
        self.init_tray_icon()
        
        # Start server status check timer
        self.server_status_timer = QTimer()
        self.server_status_timer.timeout.connect(self.check_server_status)
        self.server_status_timer.start(5000)  # Check every 5 seconds
        
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add spacer to push user button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        # Add user button
        self.user_button = QPushButton(self.username or "User")
        self.user_button.setStyleSheet("QPushButton { border: none; padding: 5px 10px; }")
        self.user_button.clicked.connect(self.show_user_menu)
        toolbar.addWidget(self.user_button)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Plugin manager action
        plugin_manager_action = QAction('Plugin Manager', self)
        plugin_manager_action.triggered.connect(self.show_plugin_manager)
        file_menu.addAction(plugin_manager_action)
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.quit_application)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Theme action
        self.theme_action = QAction('Toggle Theme', self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        
        # User menu
        self.user_menu = menubar.addMenu('User')
        self.user_menu.aboutToShow.connect(self.show_user_menu)
        
        # Servers tab
        servers_tab = QWidget()
        servers_layout = QVBoxLayout(servers_tab)
        
        # Server connection group
        connection_group = QGroupBox("Server Connection")
        connection_layout = QVBoxLayout()
        
        # Mode selection
        mode_layout = QHBoxLayout()
        self.auto_radio = QRadioButton("Auto")
        self.manual_radio = QRadioButton("Manual")
        self.auto_radio.setChecked(True)
        mode_layout.addWidget(self.auto_radio)
        mode_layout.addWidget(self.manual_radio)
        connection_layout.addLayout(mode_layout)
        
        # Server URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("Server URL:")
        self.url_input = QLineEdit()
        self.url_input.setReadOnly(True)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        connection_layout.addLayout(url_layout)
        
        connection_group.setLayout(connection_layout)
        servers_layout.addWidget(connection_group)
        
        # Server list
        self.server_list = ServerListWidget()
        self.server_list.itemClicked.connect(self.on_server_selected)
        servers_layout.addWidget(self.server_list)
        
        self.dashboard_page.addTab(servers_tab, "Servers")
        
        # Plugins tab
        plugins_tab = QWidget()
        plugins_layout = QVBoxLayout(plugins_tab)
        
        # Plugin list
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderLabels(["Name", "Version", "Status"])
        plugins_layout.addWidget(self.plugin_tree)
        
        # Plugin buttons
        plugin_buttons = QHBoxLayout()
        manage_plugins_btn = QPushButton("Manage Plugins")
        manage_plugins_btn.clicked.connect(self.show_plugin_manager)
        plugin_buttons.addWidget(manage_plugins_btn)
        plugins_layout.addLayout(plugin_buttons)
        
        self.plugins_page.addTab(plugins_tab, "Plugins")
        
    def show_page(self, index):
        """Show the selected page and update button states."""
        self.content_stack.setCurrentIndex(index)
        
        # Update button states
        for btn in [self.dashboard_btn, self.devices_btn, self.plugins_btn, 
                   self.settings_btn, self.profile_btn]:
            btn.setChecked(False)
        
        # Set the clicked button as checked
        [self.dashboard_btn, self.devices_btn, self.plugins_btn,
         self.settings_btn, self.profile_btn][index].setChecked(True)

    def show_login(self):
        """Show the login window and handle the result."""
        login_window = LoginWindow(self)
        login_window.login_successful.connect(self.on_login_successful)
        if login_window.exec() == QDialog.DialogCode.Accepted:
            self.show()
        else:
            self.quit_application()

    def on_login_successful(self, user_id):
        """Handle successful login."""
        self.user_id = user_id
        user_info = self.db.get_user_info(user_id)
        if user_info:
            self.username = user_info['username']
            self.client_id = user_info['client_id']
            self.client_secret = user_info['client_secret']
        self.user_button.setText(self.username)
        self.init_tray_icon()
        self.update_status()
        self.load_user_data()

    def load_user_data(self):
        """Load user data after successful login."""
        # TODO: Implement loading user data
        pass

    def init_tray_icon(self):
        """Initialize the system tray icon."""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'assets', 'icons', 'app.svg')
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
            quit_action.triggered.connect(self.quit_application)
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

    def quit_application(self):
        """Quit the application cleanly."""
        # Save settings
        self.settings.sync()
        # Hide tray icon
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        # Quit application
        QApplication.instance().quit()

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

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
        self.plugin_tree.clear()
        if hasattr(self.client, 'plugin_loader') and self.client.plugin_loader:
            plugins = self.client.plugin_loader.plugins
            for name, plugin in plugins.items():
                item = QTreeWidgetItem(self.plugin_tree)
                item.setText(0, name)
                item.setText(1, 'Loaded')
                self.plugin_tree.addTopLevelItem(item)

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
        self.status_bar.showMessage(' | '.join(status_parts))

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.settings.setValue('dark_mode', self.is_dark_mode)
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme to the application."""
        ThemeManager.apply_theme(self, self.is_dark_mode)
        
        # Update theme action text
        self.theme_action.setText('Switch to Light Mode' if self.is_dark_mode else 'Switch to Dark Mode')
        self.theme_action.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogHelpButton if self.is_dark_mode 
                else QStyle.StandardPixmap.SP_DialogHelpButton
            )
        )

    def show_user_menu(self):
        """Show the user menu."""
        menu = QMenu(self)
        profile_action = menu.addAction("Profile")
        menu.addSeparator()
        logout_action = menu.addAction("Logout")
        
        # Show menu at button position
        action = menu.exec(self.user_button.mapToGlobal(self.user_button.rect().bottomLeft()))
        
        if action == logout_action:
            self.logout()
        elif action == profile_action:
            self.show_profile()

    def show_profile(self):
        """Show user profile dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle('User Profile')
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # User info
        user_info = self.db.get_user_info(self.user_id)
        if user_info:
            # Username
            username_layout = QHBoxLayout()
            username_label = QLabel('Username:')
            username_value = QLabel(user_info['username'])
            username_layout.addWidget(username_label)
            username_layout.addWidget(username_value)
            layout.addLayout(username_layout)
            
            # Email
            email_layout = QHBoxLayout()
            email_label = QLabel('Email:')
            email_value = QLabel(user_info['email'])
            email_layout.addWidget(email_label)
            email_layout.addWidget(email_value)
            layout.addLayout(email_layout)
            
            # Client ID
            client_id_layout = QHBoxLayout()
            client_id_label = QLabel('Client ID:')
            client_id_value = QLineEdit(user_info['client_id'])
            client_id_value.setReadOnly(True)
            client_id_layout.addWidget(client_id_label)
            client_id_layout.addWidget(client_id_value)
            layout.addLayout(client_id_layout)
            
            # Client Secret
            client_secret_layout = QHBoxLayout()
            client_secret_label = QLabel('Client Secret:')
            client_secret_value = QLineEdit(user_info['client_secret'])
            client_secret_value.setReadOnly(True)
            client_secret_value.setEchoMode(QLineEdit.EchoMode.Password)
            client_secret_layout.addWidget(client_secret_label)
            client_secret_layout.addWidget(client_secret_value)
            layout.addLayout(client_secret_layout)
            
            # Show/Hide secret checkbox
            show_secret = QCheckBox('Show Client Secret')
            show_secret.stateChanged.connect(
                lambda state: client_secret_value.setEchoMode(
                    QLineEdit.EchoMode.Normal if state else QLineEdit.EchoMode.Password
                )
            )
            layout.addWidget(show_secret)
            
            # Account info
            account_info = QLabel(f"""
                <br>
                <b>Account Information:</b><br>
                Created: {user_info['created_at'].strftime('%Y-%m-%d %H:%M:%S')}<br>
                Last Login: {user_info['last_login'].strftime('%Y-%m-%d %H:%M:%S') if user_info['last_login'] else 'Never'}<br>
            """)
            layout.addWidget(account_info)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()

    def logout(self):
        """Handle user logout."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.hide()
            self.user_id = None
            self.username = None
            self.client_id = None
            self.client_secret = None
            self.show_login()

    def on_server_selected(self, item: QListWidgetItem):
        """Handle server selection from the list."""
        if item and self.auto_radio.isChecked():
            url = item.data(Qt.ItemDataRole.UserRole)
            self.url_input.setText(url)
            self.client.server_url = url

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