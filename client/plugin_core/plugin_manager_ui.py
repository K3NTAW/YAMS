from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QListWidget, 
                             QLabel, QFileDialog, QMessageBox, QHBoxLayout,
                             QListWidgetItem, QStyle)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
import os
import shutil
from typing import Optional

class PluginManagerDialog(QDialog):
    """Dialog for managing plugins including installation of new plugins."""
    
    def __init__(self, plugin_dir: str, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Plugin Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setAcceptDrops(True)  # Enable drag and drop
        
        layout = QVBoxLayout()
        
        # Drop zone
        self.drop_zone = QLabel(
            "📥 Drag and Drop Plugins Here\n"
            "or use the Install button below"
        )
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed palette(mid);
                border-radius: 8px;
                padding: 20px;
                background: palette(base);
                font-size: 14px;
            }
        """)
        self.drop_zone.setMinimumHeight(100)
        layout.addWidget(self.drop_zone)
        
        # Instructions
        instructions = QLabel(
            "✨ Install plugins by dragging .py files here or using the 'Install Plugin' button.\n"
            "🔄 Plugins will be automatically loaded after installation.\n"
            "⚠️ Only .py files that implement the PluginInterface are supported."
        )
        instructions.setStyleSheet("font-size: 12px; color: palette(text); padding: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Plugin list
        list_label = QLabel("Installed Plugins:")
        list_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(list_label)
        
        self.plugin_list = QListWidget()
        self.plugin_list.setStyleSheet("""
            QListWidget {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid palette(mid);
            }
            QListWidget::item:last {
                border-bottom: none;
            }
        """)
        self.refresh_plugin_list()
        layout.addWidget(self.plugin_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        install_btn = QPushButton("Install Plugin")
        install_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        install_btn.clicked.connect(self.browse_for_plugin)
        install_btn.setStyleSheet("""
            QPushButton {
                background: palette(button);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: palette(light);
            }
        """)
        button_layout.addWidget(install_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        refresh_btn.clicked.connect(self.refresh_plugin_list)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: palette(button);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: palette(light);
            }
        """)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background: palette(button);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: palette(light);
            }
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for plugin files."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if all(url.toLocalFile().endswith('.py') for url in urls):
                self.drop_zone.setStyleSheet("""
                    QLabel {
                        border: 2px dashed palette(highlight);
                        border-radius: 8px;
                        padding: 20px;
                        background: palette(base);
                        font-size: 14px;
                        color: palette(highlight);
                    }
                """)
                event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave events."""
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed palette(mid);
                border-radius: 8px;
                padding: 20px;
                background: palette(base);
                font-size: 14px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for plugin files."""
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed palette(mid);
                border-radius: 8px;
                padding: 20px;
                background: palette(base);
                font-size: 14px;
            }
        """)
        for url in event.mimeData().urls():
            self.install_plugin(url.toLocalFile())
        self.refresh_plugin_list()
    
    def browse_for_plugin(self):
        """Open file dialog to browse for plugin files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Plugin Files",
            "",
            "Python Files (*.py)"
        )
        
        for file in files:
            self.install_plugin(file)
        self.refresh_plugin_list()
    
    def install_plugin(self, source_path: str) -> bool:
        """Install a plugin file to the plugins directory."""
        try:
            # Basic validation
            if not source_path.endswith('.py'):
                self.show_error("Invalid plugin file. Only .py files are supported.")
                return False
                
            filename = os.path.basename(source_path)
            if filename == '__init__.py':
                self.show_error("Cannot install __init__.py files.")
                return False
            
            # Check if plugin already exists
            target_path = os.path.join(self.plugin_dir, filename)
            if os.path.exists(target_path):
                reply = QMessageBox.question(
                    self,
                    "Plugin Exists",
                    f"Plugin {filename} already exists. Do you want to replace it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return False
            
            # Copy plugin file
            shutil.copy2(source_path, target_path)
            QMessageBox.information(
                self,
                "Success",
                f"Plugin {filename} has been installed successfully."
            )
            return True
            
        except Exception as e:
            self.show_error(f"Failed to install plugin: {str(e)}")
            return False
    
    def refresh_plugin_list(self):
        """Refresh the list of installed plugins."""
        self.plugin_list.clear()
        try:
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    item = QListWidgetItem(
                        self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon),
                        filename
                    )
                    item.setToolTip(f"Plugin file: {filename}")
                    self.plugin_list.addItem(item)
        except Exception as e:
            self.show_error(f"Failed to refresh plugin list: {str(e)}")
    
    def show_error(self, message: str):
        """Show an error message dialog."""
        QMessageBox.critical(self, "Error", message)
