import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSystemTrayIcon, QMenu,
                             QDialog, QMessageBox, QStackedWidget, QListWidget,
                             QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QTabWidget, QGroupBox, QRadioButton, QLineEdit,
                             QToolBar, QStyle, QCheckBox, QStatusBar, QApplication,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings, QMimeData
from PyQt6.QtGui import QIcon, QAction, QDragEnterEvent, QDropEvent
from .auth_window import LoginWindow
from .theme import ModernSidebarButton, ModernTabWidget, COLORS, ThemeManager
from .resources import resources_rc  # Import the compiled resource file
from ..core.database import DatabaseManager
import sys
import asyncio
import websockets
import json
import subprocess

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
    def __init__(self, user_info):
        super().__init__()
        self.server_url = "ws://localhost:8765"
        self.url_input = None  # Initialize as None
        
        # Get the directory containing this module for relative paths
        self.module_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Store user info
        if not user_info:
            raise ValueError("User info is required")
            
        self.user_id = user_info['id']
        self.username = user_info['username']
        self.client_id = user_info['client_id']
        self.client_secret = user_info['client_secret']
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize settings
        self.settings = QSettings('Codeium', 'YAMS')
        self.is_dark_mode = self.settings.value('dark_mode', None)  # None means follow system
        self.start_with_system = self.settings.value('start_with_system', False, type=bool)
        
        self.init_ui()
        
        # Apply theme after UI is initialized
        self.apply_theme()
        
        # Don't show login here, it will be called explicitly
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('YAMS')
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add logo/title at the top
        title_widget = QWidget()
        title_widget.setObjectName("titleWidget")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("YAMS")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Yet Another Management System")
        subtitle_label.setObjectName("subtitleLabel")
        title_layout.addWidget(subtitle_label)
        
        sidebar_layout.addWidget(title_widget)
        
        # Add navigation buttons
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        self.dashboard_btn = ModernSidebarButton("Dashboard", "dashboard")
        self.devices_btn = ModernSidebarButton("Devices", "devices")
        self.plugins_btn = ModernSidebarButton("Plugins", "plugins")
        self.settings_btn = ModernSidebarButton("Settings", "settings")
        self.profile_btn = ModernSidebarButton("Profile", "profile")
        
        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.devices_btn)
        nav_layout.addWidget(self.plugins_btn)
        nav_layout.addWidget(self.settings_btn)
        nav_layout.addWidget(self.profile_btn)
        nav_layout.addStretch()
        
        sidebar_layout.addWidget(nav_widget)
        main_layout.addWidget(sidebar)
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # Create pages
        self.dashboard_page = QWidget()
        self.devices_page = QWidget()
        self.plugins_page = QWidget()
        self.settings_page = QWidget()
        self.profile_page = QWidget()
        
        # Initialize dashboard page
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setContentsMargins(20, 20, 20, 20)
        
        # Server URL input
        url_group = QWidget()
        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_group.setLayout(url_layout)
        
        self.url_input = QLineEdit(self.server_url)
        self.url_input.setPlaceholderText("Server URL (e.g., ws://localhost:8765)")
        self.url_input.setParent(url_group)  # Ensure proper parent-child relationship
        url_layout.addWidget(self.url_input)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.check_server_status)
        connect_btn.setParent(url_group)  # Ensure proper parent-child relationship
        url_layout.addWidget(connect_btn)
        
        dashboard_layout.addWidget(url_group)
        
        # Server list
        self.server_list = ServerListWidget()
        self.server_list.itemClicked.connect(self.on_server_selected)
        dashboard_layout.addWidget(self.server_list)
        
        dashboard_layout.addStretch()
        self.dashboard_page.setLayout(dashboard_layout)
        
        # Initialize devices page
        devices_layout = QVBoxLayout()
        devices_layout.setContentsMargins(20, 20, 20, 20)
        devices_layout.addWidget(QLabel("Devices page - Coming soon"))
        devices_layout.addStretch()
        self.devices_page.setLayout(devices_layout)
        
        # Initialize plugins page
        plugins_layout = QVBoxLayout()
        plugins_layout.setContentsMargins(20, 20, 20, 20)
        
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
        plugins_layout.addStretch()
        
        self.plugins_page.setLayout(plugins_layout)
        
        # Initialize settings page
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(20)
        
        # Theme Settings Section
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout()
        
        # Theme radio buttons
        self.system_theme_radio = QRadioButton("Follow System Theme")
        self.light_theme_radio = QRadioButton("Light Theme")
        self.dark_theme_radio = QRadioButton("Dark Theme")
        
        # Set initial theme selection
        if self.is_dark_mode is None:
            self.system_theme_radio.setChecked(True)
        elif self.is_dark_mode:
            self.dark_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
        
        # Connect theme radio buttons
        self.system_theme_radio.toggled.connect(lambda: self.change_theme(None))
        self.light_theme_radio.toggled.connect(lambda: self.change_theme(False))
        self.dark_theme_radio.toggled.connect(lambda: self.change_theme(True))
        
        theme_layout.addWidget(self.system_theme_radio)
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        
        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)
        
        # Startup Settings Section
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QVBoxLayout()
        
        # Start with system checkbox
        self.start_with_system_cb = QCheckBox("Start when computer starts")
        self.start_with_system_cb.setChecked(self.start_with_system)
        self.start_with_system_cb.stateChanged.connect(self.toggle_start_with_system)
        
        startup_layout.addWidget(self.start_with_system_cb)
        
        startup_group.setLayout(startup_layout)
        settings_layout.addWidget(startup_group)
        
        settings_layout.addStretch()
        self.settings_page.setLayout(settings_layout)
        
        # Initialize profile page
        profile_layout = QVBoxLayout()
        profile_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add a refresh button at the top
        refresh_btn = QPushButton('Refresh Profile')
        refresh_btn.clicked.connect(self.refresh_profile)
        profile_layout.addWidget(refresh_btn)
        
        # Create containers for profile info
        self.profile_info_container = QWidget()
        profile_info_layout = QVBoxLayout()
        self.profile_info_container.setLayout(profile_info_layout)
        profile_layout.addWidget(self.profile_info_container)
        
        # Add logout button at bottom
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout)
        profile_layout.addWidget(logout_btn)
        
        profile_layout.addStretch()
        self.profile_page.setLayout(profile_layout)
        
        # Add pages to content stack
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.devices_page)
        self.content_stack.addWidget(self.plugins_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.profile_page)
        
        main_layout.addWidget(self.content_stack)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected to server")
        
        # Connect buttons to show pages
        self.dashboard_btn.clicked.connect(lambda: self.show_page(0))
        self.devices_btn.clicked.connect(lambda: self.show_page(1))
        self.plugins_btn.clicked.connect(lambda: self.show_page(2))
        self.settings_btn.clicked.connect(lambda: self.show_page(3))
        self.profile_btn.clicked.connect(lambda: self.show_page(4))
        
        # Set stylesheet
        self.setStyleSheet("""
            #sidebar {
                background-color: """ + COLORS['sidebar_bg'] + """;
                border-right: 1px solid """ + COLORS['border'] + """;
            }
            #titleWidget {
                border-bottom: 1px solid """ + COLORS['border'] + """;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: """ + COLORS['text'] + """;
            }
            #subtitleLabel {
                font-size: 12px;
                color: """ + COLORS['text_secondary'] + """;
            }
            #contentStack {
                background-color: """ + COLORS['content_bg'] + """;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid """ + COLORS['border'] + """;
                border-radius: 4px;
                min-width: 300px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: """ + COLORS['primary'] + """;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: """ + COLORS['primary_hover'] + """;
            }
            QStatusBar {
                background-color: """ + COLORS['sidebar_bg'] + """;
                color: """ + COLORS['text'] + """;
                padding: 4px;
                border-top: 1px solid """ + COLORS['border'] + """;
            }
        """)
        
        # Initialize system tray
        self.init_tray_icon()
        
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
        
        self.dashboard_page.setLayout(servers_layout)
        
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
        
        self.plugins_page.setLayout(plugins_layout)
        
        # Initialize settings page
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(20)
        self.settings_page.setLayout(settings_layout)
        
        # Server Management Section
        server_group = QGroupBox("Server Management")
        server_layout = QVBoxLayout()
        
        # Server list
        self.server_list = ServerListWidget()
        server_layout.addWidget(self.server_list)
        
        # Add server section
        add_server_layout = QHBoxLayout()
        self.new_server_name = QLineEdit()
        self.new_server_name.setPlaceholderText("Server Name")
        self.new_server_url = QLineEdit()
        self.new_server_url.setPlaceholderText("Server URL (e.g., ws://localhost:8765)")
        add_server_btn = QPushButton("Add Server")
        add_server_btn.clicked.connect(self.add_server)
        
        add_server_layout.addWidget(self.new_server_name)
        add_server_layout.addWidget(self.new_server_url)
        add_server_layout.addWidget(add_server_btn)
        server_layout.addLayout(add_server_layout)
        
        # Remove server button
        remove_server_btn = QPushButton("Remove Selected Server")
        remove_server_btn.clicked.connect(self.remove_server)
        server_layout.addWidget(remove_server_btn)
        
        server_group.setLayout(server_layout)
        settings_layout.addWidget(server_group)
        
        # Theme Settings Section
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout()
        
        # Theme radio buttons
        self.system_theme_radio = QRadioButton("Follow System Theme")
        self.light_theme_radio = QRadioButton("Light Theme")
        self.dark_theme_radio = QRadioButton("Dark Theme")
        
        # Set initial theme selection
        if self.is_dark_mode is None:
            self.system_theme_radio.setChecked(True)
        elif self.is_dark_mode:
            self.dark_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
        
        # Connect theme radio buttons
        self.system_theme_radio.toggled.connect(lambda: self.change_theme(None))
        self.light_theme_radio.toggled.connect(lambda: self.change_theme(False))
        self.dark_theme_radio.toggled.connect(lambda: self.change_theme(True))
        
        theme_layout.addWidget(self.system_theme_radio)
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        
        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)
        
        # Startup Settings Section
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QVBoxLayout()
        
        # Start with system checkbox
        self.start_with_system_cb = QCheckBox("Start when computer starts")
        self.start_with_system_cb.setChecked(self.start_with_system)
        self.start_with_system_cb.stateChanged.connect(self.toggle_start_with_system)
        
        startup_layout.addWidget(self.start_with_system_cb)
        
        startup_group.setLayout(startup_layout)
        settings_layout.addWidget(startup_group)
        
        settings_layout.addStretch()
    
    def show_page(self, index):
        """Show the selected page and update button states."""
        self.content_stack.setCurrentIndex(index)
        
        # Update button states
        buttons = [self.dashboard_btn, self.devices_btn, self.plugins_btn, 
                  self.settings_btn, self.profile_btn]
        
        # Set the clicked button as checked
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)

    def show_login(self):
        """Show the login window."""
        login_window = LoginWindow()
        result = login_window.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Store user info from login window
            self.user_id = login_window.user_id
            self.username = login_window.username
            self.client_id = login_window.client_id
            self.client_secret = login_window.client_secret
            self.show()  # Only show main window after successful login
        else:
            # Any other result (rejected, closed) should quit the app
            QApplication.quit()

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
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(self.module_dir, 'resources', 'icons', 'tray.svg')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        
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
        if hasattr(self, 'plugin_loader') and self.plugin_loader:
            dialog = PluginManagerDialog(self.plugin_loader.plugin_dir, self)
            if dialog.exec():
                self.refresh_plugin_list()
                self.update_status()
        else:
            QMessageBox.warning(self, "Error", "Plugin system is not available")

    def refresh_plugin_list(self):
        """Refresh the list of installed plugins."""
        self.plugin_tree.clear()
        if hasattr(self, 'plugin_loader') and self.plugin_loader:
            plugins = self.plugin_loader.plugins
            for name, plugin in plugins.items():
                item = QTreeWidgetItem(self.plugin_tree)
                item.setText(0, name)
                item.setText(1, 'Loaded')
                self.plugin_tree.addTopLevelItem(item)

    async def connect_to_server(self):
        """Try to connect to the server."""
        try:
            server_url = self.url_input.text() or self.server_url
            async with websockets.connect(server_url) as websocket:
                # Send initial connection message
                await websocket.send(json.dumps({
                    "type": "connect",
                    "client_id": self.client_id
                }))
                
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"Received message: {data}")
        except Exception as e:
            print(f"Server connection error: {e}")
            return False
        return True

    def check_server_status(self):
        """Check the server connection status."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            is_connected = loop.run_until_complete(self.connect_to_server())
            self.update_status(is_connected)
        except Exception as e:
            print(f"Error checking server status: {e}")
            self.update_status(False)
        finally:
            loop.close()

    def update_status(self, is_connected=False):
        """Update the status bar."""
        try:
            status_parts = []
            
            if hasattr(self, 'plugin_loader') and self.plugin_loader:
                plugins = self.plugin_loader.plugins
                status_parts.append(f'Plugins: {len(plugins)}')
            
            status_parts.append(f'Server: {"Connected" if is_connected else "Disconnected"}')
            
            try:
                server_url = self.server_url
                if hasattr(self, 'url_input') and self.url_input and not self.url_input.isHidden():
                    server_url = self.url_input.text() or server_url
                status_parts.append(f'URL: {server_url}')
            except:
                status_parts.append(f'URL: {self.server_url}')
            
            self.status_bar.showMessage(' | '.join(status_parts))
        except Exception as e:
            print(f"Error updating status: {e}")
            self.status_bar.showMessage("Error updating status")

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
        logout_action = menu.addAction("Logout")
        
        # Show menu at button position
        action = menu.exec(self.user_button.mapToGlobal(self.user_button.rect().bottomLeft()))
        
        if action == logout_action:
            self.logout()

    def show_profile(self):
        """Show user profile by switching to profile page."""
        self.content_stack.setCurrentWidget(self.profile_page)
        self.refresh_profile()  # Refresh profile info when showing the page

    def refresh_profile(self):
        """Refresh the profile page with latest user info."""
        # Clear existing profile info
        layout = self.profile_info_container.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add user info
        layout.addWidget(QLabel(f"User ID: {self.user_id}"))
        layout.addWidget(QLabel(f"Username: {self.username}"))
        layout.addWidget(QLabel(f"Client ID: {self.client_id}"))

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

    def on_server_selected(self, item):
        """Handle server selection."""
        if item:
            self.server_url = item.text()
            self.url_input.setText(self.server_url)
            self.check_server_status()

    def add_server(self):
        """Add a new server to the list."""
        name = self.new_server_name.text().strip()
        url = self.new_server_url.text().strip()
        
        if not name or not url:
            QMessageBox.warning(self, "Error", "Please enter both server name and URL")
            return
            
        # Add to list
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, url)
        self.server_list.addItem(item)
        
        # Clear inputs
        self.new_server_name.clear()
        self.new_server_url.clear()
        
        # Save to settings
        self.save_servers()
    
    def remove_server(self):
        """Remove the selected server from the list."""
        current_item = self.server_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a server to remove")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove the server '{current_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.server_list.takeItem(self.server_list.row(current_item))
            self.save_servers()
    
    def save_servers(self):
        """Save the current server list to settings."""
        servers = {}
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            servers[item.text()] = item.data(Qt.ItemDataRole.UserRole)
        self.settings.setValue('servers', servers)
    
    def load_servers(self):
        """Load servers from settings."""
        self.server_list.clear()
        servers = self.settings.value('servers', {})
        for name, url in servers.items():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.server_list.addItem(item)
    
    def change_theme(self, is_dark_mode):
        """Change the application theme."""
        if self.is_dark_mode != is_dark_mode:
            self.is_dark_mode = is_dark_mode
            self.settings.setValue('dark_mode', is_dark_mode)
            self.apply_theme()
    
    def toggle_start_with_system(self, state):
        """Toggle whether the application starts with the system."""
        try:
            if sys.platform == 'darwin':
                app_path = os.path.abspath(sys.argv[0])
                script = f'''
                tell application "System Events"
                    try
                        delete login item "YAMS"
                    end try
                    {f'make login item at end with properties {{name:"YAMS", path:"{app_path}", hidden:false}}' if state else ''}
                end tell
                '''
                subprocess.run(['osascript', '-e', script], check=False)
            
            self.start_with_system = bool(state)
            self.settings.setValue('start_with_system', self.start_with_system)
            self.settings.sync()
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not {'' if state else 'remove '} startup item: {str(e)}")
    
    def on_theme_changed(self, theme):
        """Handle theme change from settings."""
        if theme == 'system':
            self.is_dark_mode = None
        else:
            self.is_dark_mode = theme == 'dark'
        
        self.settings.setValue('dark_mode', self.is_dark_mode)
        self.apply_theme()

def create_gui():
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
    
    window = MainWindow(None)
    return app, window