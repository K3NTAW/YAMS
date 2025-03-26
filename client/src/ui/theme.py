"""Theme management for YAMS."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QPalette,
    QColor,
    QIcon,
    QPainter,
    QPixmap,
    QBrush,
    QFont,
    QPen
)
from PyQt6.QtCore import (
    QSize,
    QRect,
    QPoint
)
from PyQt6.QtWidgets import (
    QPushButton,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QGroupBox,
    QRadioButton,
    QCheckBox,
    QStatusBar
)
import os

# Color definitions
COLORS = {
    'primary': '#007AFF',
    'primary_hover': '#0056b3',
    'sidebar_bg': '#f8f9fa',
    'sidebar_bg_dark': '#1e1e1e',
    'content_bg': '#ffffff',
    'content_bg_dark': '#2d2d2d',
    'text': '#212529',
    'text_dark': '#ffffff',
    'text_secondary': '#6c757d',
    'text_secondary_dark': '#a0a0a0',
    'border': '#dee2e6',
    'border_dark': '#404040',
}

class ModernLineEdit(QLineEdit):
    """Modern styled line edit."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                background-color: {COLORS['content_bg']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)

class ModernSidebarButton(QPushButton):
    """Modern styled sidebar button."""
    
    def __init__(self, text, icon_name=None, is_dark_mode=False):
        """Initialize the button."""
        super().__init__(text)
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_name = icon_name
        self.icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", f"{icon_name}.svg") if icon_name else None
        
        if self.icon_path and os.path.exists(self.icon_path):
            self.setIconSize(QSize(24, 24))
        
        self.update_theme(is_dark_mode)
    
    def update_theme(self, is_dark_mode):
        """Update button theme."""
        # Update icon color
        if self.icon_path and os.path.exists(self.icon_path):
            icon = QIcon(self.icon_path)
            pixmap = icon.pixmap(24, 24)
            
            # Create mask from the original pixmap
            mask = pixmap.createMaskFromColor(QColor('#000000'), Qt.MaskMode.MaskOutColor)
            
            # Create a new pixmap and fill it with the desired color
            colored_pixmap = QPixmap(pixmap.size())
            colored_pixmap.fill(QColor('#FFFFFF' if is_dark_mode else '#000000'))
            colored_pixmap.setMask(mask)
            
            # Set the colored icon
            self.setIcon(QIcon(colored_pixmap))
        
        # Update stylesheet
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 16px;
                border: none;
                border-radius: 0;
                font-size: 14px;
                background-color: transparent;
                color: """ + ('#FFFFFF' if is_dark_mode else '#000000') + """;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.2);
                color: """ + ('#FFFFFF' if is_dark_mode else '#000000') + """;
            }
        """)

class ModernTabWidget(QTabWidget):
    """Modern styled tab widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 20px;
                background-color: {COLORS['content_bg']};
            }}
            QTabBar::tab {{
                padding: 8px 16px;
                margin-right: 4px;
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background-color: {COLORS['sidebar_bg']};
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['content_bg']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['content_bg']};
            }}
        """)

class ModernButton(QPushButton):
    """Modern styled button."""
    
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
                    background-color: {COLORS['primary_hover']};
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

class ThemeManager:
    """Manages application theming."""
    
    @staticmethod
    def get_system_theme():
        """Get the system theme (dark or light)."""
        # On macOS, we can check system appearance
        try:
            import Foundation
            appearance = Foundation.NSApp.effectiveAppearance()
            return appearance.name().containsString_('Dark')
        except:
            return False  # Default to light theme if we can't detect
    
    @staticmethod
    def apply_theme(window, is_dark_mode=None):
        """Apply theme to the window and all its widgets."""
        # If theme is set to follow system, get system theme
        if is_dark_mode is None:
            is_dark_mode = ThemeManager.get_system_theme()
        
        # Create palette
        palette = QPalette()
        
        if is_dark_mode:
            # Dark theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['sidebar_bg_dark']))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text_dark']))
            palette.setColor(QPalette.ColorRole.Base, QColor(COLORS['content_bg_dark']))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS['sidebar_bg_dark']))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS['content_bg_dark']))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS['text_dark']))
            palette.setColor(QPalette.ColorRole.Text, QColor(COLORS['text_dark']))
            palette.setColor(QPalette.ColorRole.Button, QColor(COLORS['sidebar_bg_dark']))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS['text_dark']))
            palette.setColor(QPalette.ColorRole.Link, QColor(COLORS['primary']))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS['primary']))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS['text_dark']))
            
            # Update stylesheet
            window.setStyleSheet("""
                QMainWindow {
                    background-color: """ + COLORS['content_bg_dark'] + """;
                }
                #sidebar {
                    background-color: """ + COLORS['sidebar_bg_dark'] + """;
                    border-right: 1px solid """ + COLORS['border_dark'] + """;
                }
                #titleWidget {
                    border-bottom: 1px solid """ + COLORS['border_dark'] + """;
                }
                #titleLabel {
                    color: """ + COLORS['text_dark'] + """;
                }
                #subtitleLabel {
                    color: """ + COLORS['text_secondary_dark'] + """;
                }
                QPushButton {
                    background-color: """ + COLORS['primary'] + """;
                    color: """ + COLORS['text_dark'] + """;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: """ + COLORS['primary_hover'] + """;
                }
                QPushButton:disabled {
                    background-color: """ + COLORS['text_secondary_dark'] + """;
                }
                QLineEdit {
                    background-color: """ + COLORS['sidebar_bg_dark'] + """;
                    color: """ + COLORS['text_dark'] + """;
                    border: 1px solid """ + COLORS['border_dark'] + """;
                    border-radius: 4px;
                    padding: 8px;
                }
                QGroupBox {
                    border: 1px solid """ + COLORS['border_dark'] + """;
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 1em;
                    color: """ + COLORS['text_dark'] + """;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px;
                }
                QLabel {
                    color: """ + COLORS['text_dark'] + """;
                }
                QRadioButton, QCheckBox {
                    color: """ + COLORS['text_dark'] + """;
                }
                QStatusBar {
                    background-color: """ + COLORS['sidebar_bg_dark'] + """;
                    color: """ + COLORS['text_dark'] + """;
                }
            """)
        else:
            # Light theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['sidebar_bg']))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text']))
            palette.setColor(QPalette.ColorRole.Base, QColor(COLORS['content_bg']))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS['sidebar_bg']))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS['content_bg']))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS['text']))
            palette.setColor(QPalette.ColorRole.Text, QColor(COLORS['text']))
            palette.setColor(QPalette.ColorRole.Button, QColor(COLORS['sidebar_bg']))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS['text']))
            palette.setColor(QPalette.ColorRole.Link, QColor(COLORS['primary']))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS['primary']))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#ffffff'))
            
            # Update stylesheet
            window.setStyleSheet("""
                QMainWindow {
                    background-color: """ + COLORS['content_bg'] + """;
                }
                #sidebar {
                    background-color: """ + COLORS['sidebar_bg'] + """;
                    border-right: 1px solid """ + COLORS['border'] + """;
                }
                #titleWidget {
                    border-bottom: 1px solid """ + COLORS['border'] + """;
                }
                #titleLabel {
                    color: """ + COLORS['text'] + """;
                }
                #subtitleLabel {
                    color: """ + COLORS['text_secondary'] + """;
                }
                QPushButton {
                    background-color: """ + COLORS['primary'] + """;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: """ + COLORS['primary_hover'] + """;
                }
                QPushButton:disabled {
                    background-color: """ + COLORS['text_secondary'] + """;
                }
                QLineEdit {
                    background-color: """ + COLORS['content_bg'] + """;
                    color: """ + COLORS['text'] + """;
                    border: 1px solid """ + COLORS['border'] + """;
                    border-radius: 4px;
                    padding: 8px;
                }
                QGroupBox {
                    border: 1px solid """ + COLORS['border'] + """;
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 1em;
                    color: """ + COLORS['text'] + """;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px;
                }
                QLabel {
                    color: """ + COLORS['text'] + """;
                }
                QRadioButton, QCheckBox {
                    color: """ + COLORS['text'] + """;
                }
                QStatusBar {
                    background-color: """ + COLORS['sidebar_bg'] + """;
                    color: """ + COLORS['text'] + """;
                }
            """)
        
        window.setPalette(palette)
