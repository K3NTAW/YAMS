import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSystemTrayIcon, QMenu,
                             QDialog, QMessageBox, QStackedWidget, QListWidget,
                             QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QTabWidget, QGroupBox, QRadioButton, QLineEdit,
                             QToolBar, QStyle, QCheckBox, QStatusBar, QApplication,
                             QSizePolicy, QComboBox, QButtonGroup, QFileDialog)
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
from ..core.plugin_loader import PluginLoader
from .plugin_manager import PluginManagerDialog
import darkdetect

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
    
    def __init__(self, plugin_loader, plugin_dir: str, parent=None):
        super().__init__(parent)
        self.plugin_loader = plugin_loader
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
        
        # Initialize plugin system
        self.plugin_loader = PluginLoader()
        
        # Set up UI
        self.init_ui()
        
        # Initialize plugins
        self.init_plugins()
        
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
        
        self.dashboard_btn = ModernSidebarButton("Dashboard", "dashboard", self.is_dark_mode)
        self.devices_btn = ModernSidebarButton("Devices", "devices", self.is_dark_mode)
        self.plugins_btn = ModernSidebarButton("Plugins", "plugins", self.is_dark_mode)
        self.settings_btn = ModernSidebarButton("Settings", "settings", self.is_dark_mode)
        self.profile_btn = ModernSidebarButton("Profile", "profile", self.is_dark_mode)
        
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
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setContentsMargins(20, 20, 20, 20)
        dashboard_layout.setSpacing(15)
        dashboard_layout.addStretch()
        self.dashboard_page.setLayout(dashboard_layout)

        # Initialize devices page
        devices_layout = QVBoxLayout()
        devices_layout.setContentsMargins(20, 20, 20, 20)
        devices_layout.setSpacing(15)
        devices_layout.addStretch()
        self.devices_page = QWidget()
        self.devices_page.setLayout(devices_layout)

        # Initialize plugins page
        plugins_layout = QVBoxLayout()
        plugins_layout.setContentsMargins(20, 20, 20, 20)
        plugins_layout.setSpacing(15)

        # Plugin Overview
        plugin_overview = QGroupBox("Plugin Overview")
        plugin_overview.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        plugin_layout = QVBoxLayout()
        plugin_layout.setSpacing(10)

        # Active Plugins Section
        active_plugins = QGroupBox("Active Plugins")
        active_plugins.setStyleSheet("QGroupBox { font-weight: normal; }")
        active_layout = QVBoxLayout()
        self.active_plugins_list = QListWidget()
        self.active_plugins_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 255, 0, 0.1);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        active_layout.addWidget(self.active_plugins_list)
        active_plugins.setLayout(active_layout)
        plugin_layout.addWidget(active_plugins)

        # Inactive Plugins Section
        inactive_plugins = QGroupBox("Inactive Plugins")
        inactive_plugins.setStyleSheet("QGroupBox { font-weight: normal; }")
        inactive_layout = QVBoxLayout()
        self.inactive_plugins_list = QListWidget()
        self.inactive_plugins_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(128, 128, 128, 0.1);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        inactive_layout.addWidget(self.inactive_plugins_list)
        inactive_plugins.setLayout(inactive_layout)
        plugin_layout.addWidget(inactive_plugins)

        # Plugin Stats
        stats_layout = QHBoxLayout()
        self.total_plugins_label = QLabel("Total Plugins: 0")
        self.active_count_label = QLabel("Active: 0")
        self.commands_count_label = QLabel("Available Commands: 0")
        
        for label in [self.total_plugins_label, self.active_count_label, self.commands_count_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 0, 0, 0.1);
                    padding: 5px 10px;
                    border-radius: 3px;
                }
            """)
            stats_layout.addWidget(label)
        
        plugin_layout.addLayout(stats_layout)
        plugin_overview.setLayout(plugin_layout)
        plugins_layout.addWidget(plugin_overview)

        # Plugin Actions
        actions_layout = QHBoxLayout()
        manage_plugins_btn = QPushButton("Manage Plugins")
        manage_plugins_btn.clicked.connect(self.show_plugin_manager)
        manage_plugins_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #007AFF;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        actions_layout.addWidget(manage_plugins_btn)
        actions_layout.addStretch()
        plugins_layout.addLayout(actions_layout)
        
        plugins_layout.addStretch()
        
        self.plugins_page = QWidget()
        self.plugins_page.setLayout(plugins_layout)
        
        # Add pages to content stack
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.devices_page)
        self.content_stack.addWidget(self.plugins_page)
        self.settings_page = self.init_settings_page()
        self.content_stack.addWidget(self.settings_page)
        self.profile_page = self.init_profile_page()
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
            QMainWindow {
                background-color: """ + ('#2E2E2E' if self.is_dark_mode else '#FFFFFF') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QWidget {
                background-color: """ + ('#2E2E2E' if self.is_dark_mode else '#FFFFFF') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QMenuBar {
                background-color: """ + ('#1E1E1E' if self.is_dark_mode else '#F0F0F0') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QMenuBar::item:selected {
                background-color: """ + ('#404040' if self.is_dark_mode else '#E0E0E0') + """;
            }
            QMenu {
                background-color: """ + ('#2E2E2E' if self.is_dark_mode else '#FFFFFF') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QMenu::item:selected {
                background-color: """ + ('#404040' if self.is_dark_mode else '#E0E0E0') + """;
            }
            QPushButton {
                background-color: """ + ('#404040' if self.is_dark_mode else '#F0F0F0') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: """ + ('#505050' if self.is_dark_mode else '#E0E0E0') + """;
            }
            QPushButton:pressed {
                background-color: """ + ('#303030' if self.is_dark_mode else '#D0D0D0') + """;
            }
            QLineEdit {
                background-color: """ + ('#404040' if self.is_dark_mode else '#FFFFFF') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
                border: 1px solid """ + ('#505050' if self.is_dark_mode else '#C0C0C0') + """;
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget {
                background-color: """ + ('#404040' if self.is_dark_mode else '#FFFFFF') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
                border: 1px solid """ + ('#505050' if self.is_dark_mode else '#C0C0C0') + """;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: """ + ('#505050' if self.is_dark_mode else '#E0E0E0') + """;
            }
            QTreeWidget {
                background-color: """ + ('#404040' if self.is_dark_mode else '#FFFFFF') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
                border: 1px solid """ + ('#505050' if self.is_dark_mode else '#C0C0C0') + """;
                border-radius: 3px;
            }
            QTreeWidget::item:selected {
                background-color: """ + ('#505050' if self.is_dark_mode else '#E0E0E0') + """;
            }
            QStatusBar {
                background-color: """ + ('#1E1E1E' if self.is_dark_mode else '#F0F0F0') + """;
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QLabel {
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QGroupBox {
                border: 1px solid """ + ('#505050' if self.is_dark_mode else '#C0C0C0') + """;
                border-radius: 3px;
                margin-top: 0.5em;
                padding-top: 0.5em;
            }
            QGroupBox::title {
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QRadioButton {
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            QCheckBox {
                color: """ + ('#FFFFFF' if self.is_dark_mode else '#000000') + """;
            }
            #sidebar {
                background-color: """ + ('#1E1E1E' if self.is_dark_mode else '#F0F0F0') + """;
                border-right: 1px solid """ + ('#505050' if self.is_dark_mode else '#C0C0C0') + """;
            }
            #contentStack {
                background-color: """ + ('#2E2E2E' if self.is_dark_mode else '#FFFFFF') + """;
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
    
    def init_settings_page(self):
        """Initialize the settings page."""
        settings_page = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(15)

        # Settings header
        settings_title = QLabel("Settings")
        settings_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        settings_layout.addWidget(settings_title)

        # Server Settings Group
        server_group = QGroupBox("Server Settings")
        server_layout = QVBoxLayout()
        server_group.setLayout(server_layout)

        # Server Selection
        server_selection_layout = QHBoxLayout()
        server_label = QLabel("Server:")
        self.server_combo = QComboBox()
        self.server_combo.addItems(["Production", "Development", "Custom"])
        server_selection_layout.addWidget(server_label)
        server_selection_layout.addWidget(self.server_combo)
        server_selection_layout.addStretch()
        server_layout.addLayout(server_selection_layout)

        # URL Mode Selection
        url_mode_layout = QHBoxLayout()
        url_mode_label = QLabel("URL Mode:")
        self.url_mode_group = QButtonGroup()
        auto_radio = QRadioButton("Automatic")
        manual_radio = QRadioButton("Manual")
        self.url_mode_group.addButton(auto_radio, 0)
        self.url_mode_group.addButton(manual_radio, 1)
        auto_radio.setChecked(True)
        url_mode_layout.addWidget(url_mode_label)
        url_mode_layout.addWidget(auto_radio)
        url_mode_layout.addWidget(manual_radio)
        url_mode_layout.addStretch()
        server_layout.addLayout(url_mode_layout)

        # Manual URL Input
        url_input_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter server URL...")
        self.url_input.setEnabled(False)  # Disabled by default in automatic mode
        url_input_layout.addWidget(url_label)
        url_input_layout.addWidget(self.url_input)
        server_layout.addLayout(url_input_layout)

        # Add server group to settings
        settings_layout.addWidget(server_group)

        # Theme Settings Group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)

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

        settings_layout.addWidget(theme_group)

        # Startup Settings Group
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QVBoxLayout()
        startup_group.setLayout(startup_layout)

        # Start with system checkbox
        self.start_with_system_cb = QCheckBox("Start when computer starts")
        self.start_with_system_cb.setChecked(self.start_with_system)
        self.start_with_system_cb.stateChanged.connect(self.toggle_start_with_system)

        startup_layout.addWidget(self.start_with_system_cb)

        settings_layout.addWidget(startup_group)
        settings_layout.addStretch()

        # Save Button
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        settings_layout.addWidget(save_btn)

        # Connect signals
        self.url_mode_group.buttonClicked.connect(self.on_url_mode_changed)
        self.server_combo.currentTextChanged.connect(self.on_server_changed)
        save_btn.clicked.connect(self.save_settings)

        settings_page.setLayout(settings_layout)
        return settings_page

    def on_url_mode_changed(self, button):
        """Handle URL mode change."""
        is_manual = self.url_mode_group.checkedId() == 1
        self.url_input.setEnabled(is_manual)
        if not is_manual:
            self.update_automatic_url()

    def on_server_changed(self, server):
        """Handle server selection change."""
        if self.url_mode_group.checkedId() == 0:  # Automatic mode
            self.update_automatic_url()

    def update_automatic_url(self):
        """Update URL based on selected server in automatic mode."""
        server = self.server_combo.currentText()
        if server == "Production":
            url = "https://api.yams.example.com"
        elif server == "Development":
            url = "http://localhost:8000"
        else:  # Custom
            url = ""
        self.url_input.setText(url)

    def save_settings(self):
        """Save the current settings."""
        settings = {
            'server': self.server_combo.currentText(),
            'url_mode': 'manual' if self.url_mode_group.checkedId() == 1 else 'automatic',
            'url': self.url_input.text(),
            'theme': 'system' if self.system_theme_radio.isChecked() else 
                    'dark' if self.dark_theme_radio.isChecked() else 'light',
            'start_with_system': self.start_with_system_cb.isChecked()
        }
        
        # Save settings to database or config file
        print("Saving settings:", settings)  # For now just print
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully!")

    def init_profile_page(self):
        """Initialize the profile page."""
        print("Initializing profile page...")  # Debug print
        
        profile_page = QWidget()
        profile_layout = QVBoxLayout()
        profile_layout.setContentsMargins(20, 20, 20, 20)
        profile_layout.setSpacing(15)
        
        # Profile header
        profile_title = QLabel("Your Profile")
        profile_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        profile_layout.addWidget(profile_title)
        
        # Create fields
        fields = [
            ("Username", "username"),
            ("User ID", "user_id"),
            ("Client ID", "client_id"),
            ("Client Secret", "client_secret")
        ]
        
        print("Creating profile fields...")  # Debug print
        self.info_labels = {}
        for label_text, field_name in fields:
            group = QGroupBox(label_text)
            group_layout = QHBoxLayout()
            group.setLayout(group_layout)
            
            label = QLabel()
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setWordWrap(True)
            group_layout.addWidget(label)
            
            profile_layout.addWidget(group)
            self.info_labels[field_name] = label
            print(f"Created label for {field_name}")  # Debug print
        
        profile_layout.addStretch()
        
        # Add logout button at bottom
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        profile_layout.addWidget(logout_btn)
        
        profile_page.setLayout(profile_layout)
        print("Profile page initialization complete")  # Debug print
        return profile_page

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
        print("Opening login window...")  # Debug print
        login_window = LoginWindow(self)
        
        if login_window.exec() == QDialog.DialogCode.Rejected:
            print("Login window rejected, quitting...")  # Debug print
            QApplication.quit()
            
        # Get user info directly from database
        db = DatabaseManager()
        user_info = db.get_user_info(1)  # Hardcode to user ID 1 for now
        
        if user_info:
            print("Got user info from database:", user_info)  # Debug print
            self.username = user_info['username']
            self.user_id = 1  # Hardcode for now
            self.client_id = user_info['client_id']
            self.client_secret = user_info['client_secret']
            
            # Update UI
            self.user_button.setText(self.username)
            self.init_tray_icon()
            self.update_status()
            
            # Show the main window
            self.show()
            self.activateWindow()
            
            # Show profile
            self.show_profile()
        else:
            print("Failed to get user info from database")  # Debug print
            QMessageBox.warning(self, 'Error', 'Could not load user information')
            QApplication.quit()

    def refresh_profile(self):
        """Refresh the profile page with latest user info."""
        print("Refreshing profile...")  # Debug print
        
        if not hasattr(self, 'info_labels'):
            print("Warning: info_labels not initialized")
            return
            
        # Update all labels with user info
        print("Current user info:", {
            'username': getattr(self, 'username', None),
            'user_id': getattr(self, 'user_id', None),
            'client_id': getattr(self, 'client_id', None),
            'client_secret': getattr(self, 'client_secret', None)
        })
        
        for field_name in ['username', 'user_id', 'client_id', 'client_secret']:
            if self.info_labels.get(field_name):
                value = getattr(self, field_name, '')
                self.info_labels[field_name].setText(str(value or ''))
                print(f"Updated {field_name} label with value: {value}")
            else:
                print(f"Warning: {field_name} label not found")

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
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extensions")
        dialog = PluginManagerDialog(self.plugin_loader, plugin_dir, parent=self)
        dialog.exec()  # We want to update regardless of dialog result
        self.plugin_loader.load_plugins()  # Force reload all plugins
        self.update_plugin_lists()

    def update_plugin_lists(self):
        """Update the active and inactive plugin lists"""
        self.active_plugins_list.clear()
        self.inactive_plugins_list.clear()
        
        if not hasattr(self, 'plugin_loader'):
            return
            
        active_count = 0
        command_count = 0
        
        for plugin_name, plugin in self.plugin_loader.plugins.items():
            # Skip system plugins
            if plugin_name == "loader":
                continue
                
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(5, 5, 5, 5)
            
            name_label = QLabel(plugin_name)
            layout.addWidget(name_label)
            
            if plugin.is_active():
                status_label = QLabel("Active")
                status_label.setStyleSheet("color: green;")
                active_count += 1
                command_count += len(plugin.get_commands())
                self.active_plugins_list.addItem(item)
            else:
                status_label = QLabel("Inactive")
                status_label.setStyleSheet("color: gray;")
                self.inactive_plugins_list.addItem(item)
                
            layout.addWidget(status_label)
            layout.addStretch()
            
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            
            if plugin.is_active():
                self.active_plugins_list.setItemWidget(item, widget)
            else:
                self.inactive_plugins_list.setItemWidget(item, widget)
        
        total_plugins = len([p for p in self.plugin_loader.plugins if p != "loader"])
        self.total_plugins_label.setText(f"Total Plugins: {total_plugins}")
        self.active_count_label.setText(f"Active: {active_count}")
        self.commands_count_label.setText(f"Available Commands: {command_count}")

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
        
        # Update sidebar buttons
        self.dashboard_btn.update_theme(self.is_dark_mode)
        self.devices_btn.update_theme(self.is_dark_mode)
        self.plugins_btn.update_theme(self.is_dark_mode)
        self.settings_btn.update_theme(self.is_dark_mode)
        self.profile_btn.update_theme(self.is_dark_mode)

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
        self.show_page(4)  # Index 4 is the profile page
        self.refresh_profile()

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

    def init_plugins(self):
        """Initialize the plugin system."""
        try:
            # Add default plugin directories
            default_plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extensions")
            self.plugin_loader.add_plugin_directory(default_plugin_dir)
            
            # Load plugins
            self.plugin_loader.load_plugins()
            
            # Update UI
            self.update_plugin_lists()
            
        except Exception as e:
            print(f"Error initializing plugin system: {e}")
            import traceback
            traceback.print_exc()

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