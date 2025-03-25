from PyQt6.QtWidgets import QPushButton, QLineEdit, QTabBar, QWidget
from PyQt6.QtCore import Qt

# Color scheme
COLORS = {
    'primary': '#4a90e2',
    'primary_hover': '#357abd',
    'primary_pressed': '#2d6da3',
    'background': '#ffffff',
    'sidebar': '#f5f5f5',
    'text': '#333333',
    'text_secondary': '#666666',
    'border': '#e0e0e0',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336'
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
                background-color: {COLORS['sidebar']};
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['background']};
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
                    background-color: {COLORS['sidebar']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['border']};
                }}
            """)

class ModernSidebarButton(QPushButton):
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                text-align: left;
                margin: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)

class ModernTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
