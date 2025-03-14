import sys
import os
import json
import asyncio
import websockets
import darkdetect
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSystemTrayIcon, QMenu, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QStatusBar, QMessageBox,
    QLineEdit, QProgressBar, QStyle, QComboBox, QCheckBox,
    QGroupBox, QRadioButton, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor, QFont

class ModernDarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.ColorRole.Window, QColor(33, 33, 33))
        self.setColor(QPalette.ColorRole.WindowText, QColor(238, 238, 238))
        self.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        self.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        self.setColor(QPalette.ColorRole.ToolTipBase, QColor(238, 238, 238))
        self.setColor(QPalette.ColorRole.ToolTipText, QColor(238, 238, 238))
        self.setColor(QPalette.ColorRole.Text, QColor(238, 238, 238))
        self.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ColorRole.ButtonText, QColor(238, 238, 238))
        self.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        self.setColor(QPalette.ColorRole.Link, QColor(66, 165, 245))
        self.setColor(QPalette.ColorRole.Highlight, QColor(66, 165, 245))
        self.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

class ModernLightPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        self.setColor(QPalette.ColorRole.WindowText, QColor(33, 33, 33))
        self.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        self.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        self.setColor(QPalette.ColorRole.ToolTipBase, QColor(33, 33, 33))
        self.setColor(QPalette.ColorRole.ToolTipText, QColor(33, 33, 33))
        self.setColor(QPalette.ColorRole.Text, QColor(33, 33, 33))
        self.setColor(QPalette.ColorRole.Button, QColor(250, 250, 250))
        self.setColor(QPalette.ColorRole.ButtonText, QColor(33, 33, 33))
        self.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 0))
        self.setColor(QPalette.ColorRole.Link, QColor(33, 150, 243))
        self.setColor(QPalette.ColorRole.Highlight, QColor(33, 150, 243))
        self.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

class ModernButton(QPushButton):
    def __init__(self, text, primary=False, danger=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.danger = danger
        self.setMinimumWidth(100)  
        self.setMinimumHeight(32)  
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_style(self):
        if self.danger:
            style = """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #dc3545, stop:1 #c82333);
                    color: white;
                    border: none;
                    padding: 6px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #c82333, stop:1 #bd2130);
                }
                QPushButton:pressed {
                    background: #bd2130;
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """
        elif self.primary:
            style = """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #28a745, stop:1 #218838);
                    color: white;
                    border: none;
                    padding: 6px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #218838, stop:1 #1e7e34);
                }
                QPushButton:pressed {
                    background: #1e7e34;
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """
        else:
            style = """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f8f9fa, stop:1 #e9ecef);
                    color: #212529;
                    border: 1px solid #ced4da;
                    padding: 6px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e9ecef, stop:1 #dee2e6);
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background: #dee2e6;
                }
                QPushButton:disabled {
                    background: #e9ecef;
                    color: #adb5bd;
                    border-color: #dee2e6;
                }
            """
        self.setStyleSheet(style)

class ModernGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid palette(highlight);
                border-radius: 8px;
                margin-top: 16px;
                padding: 24px 16px 16px 16px;
                background: palette(window);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                padding: 0 8px;
                color: palette(highlight);
                font-size: 14px;
            }
        """)

class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: 2px solid palette(mid);
                border-radius: 6px;
                padding: 6px 12px;
                background: palette(base);
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid palette(highlight);
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
            QComboBox::down-arrow {
                image: url(down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox:on {
                border: 2px solid palette(highlight);
            }
            QComboBox QAbstractItemView {
                border: 2px solid palette(highlight);
                border-radius: 6px;
                background: palette(base);
                selection-background-color: palette(highlight);
            }
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid palette(mid);
                border-radius: 6px;
                padding: 8px 12px;
                background: palette(base);
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 2px solid palette(highlight);
            }
            QLineEdit:disabled {
                background: palette(window);
                border-color: palette(mid);
                color: palette(mid);
            }
        """)

