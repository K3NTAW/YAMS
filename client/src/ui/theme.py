from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
import darkdetect

class ThemeManager:
    """Manages application theming with support for light and dark modes."""
    
    LIGHT_THEME = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'bg_tertiary': '#e5e5e5',
        'accent': '#2b5797',
        'accent_hover': '#1e3c6e',
        'accent_pressed': '#153053',
        'text_primary': '#000000',
        'text_secondary': '#666666',
        'border': '#cccccc',
        'button_text': '#ffffff',
        'input_bg': '#ffffff',
        'input_bg_disabled': '#f0f0f0',
        'status_bar_bg': '#f8f8f8',
    }
    
    DARK_THEME = {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#252526',
        'bg_tertiary': '#333333',
        'accent': '#0078d4',
        'accent_hover': '#1e8ae6',
        'accent_pressed': '#0063b1',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'border': '#404040',
        'button_text': '#ffffff',
        'input_bg': '#3c3c3c',
        'input_bg_disabled': '#2d2d2d',
        'status_bar_bg': '#007acc',
    }
    
    @classmethod
    def get_theme(cls, is_dark: bool) -> dict:
        """Get the theme colors based on the mode."""
        return cls.DARK_THEME if is_dark else cls.LIGHT_THEME
    
    @classmethod
    def apply_theme(cls, widget, is_dark: bool):
        """Apply theme to the widget and its children."""
        theme = cls.get_theme(is_dark)
        
        # Main window style
        widget.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
            }}
            
            QWidget {{
                color: {theme['text_primary']};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['bg_primary']};
            }}
            
            QTabBar::tab {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
                color: {theme['text_primary']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme['bg_primary']};
                color: {theme['accent']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {theme['bg_secondary']};
            }}
            
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['button_text']};
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                min-height: 32px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {theme['accent_pressed']};
            }}
            
            QPushButton:disabled {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text_secondary']};
            }}
            
            QLineEdit {{
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 4px 8px;
                background-color: {theme['input_bg']};
                color: {theme['text_primary']};
                min-height: 28px;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {theme['accent']};
            }}
            
            QLineEdit:disabled {{
                background-color: {theme['input_bg_disabled']};
                color: {theme['text_secondary']};
            }}
            
            QGroupBox {{
                border: 1px solid {theme['border']};
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 0.5em;
                color: {theme['text_primary']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {theme['accent']};
            }}
            
            QTreeWidget, QListWidget {{
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['bg_primary']};
                alternate-background-color: {theme['bg_secondary']};
            }}
            
            QTreeWidget::item, QListWidget::item {{
                color: {theme['text_primary']};
                padding: 4px;
            }}
            
            QTreeWidget::item:selected, QListWidget::item:selected {{
                background-color: {theme['accent']};
                color: {theme['button_text']};
            }}
            
            QStatusBar {{
                background-color: {theme['status_bar_bg']};
                color: {theme['button_text']};
                padding: 5px;
                font-size: 12px;
            }}
            
            QRadioButton {{
                color: {theme['text_primary']};
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {theme['accent']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {theme['accent']};
                border: 2px solid {theme['accent']};
            }}
            
            QRadioButton::indicator:unchecked {{
                background-color: {theme['bg_primary']};
                border: 2px solid {theme['border']};
            }}
            
            QLabel {{
                color: {theme['text_primary']};
            }}
            
            QMenu {{
                background-color: {theme['bg_primary']};
                border: 1px solid {theme['border']};
            }}
            
            QMenu::item {{
                padding: 6px 24px;
                color: {theme['text_primary']};
            }}
            
            QMenu::item:selected {{
                background-color: {theme['accent']};
                color: {theme['button_text']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {theme['border']};
                margin: 4px 0;
            }}
        """)
