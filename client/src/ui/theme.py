from PyQt6.QtWidgets import QPushButton, QWidget, QTabWidget, QLineEdit, QTabBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Color scheme
COLORS = {
    'primary': '#4a90e2',
    'primary_hover': '#357abd',
    'primary_pressed': '#2d6da3',
    'secondary': '#6c757d',
    'secondary_hover': '#5a6268',
    'secondary_pressed': '#545b62',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'white': '#ffffff',
    'sidebar_bg': '#f5f5f5',
    'content_bg': '#ffffff',
    'border': '#dee2e6',
    'text': '#333333',
    'text_secondary': '#6c757d',
}

class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                background-color: {COLORS['sidebar_bg']};
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['content_bg']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_secondary']};
            }}
        """)

class ModernButton(QPushButton):
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['primary_pressed']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['primary']};
                    border: 2px solid {COLORS['primary']};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['sidebar_bg']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['border']};
                }}
            """)

class ModernSidebarButton(QPushButton):
    def __init__(self, text, icon_name=None):
        super().__init__(text)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if icon_name:
            # Create QIcon from the icon name
            icon = QIcon(f"client/src/ui/icons/{icon_name}.png")
            self.setIcon(icon)
        
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                padding: 12px 20px;
                text-align: left;
                font-size: 14px;
                color: {COLORS['text']};
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
            }}
        """)

class ModernTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 20px;
                background-color: {COLORS['white']};
            }}
            QTabBar::tab {{
                padding: 8px 16px;
                margin-right: 4px;
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background-color: {COLORS['light']};
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['white']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['white']};
            }}
        """)