class ClientThread(QThread):
    connection_status = pyqtSignal(bool, str)
    plugin_status = pyqtSignal(dict)
    message_received = pyqtSignal(dict)
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.running = True
    
    def run(self):
        asyncio.run(self.client_loop())
    
    async def client_loop(self):
        while self.running:
            try:
                self.connection_status.emit(False, "Connecting...")
                
                async with websockets.connect(self.client.server_url) as websocket:
                    self.connection_status.emit(True, "Connected")
                    
                    # Authenticate
                    auth_message = {
                        "type": "auth",
                        "client_id": self.client.client_id,
                        "client_secret": self.client.client_secret
                    }
                    await websocket.send(json.dumps(auth_message))
                    
                    response = await websocket.recv()
                    auth_response = json.loads(response)
                    
                    if auth_response.get("status") != "success":
                        raise Exception("Authentication failed")
                    
                    # Get initial plugin status
                    plugins = self.client.plugin_loader.discover_plugins()
                    self.plugin_status.emit({"plugins": list(plugins.keys())})
                    
                    while True:
                        message = await websocket.recv()
                        parsed_message = json.loads(message)
                        self.message_received.emit(parsed_message)
                        
            except websockets.exceptions.ConnectionClosed:
                self.connection_status.emit(False, "Connection lost")
                await asyncio.sleep(5)
            except Exception as e:
                self.connection_status.emit(False, f"Error: {str(e)}")
                await asyncio.sleep(5)

