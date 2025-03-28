from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QMessageBox, QStackedWidget,
                            QWidget, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from ..core.database import DatabaseManager
import uuid
import secrets

class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 16px;
                background-color: #f5f5f5;
                color: #333333;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
        """)

class ModernButton(QPushButton):
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2d6da3;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #4a90e2;
                    border: 2px solid #4a90e2;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #f0f7ff;
                }
                QPushButton:pressed {
                    background-color: #e5f1ff;
                }
            """)

class LoginWindow(QDialog):
    login_successful = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.init_ui()
        self.setWindowTitle('YAMS - Login')
        self.setFixedSize(400, 500)
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """)
        
        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Login page
        login_page = QWidget()
        login_layout = QVBoxLayout(login_page)
        login_layout.setSpacing(15)
        login_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo/Title
        title_label = QLabel('Welcome Back')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        login_layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel('Sign in to continue')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("QLabel { color: #666666; font-size: 16px; margin-bottom: 20px; }")
        login_layout.addWidget(subtitle)
        
        # Add some spacing
        login_layout.addSpacing(20)
        
        # Username input
        self.username_input = ModernLineEdit(placeholder='Username')
        login_layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = ModernLineEdit(placeholder='Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.password_input)
        
        # Add some spacing
        login_layout.addSpacing(20)
        
        # Login button
        login_button = ModernButton('Sign In', primary=True)
        login_button.clicked.connect(self.login)
        login_layout.addWidget(login_button)
        
        # Register link
        register_link = ModernButton('Create New Account', primary=False)
        register_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        login_layout.addWidget(register_link)
        
        # Add stretching space at the bottom
        login_layout.addStretch()
        
        # Registration page
        register_page = QWidget()
        register_layout = QVBoxLayout(register_page)
        register_layout.setSpacing(15)
        register_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        reg_title = QLabel('Create Account')
        reg_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reg_title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        register_layout.addWidget(reg_title)
        
        # Subtitle
        reg_subtitle = QLabel('Fill in your details to get started')
        reg_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reg_subtitle.setStyleSheet("QLabel { color: #666666; font-size: 16px; margin-bottom: 20px; }")
        register_layout.addWidget(reg_subtitle)
        
        # Add some spacing
        register_layout.addSpacing(20)
        
        # Registration inputs
        self.reg_username = ModernLineEdit(placeholder='Username')
        register_layout.addWidget(self.reg_username)
        
        self.reg_email = ModernLineEdit(placeholder='Email')
        register_layout.addWidget(self.reg_email)
        
        self.reg_password = ModernLineEdit(placeholder='Password')
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.reg_password)
        
        self.reg_confirm_password = ModernLineEdit(placeholder='Confirm Password')
        self.reg_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.reg_confirm_password)
        
        # Add some spacing
        register_layout.addSpacing(20)
        
        # Register button
        register_button = ModernButton('Create Account', primary=True)
        register_button.clicked.connect(self.register)
        register_layout.addWidget(register_button)
        
        # Back to login button
        back_button = ModernButton('Back to Login', primary=False)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        register_layout.addWidget(back_button)
        
        # Add stretching space at the bottom
        register_layout.addStretch()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(login_page)
        self.stacked_widget.addWidget(register_page)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
    
    def login(self):
        """Handle login attempt."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Get user info from database
        user_info = self.db.authenticate_user(username, password)
        if user_info:
            self.user_id = user_info['id']
            self.username = user_info['username']
            self.client_id = user_info['client_id']
            self.client_secret = user_info['client_secret']
            self.login_successful.emit(self.user_id)  # Emit the user ID
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid credentials')
    
    def register(self):
        """Handle registration attempt."""
        username = self.reg_username.text()
        password = self.reg_password.text()
        confirm_password = self.reg_confirm_password.text()
        email = self.reg_email.text()
        
        # Validate inputs
        if not all([username, password, confirm_password, email]):
            QMessageBox.warning(self, 'Registration Failed', 'All fields are required')
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, 'Registration Failed', 'Passwords do not match')
            return
        
        # Generate client credentials internally
        client_id = str(uuid.uuid4())
        client_secret = secrets.token_urlsafe(32)
        
        success, error = self.db.register_user(
            username, password, email, client_id, client_secret
        )
        
        if success:
            QMessageBox.information(
                self,
                'Registration Successful',
                'Account created successfully! You can now log in.'
            )
            self.stacked_widget.setCurrentIndex(0)  # Switch back to login
            # Clear registration fields
            self.reg_username.clear()
            self.reg_email.clear()
            self.reg_password.clear()
            self.reg_confirm_password.clear()
        else:
            QMessageBox.warning(self, 'Registration Failed', error)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # If user clicks X button, reject the dialog which will close the app
        self.reject()
        event.accept()
        self.reject()
        event.accept()
