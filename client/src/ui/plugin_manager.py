from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QListWidget, QListWidgetItem, QLabel, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt
import os

class PluginManagerDialog(QDialog):
    def __init__(self, plugin_loader, plugin_dir, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.plugin_loader = plugin_loader
        self.plugin_dir = plugin_dir
        self.setWindowTitle("Plugin Manager")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Plugin directory section
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(f"Plugin Directory: {self.plugin_dir}")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        layout.addLayout(dir_layout)
        
        # Plugin list
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderLabels(["Name", "Version", "Status"])
        self.plugin_tree.setColumnWidth(0, 200)
        self.plugin_tree.itemClicked.connect(self.toggle_plugin)
        layout.addWidget(self.plugin_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("Install Plugin...")
        self.install_btn.clicked.connect(self.install_plugin)
        button_layout.addWidget(self.install_btn)
        
        self.uninstall_btn = QPushButton("Uninstall Plugin")
        self.uninstall_btn.clicked.connect(self.uninstall_plugin)
        button_layout.addWidget(self.uninstall_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_plugin_list)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize plugin list
        self.refresh_plugin_list()
    
    def install_plugin(self):
        """Install a new plugin"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Plugin File",
            os.path.expanduser("~"),
            "Python Files (*.py)"
        )
        
        if file_path:
            try:
                if self.plugin_loader.install_plugin(file_path, self.plugin_dir):
                    QMessageBox.information(self, "Success", "Plugin installed successfully!")
                    self.refresh_plugin_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to install plugin")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to install plugin: {str(e)}")
    
    def uninstall_plugin(self):
        """Uninstall selected plugin"""
        current_item = self.plugin_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a plugin to uninstall")
            return
            
        plugin_name = current_item.text(0)
        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            f"Are you sure you want to uninstall '{plugin_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.plugin_loader.uninstall_plugin(plugin_name):
                    QMessageBox.information(self, "Success", f"Plugin '{plugin_name}' uninstalled successfully!")
                    self.refresh_plugin_list()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to uninstall plugin '{plugin_name}'")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to uninstall plugin: {str(e)}")
    
    def refresh_plugin_list(self):
        """Refresh the plugin list"""
        self.plugin_tree.clear()
        
        if not os.path.exists(self.plugin_dir):
            return
            
        # Force reload plugins
        self.plugin_loader.load_plugins()
            
        for plugin_name, plugin in self.plugin_loader.plugins.items():
            metadata = plugin.get_metadata()
            item = QTreeWidgetItem(self.plugin_tree)
            item.setText(0, plugin_name)
            item.setText(1, metadata.get('version', '1.0.0'))
            item.setText(2, 'Active' if plugin.is_active() else 'Inactive')
            self.plugin_tree.addTopLevelItem(item)
            
    def toggle_plugin(self, item: QTreeWidgetItem, column: int):
        """Toggle plugin active state when clicking the status column"""
        if column == 2:  # Status column
            plugin_name = item.text(0)
            plugin = self.plugin_loader.get_plugin(plugin_name)
            if plugin:
                new_state = not plugin.is_active()
                if self.plugin_loader.set_plugin_active(plugin_name, new_state):
                    item.setText(2, 'Active' if new_state else 'Inactive')
                    self.parent.update_plugin_lists()