class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.client_thread = None
        self.servers_config = self.load_servers_config()
        
        self.init_ui()
        
    def load_servers_config(self):
        try:
            with open('config/servers.json', 'r') as f:
                config = json.load(f)
                return config
        except Exception as e:
            return {"servers": {}, "default_server": ""}
        
    def init_ui(self):
        self.setWindowTitle("Remote Device Manager")
        self.setMinimumSize(1000, 700)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: palette(window);
            }
            QTabWidget::pane {
                border: 1px solid palette(mid);
                border-radius: 3px;
            }
            QTabBar::tab {
                padding: 8px 16px;
            }
            QTabBar::tab:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QTreeWidget {
                border: 2px solid palette(mid);
                border-radius: 6px;
                background: palette(base);
                padding: 8px;
            }
            QTreeWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background: palette(midlight);
            }
            QTreeWidget::item:selected {
                background: palette(highlight);
                color: palette(highlightedtext);
            }
            QStatusBar {
                border-top: 2px solid palette(mid);
                padding: 8px;
                font-weight: bold;
            }
            QLabel {
                font-size: 13px;
            }
            QRadioButton {
                font-size: 13px;
                padding: 4px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Dashboard tab
        dashboard = QWidget()
        dashboard_layout = QVBoxLayout(dashboard)
        dashboard_layout.setSpacing(16)  # Increased spacing between sections

        # Status section
        status_group = ModernGroupBox("Connection Status")
        status_layout = QHBoxLayout(status_group)
        
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: #ff5252; font-weight: bold;")
        status_layout.addWidget(self.connection_status)
        
        self.connect_button = ModernButton("Connect", primary=True)
        self.connect_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.connect_button.clicked.connect(self.toggle_connection)
        status_layout.addWidget(self.connect_button)
        
        status_layout.addStretch()
        dashboard_layout.addWidget(status_group)
        
        # Plugin section
        plugins_group = ModernGroupBox("Installed Plugins")
        plugins_layout = QVBoxLayout(plugins_group)
        
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderLabels(["Plugin", "Status", "Actions"])
        self.plugin_tree.setAlternatingRowColors(True)
        self.plugin_tree.setMinimumWidth(800)  # Set minimum width for the tree
        self.plugin_tree.setMinimumHeight(200)  # Set minimum height
        
        # Style the tree widget
        self.plugin_tree.setStyleSheet("""
            QTreeWidget {
                background-color: palette(base);
            }
            QTreeWidget::item {
                min-height: 44px;  /* Increased row height */
                padding: 4px;
            }
            QTreeWidget QHeaderView::section {
                background-color: palette(window);
                padding: 6px;
                border: none;
                border-right: 1px solid palette(mid);
            }
        """)
        
        # Load and display plugins
        self.load_plugins()
        
        plugins_layout.addWidget(self.plugin_tree)
        dashboard_layout.addWidget(plugins_group)
        
        tabs.addTab(dashboard, "Dashboard")
        tabs.setTabIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Logs tab
        logs = QWidget()
        logs_layout = QVBoxLayout(logs)
        logs_layout.setContentsMargins(15, 15, 15, 15)
        
        logs_group = ModernGroupBox("System Logs")
        logs_inner_layout = QVBoxLayout(logs_group)
        
        self.log_view = QTreeWidget()
        self.log_view.setHeaderLabels(["Time", "Level", "Message"])
        self.log_view.setColumnWidth(0, 150)
        self.log_view.setColumnWidth(1, 100)
        self.log_view.setAlternatingRowColors(True)
        logs_inner_layout.addWidget(self.log_view)
        
        logs_layout.addWidget(logs_group)
        
        tabs.addTab(logs, "Logs")
        tabs.setTabIcon(1, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        
        # Settings tab
        settings = QWidget()
        settings_layout = QVBoxLayout(settings)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(15)
        
        # Server Configuration Group
        server_group = ModernGroupBox("Server Configuration")
        server_layout = QVBoxLayout()
        server_layout.setSpacing(16)
        
        # Server Mode Selection
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)
        self.auto_radio = QRadioButton("Automatic")
        self.manual_radio = QRadioButton("Manual")
        mode_layout.addWidget(self.auto_radio)
        mode_layout.addWidget(self.manual_radio)
        mode_layout.addStretch()
        server_layout.addLayout(mode_layout)
        
        # Auto Server Selection
        self.server_combo = ModernComboBox()
        for server_name in self.servers_config["servers"]:
            self.server_combo.addItem(server_name)
        server_layout.addWidget(self.server_combo)
        
        # Manual Server URL
        self.url_input = ModernLineEdit()
        self.url_input.setPlaceholderText("Enter server URL...")
        server_layout.addWidget(self.url_input)
        
        server_group.setLayout(server_layout)
        settings_layout.addWidget(server_group)
        
        # Client Configuration Group
        client_group = ModernGroupBox("Client Configuration")
        client_layout = QVBoxLayout()
        client_layout.setSpacing(16)
        
        # Client ID
        id_layout = QHBoxLayout()
        id_label = QLabel("Client ID:")
        self.id_input = ModernLineEdit()
        self.id_input.setText(self.client.client_id)
        self.id_input.setReadOnly(True)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        client_layout.addLayout(id_layout)
        
        # Client Secret
        secret_layout = QHBoxLayout()
        secret_label = QLabel("Client Secret:")
        self.secret_input = ModernLineEdit()
        self.secret_input.setText(self.client.client_secret)
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_secret_btn = ModernButton("Show")
        self.show_secret_btn.clicked.connect(self.toggle_secret_visibility)
        secret_layout.addWidget(secret_label)
        secret_layout.addWidget(self.secret_input)
        secret_layout.addWidget(self.show_secret_btn)
        client_layout.addLayout(secret_layout)
        
        client_group.setLayout(client_layout)
        settings_layout.addWidget(client_group)
        
        # Hide URL input initially if automatic is selected
        self.auto_radio.toggled.connect(self.update_server_mode)
        self.server_combo.currentTextChanged.connect(self.update_server_url)
        
        # Set initial server mode
        self.auto_radio.setChecked(True)
        self.update_server_mode(True)

        settings_layout.addStretch()
        tabs.addTab(settings, "Settings")
        tabs.setTabIcon(2, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        
        # Connect signals
        self.auto_radio.toggled.connect(self.update_server_mode)
        self.server_combo.currentTextChanged.connect(self.update_server_url)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # System tray
        self.setup_system_tray()
        
        # Start client thread
        self.start_client()
    
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setToolTip("Remote Device Manager")
        
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def update_server_mode(self, checked):
        if checked:  # Automatic mode
            self.server_combo.setVisible(True)
            self.url_input.setVisible(False)
            if self.server_combo.currentText() in self.servers_config["servers"]:
                server_url = self.servers_config["servers"][self.server_combo.currentText()]["url"]
                self.url_input.setText(server_url)
        else:  # Manual mode
            self.server_combo.setVisible(False)
            self.url_input.setVisible(True)

    def update_server_url(self, server_name):
        if self.auto_radio.isChecked() and server_name in self.servers_config["servers"]:
            server_url = self.servers_config["servers"][server_name]["url"]
            self.url_input.setText(server_url)

    def toggle_secret_visibility(self):
        if self.secret_input.echoMode() == QLineEdit.EchoMode.Password:
            reply = QMessageBox.warning(
                self,
                "Security Warning",
                "Revealing the client secret can be a security risk. "
                "Make sure no one else can see your screen. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.secret_input.setEchoMode(QLineEdit.EchoMode.Normal)
                self.show_secret_btn.setText("Hide")
        else:
            self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_secret_btn.setText("Show")
    
    def start_client(self):
        if self.client_thread is None or not self.client_thread.isRunning():
            self.client_thread = ClientThread(self.client)
            self.client_thread.connection_status.connect(self.update_connection_status)
            self.client_thread.plugin_status.connect(self.update_plugins)
            self.client_thread.message_received.connect(self.handle_message)
            self.client_thread.start()
            self.connect_button.setText("Disconnect")
            self.connect_button.primary = False
            self.connect_button.danger = True
            self.connect_button.update_style()
    
    def toggle_connection(self):
        if self.client_thread and self.client_thread.isRunning():
            self.client_thread.running = False
            self.client_thread.quit()
            self.client_thread = None
            self.connect_button.setText("Connect")
            self.connect_button.primary = True
            self.connect_button.danger = False
            self.connect_button.update_style()
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: #ff5252; font-weight: bold;")
        else:
            self.start_client()
    
    def update_connection_status(self, connected, message):
        self.connection_status.setText(message)
        self.connection_status.setStyleSheet(
            "color: #34c759; font-weight: bold;" if connected else "color: #ff5252; font-weight: bold;"
        )
        self.status_bar.showMessage(message)
    
    def update_plugins(self, data):
        self.plugin_tree.clear()
        for plugin_name in data.get("plugins", []):
            item = QTreeWidgetItem([plugin_name, "Loaded", ""])
            self.plugin_tree.addTopLevelItem(item)
    
    def handle_message(self, message):
        item = QTreeWidgetItem([
            QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"),
            message.get("type", "INFO"),
            str(message)
        ])
        self.log_view.addTopLevelItem(item)
        self.log_view.scrollToBottom()
    
    def load_plugins(self):
        self.plugin_tree.clear()
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugin_core', 'plugins')
        
        if not os.path.exists(plugin_dir):
            print(f"Plugin directory not found: {plugin_dir}")
            return
            
        self.plugin_buttons = {}
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_name = filename[:-3]
                item = QTreeWidgetItem(self.plugin_tree)
                item.setText(0, plugin_name)
                item.setText(1, "Disabled")
                
                # Create action buttons container
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(8, 8, 8, 8)  # Increased margins
                action_layout.setSpacing(20)  # More space between buttons
                
                # Enable/Disable button
                toggle_btn = ModernButton("Enable", primary=True)
                toggle_btn.setFixedSize(150, 36)  # Increased button size
                toggle_btn.clicked.connect(lambda checked, name=plugin_name, btn=toggle_btn: self.toggle_plugin(name, btn))
                action_layout.addWidget(toggle_btn)
                self.plugin_buttons[plugin_name] = toggle_btn
                
                # Configure button
                config_btn = ModernButton("Configure")
                config_btn.setFixedSize(150, 36)  # Increased button size
                config_btn.clicked.connect(lambda checked, name=plugin_name: self.configure_plugin(name))
                action_layout.addWidget(config_btn)
                
                action_layout.addStretch()
                self.plugin_tree.setItemWidget(item, 2, action_widget)

        # Set proper column widths
        self.plugin_tree.setColumnWidth(0, 250)  # Plugin name
        self.plugin_tree.setColumnWidth(1, 150)  # Status
        self.plugin_tree.setColumnWidth(2, 400)  # Actions - much wider for buttons

    def toggle_plugin(self, plugin_name, button):
        try:
            if button.text() == "Enable":
                button.setText("Disable")
                button.primary = False
                button.danger = True
                button.update_style()
            else:
                button.setText("Enable")
                button.primary = True
                button.danger = False
                button.update_style()
        except Exception as e:
            print(f"Error toggling plugin {plugin_name}: {e}")

    def configure_plugin(self, plugin_name):
        print(f"Opening configuration for plugin: {plugin_name}")
        # Add configuration logic here
        
    def closeEvent(self, event):
        if self.client_thread and self.client_thread.isRunning():
            self.client_thread.running = False
            self.client_thread.quit()
            self.client_thread.wait()
        event.accept()
        
    def quit_application(self):
        self.close()
        
def create_gui(client):
    # Create Qt Application
    app = QApplication(sys.argv)
    
    # Set style based on system theme
    app.setStyle("Fusion")
    if darkdetect.isDark():
        app.setPalette(ModernDarkPalette())
    else:
        app.setPalette(ModernLightPalette())
    
    # Create and show the main window
    window = MainWindow(client)
    window.show()
    
    return app, window  # Return both app and window to prevent window from being garbage collected
