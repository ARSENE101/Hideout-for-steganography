import sys
import sqlite3
import bcrypt
import os
import base64
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpacerItem, QSizePolicy, QLineEdit, QMessageBox,
    QFileDialog, QProgressBar, QGroupBox, QStackedWidget, QFrame,
    QScrollArea, QGridLayout, QTextEdit, QTabWidget, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPen, QIcon


class UserDB:
    """Handles user authentication and storage using SQLite"""

    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.create_table()

    def create_table(self):
        """Create users table if not exists"""
        try:
            query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.conn.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"Error creating table: {e}")

    def register_user(self, username, password):
        """Register new user with hashed password"""
        try:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            self.conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username exists
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    def authenticate(self, username, password):
        """Verify user credentials"""
        try:
            cursor = self.conn.execute(
                "SELECT password FROM users WHERE username=?",
                (username,))
            row = cursor.fetchone()

            if row:
                stored_password = row[0]
                return bcrypt.checkpw(password.encode(), stored_password)
            return False
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = UserDB()
        self.setWindowTitle("Hideout - Authentication")
        self.setMinimumSize(400, 500)  # Make resizable
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)

        # Create scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Central widget
        central = QWidget()
        scroll_area.setWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Logo/Title Section
        title_frame = QFrame()
        title_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)

        logo_label = QLabel("🔐")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px; margin: 10px;")

        title_label = QLabel("Hideout")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin: 10px;
        """)
        title_label.setWordWrap(True)

        subtitle_label = QLabel("Steganography Suite")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            font-family: 'Segoe UI', Arial;
        """)
        subtitle_label.setWordWrap(True)

        title_layout.addWidget(logo_label)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        # Login Form
        form_frame = QFrame()
        form_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Form elements
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        input_style = """
            QLineEdit {
                background: black;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial;
            }
            QLineEdit:focus {
                border-color: #667eea;
                outline: none;
            }
        """
        self.username.setStyleSheet(input_style)
        self.password.setStyleSheet(input_style)

        # Buttons
        self.btn_login = QPushButton("Sign In")
        self.btn_login.clicked.connect(self.login)
        self.btn_register = QPushButton("Create Account")
        self.btn_register.clicked.connect(self.register)

        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fe8, stop:1 #6a47a0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f63e6, stop:1 #5f429e);
            }
        """

        register_button_style = """
            QPushButton {
                background: transparent;
                color: #667eea;
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background: #667eea;
                color: white;
            }
        """

        self.btn_login.setStyleSheet(button_style)
        self.btn_register.setStyleSheet(register_button_style)

        # Layout
        form_layout.addWidget(QLabel("Username"))
        form_layout.addWidget(self.username)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.password)
        form_layout.addWidget(self.btn_login)
        form_layout.addWidget(self.btn_register)

        layout.addWidget(title_frame)
        layout.addWidget(form_frame)
        layout.addStretch()

    def login(self):
        """Handle login attempt"""
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        if self.db.authenticate(username, password):
            self.open_main_app()
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials")

    def register(self):
        """Handle user registration"""
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Error", "Password must be ≥8 characters")
            return

        if self.db.register_user(username, password):
            QMessageBox.information(self, "Success", "Registration successful!")
        else:
            QMessageBox.critical(self, "Error", "Username already exists")

    def open_main_app(self):
        """Launch main application window"""
        self.main_window = MainApp(username=self.username.text())
        self.main_window.show()
        self.close()


class NavButton(QPushButton):
    """Custom navigation button with modern styling and responsive design"""

    def __init__(self, text, icon="", parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}" if icon else text)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.update_styles()

    def update_styles(self):
        """Update styles based on current size"""
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background: rgba(99, 102, 241, 0.1);
                color: #6366f1;
            }
            QPushButton:checked {
                background: #6366f1;
                color: white;
            }
        """)

    def resizeEvent(self, event):
        """Update styles when resized"""
        super().resizeEvent(event)
        self.update_styles()


class ModernSidebar(QWidget):
    """Modern responsive sidebar with navigation"""
    page_changed = pyqtSignal(int)

    def __init__(self, username):
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border-right: 1px solid #e5e7eb;
            }
        """)

        # Scroll area for sidebar
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        sidebar_content = QWidget()
        scroll_area.setWidget(sidebar_content)
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)

        # User Profile Section
        profile_frame = QFrame()
        profile_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        profile_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        profile_layout = QVBoxLayout(profile_frame)

        avatar_label = QLabel("👤")
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("font-size: 32px; color: white;")

        username_label = QLabel(f"Welcome, {username}")
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        username_label.setWordWrap(True)

        profile_layout.addWidget(avatar_label)
        profile_layout.addWidget(username_label)

        # Navigation Buttons
        nav_label = QLabel("Navigation")
        nav_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin: 16px 0 8px 0;
        """)

        self.nav_buttons = []
        nav_items = [
            ("Dashboard", "🏠", 0),
            ("Image Steganography", "🖼️", 1),
            ("Text Steganography", "📝", 2),
            ("Document Steganography", "📄", 3),
            ("Program Steganography", "💻", 4),
        ]

        for text, icon, index in nav_items:
            btn = NavButton(text, icon)
            btn.clicked.connect(lambda checked, idx=index: self.change_page(idx))
            self.nav_buttons.append(btn)

        # Set default selection
        self.nav_buttons[0].setChecked(True)

        # Tools Section
        tools_label = QLabel("Tools")
        tools_label.setStyleSheet(nav_label.styleSheet())

        tools_items = [
            ("Settings", "⚙️"),
            ("Help & Support", "❓"),
            ("About", "ℹ️"),
        ]

        self.tool_buttons = []
        for text, icon in tools_items:
            btn = NavButton(text, icon)
            self.tool_buttons.append(btn)

        # Logout Button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        logout_btn.clicked.connect(self.logout)

        # Layout
        sidebar_layout.addWidget(profile_frame)
        sidebar_layout.addWidget(nav_label)
        for btn in self.nav_buttons:
            sidebar_layout.addWidget(btn)
        sidebar_layout.addWidget(tools_label)
        for btn in self.tool_buttons:
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(logout_btn)

    def change_page(self, index):
        """Handle page navigation"""
        # Uncheck all navigation buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)

        # Check the selected button
        self.nav_buttons[index].setChecked(True)

        # Emit signal
        self.page_changed.emit(index)

    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.window().close()
            login_window = LoginWindow()
            login_window.show()


class DashboardWidget(QWidget):
    """Responsive Dashboard home page"""

    def __init__(self, username):
        super().__init__()
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Welcome Section
        welcome_frame = QFrame()
        welcome_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_frame)

        welcome_title = QLabel(f"Welcome back, {username}! 👋")
        welcome_title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        welcome_title.setWordWrap(True)

        welcome_subtitle = QLabel("Secure your data with advanced steganography techniques")
        welcome_subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
            margin-top: 8px;
        """)
        welcome_subtitle.setWordWrap(True)

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_subtitle)

        # Quick Actions Grid
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("""
            color: #1f2937;
            font-size: 20px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin: 20px 0 10px 0;
        """)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(15)

        quick_actions = [
            ("🖼️ Image Steganography", "Hide data in images", "#3b82f6"),
            ("📝 Text Steganography", "Embed secrets in text", "#10b981"),
            ("📄 Document Steganography", "Secure document hiding", "#f59e0b"),
            ("💻 Program Steganography", "Code-based concealment", "#8b5cf6"),
        ]

        for i, (title, desc, color) in enumerate(quick_actions):
            action_frame = QFrame()
            action_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            action_frame.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 2px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 15px;
                }}
                QFrame:hover {{
                    border-color: {color};
                    background: {color}15;
                }}
            """)

            action_layout = QVBoxLayout(action_frame)

            action_title = QLabel(title)
            action_title.setStyleSheet(f"""
                color: {color};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            """)
            action_title.setWordWrap(True)

            action_desc = QLabel(desc)
            action_desc.setStyleSheet("""
                color: #6b7280;
                font-size: 14px;
                font-family: 'Segoe UI', Arial;
                margin-top: 5px;
            """)
            action_desc.setWordWrap(True)

            action_layout.addWidget(action_title)
            action_layout.addWidget(action_desc)

            actions_grid.addWidget(action_frame, i // 2, i % 2)

        # Info Section
        info_frame = QFrame()
        info_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        info_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("💡 Did you know?")
        info_title.setStyleSheet("""
            color: #1f2937;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)

        info_text = QLabel(
            "Steganography is the practice of concealing information within another message or "
            "physical object. Unlike cryptography, which scrambles data, steganography hides "
            "the very existence of the secret information."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            color: #4b5563;
            font-size: 14px;
            font-family: 'Segoe UI', Arial;
            line-height: 1.6;
            margin-top: 10px;
        """)

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)

        content_layout.addWidget(welcome_frame)
        content_layout.addWidget(actions_label)
        content_layout.addLayout(actions_grid)
        content_layout.addWidget(info_frame)
        content_layout.addStretch()


class SteganographyWidget(QWidget):
    """Enhanced Responsive Image Steganography Widget with updated logic"""

    def __init__(self):
        super().__init__()
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        scroll_area.setWidget(content)
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("🖼️ Image Steganography")
        header_label.setStyleSheet("""
            color: #1f2937;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin-bottom: 10px;
        """)
        header_label.setWordWrap(True)

        subtitle_label = QLabel("Hide and extract data from images using LSB steganography")
        subtitle_label.setStyleSheet("""
            color: #6b7280;
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
        """)
        subtitle_label.setWordWrap(True)

        # Tab Widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                padding: 10px 15px;
                margin-right: 2px;
                font-family: 'Segoe UI', Arial;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #f3f4f6;
            }
        """)

        # Embed Tab
        embed_widget = self.create_embed_widget()
        tab_widget.addTab(embed_widget, "🔒 Hide Data")
        tab_widget.setStyleSheet("""
                    QFrame {
                        background: #f8fafc;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)

        # Extract Tab
        extract_widget = self.create_extract_widget()
        tab_widget.addTab(extract_widget, "🔓 Extract Data")


        self.content_layout.addWidget(header_label)
        self.content_layout.addWidget(subtitle_label)
        self.content_layout.addWidget(tab_widget)

        # Initialize variables
        self.carrier_path = None
        self.payload_path = None
        self.save_path = None
        self.original_payload_size = None

    def create_embed_widget(self):
        """Create the embedding interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # File selection section
        files_frame = QFrame()
        files_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        files_layout = QVBoxLayout(files_frame)

        # Carrier image selection
        carrier_layout = QHBoxLayout()
        carrier_layout.setSpacing(10)
        self.carrier_button = QPushButton("📁 Select Carrier Image")
        self.carrier_button.clicked.connect(self.upload_carrier)
        self.carrier_button.setStyleSheet(self.get_button_style("#3b82f6"))
        self.carrier_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.carrier_label = QLabel("No carrier image selected")
        self.carrier_label.setStyleSheet("color: #6b7280; font-size: 14px;")
        self.carrier_label.setWordWrap(True)
        self.carrier_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        carrier_layout.addWidget(self.carrier_button)
        carrier_layout.addWidget(self.carrier_label, 1)

        # Data file selection
        data_layout = QHBoxLayout()
        data_layout.setSpacing(10)
        self.data_button = QPushButton("📄 Select Data File")
        self.data_button.clicked.connect(self.upload_data)
        self.data_button.setStyleSheet(self.get_button_style("#10b981"))
        self.data_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.data_label = QLabel("No data file selected")
        self.data_label.setStyleSheet("color: #6b7280; font-size: 14px;")
        self.data_label.setWordWrap(True)
        self.data_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        data_layout.addWidget(self.data_button)
        data_layout.addWidget(self.data_label, 1)

        files_layout.addLayout(carrier_layout)
        files_layout.addLayout(data_layout)

        # Embed button
        self.embed_button = QPushButton("🔒 Embed Data")
        self.embed_button.clicked.connect(self.embed_data)
        self.embed_button.setStyleSheet(self.get_button_style("#8b5cf6", large=True))

        # Progress and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background: #f9fafb;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 6px;
            }
        """)

        self.status_message = QLabel("")
        self.status_message.setWordWrap(True)
        self.status_message.setStyleSheet("color: #059669; font-weight: bold; margin: 10px 0;")

        layout.addWidget(files_frame)
        layout.addWidget(self.embed_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_message)
        layout.addStretch()

        return widget

    def create_extract_widget(self):
        """Create the extraction interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # File selection
        select_frame = QFrame()
        select_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        select_layout = QHBoxLayout(select_frame)
        select_layout.setSpacing(10)

        self.extract_button = QPushButton("📁 Select Embedded Image")
        self.extract_button.clicked.connect(self.extract_data)
        self.extract_button.setStyleSheet(self.get_button_style("#f59e0b", large=True))
        self.extract_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.embedded_label = QLabel("No embedded image selected")
        self.embedded_label.setStyleSheet("color: #6b7280; font-size: 14px;")
        self.embedded_label.setWordWrap(True)
        self.embedded_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        select_layout.addWidget(self.extract_button)
        select_layout.addWidget(self.embedded_label, 1)

        # Progress and status
        self.extract_progress = QProgressBar()
        self.extract_progress.setStyleSheet(self.progress_bar.styleSheet())

        self.extract_status = QLabel("")
        self.extract_status.setWordWrap(True)
        self.extract_status.setStyleSheet("color: #059669; font-weight: bold; margin: 10px 0;")

        layout.addWidget(select_frame)
        layout.addWidget(self.extract_progress)
        layout.addWidget(self.extract_status)
        layout.addStretch()

        return widget

    def get_button_style(self, color, large=False):
        """Get consistent button styling"""
        padding = "12px 20px" if large else "10px 15px"
        font_size = "16px" if large else "14px"

        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: {padding};
                font-size: {font_size};
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }}
            QPushButton:hover {{
                background: {color}dd;
            }}
            QPushButton:pressed {{
                background: {color}bb;
            }}
        """

    def upload_carrier(self):
        """Upload carrier image with format warning"""
        try:
            self.carrier_path, _ = QFileDialog.getOpenFileName(
                self, "Select Carrier Image", "",
                "Images (*.png *.jpg *.jpeg);;All Files (*)"
            )

            if not self.carrier_path:
                self.carrier_label.setText("No carrier image selected")
                return

            self.carrier_label.setText(f"✅ {os.path.basename(self.carrier_path)}")
            self.carrier_label.setStyleSheet("color: #059669; font-size: 14px; font-weight: bold;")

            # Warn about JPEG format
            if self.carrier_path.lower().endswith(('.jpg', '.jpeg')):
                QMessageBox.warning(
                    self, "Warning",
                    "JPEG is lossy and may corrupt embedded data.\nUse PNG for best results."
                )

            # Show preview
            self.preview = PreviewDialog(self.carrier_path, self)
            self.preview.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload carrier image: {e}")

    def upload_data(self):
        """Upload data file"""
        try:
            self.payload_path, _ = QFileDialog.getOpenFileName(
                self, "Select Data File", "", "All Files (*)"
            )

            if not self.payload_path:
                self.data_label.setText("No data file selected")
                return

            file_size = os.path.getsize(self.payload_path)
            readable_size = self.format_file_size(file_size)
            self.data_label.setText(f"✅ {os.path.basename(self.payload_path)} ({readable_size})")
            self.data_label.setStyleSheet("color: #059669; font-size: 14px; font-weight: bold;")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload data file: {e}")

    def format_file_size(self, size_bytes):
        """Convert file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} GB"

    def embed_data(self):
        """Embed data into carrier image using LSB steganography"""
        try:
            if not self.carrier_path:
                QMessageBox.warning(self, "Error", "Please upload a carrier image")
                return

            if not self.payload_path:
                QMessageBox.warning(self, "Error", "Please upload a data file")
                return

            # Read data to embed
            with open(self.payload_path, 'rb') as f:
                data = f.read()

            # Add 4-byte length prefix (big-endian)
            data_length = len(data)
            length_bytes = data_length.to_bytes(4, byteorder='big')
            data_to_embed = length_bytes + data

            # Convert to bit string
            data_bits = ''.join(format(byte, '08b') for byte in data_to_embed)
            total_bits = len(data_bits)

            # Open carrier image
            img = Image.open(self.carrier_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            pixels = np.array(img)
            height, width, channels = pixels.shape
            total_pixels = height * width * channels

            # Check capacity
            if total_bits > total_pixels:
                QMessageBox.warning(
                    self, "Error",
                    f"Data too large for carrier image\n"
                    f"Carrier capacity: {self.format_file_size(total_pixels // 8)}\n"
                    f"Data size: {self.format_file_size(len(data_to_embed))}"
                )
                return

            # Create pixel generator
            pixel_gen = ((i, j, k)
                         for i in range(height)
                         for j in range(width)
                         for k in range(channels))

            # Update progress bar
            self.progress_bar.setMaximum(total_bits)
            self.progress_bar.setValue(0)
            self.status_message.setText("🔄 Embedding data...")
            QApplication.processEvents()

            # Embed data using LSB
            for bit_index, bit in enumerate(data_bits):
                i, j, k = next(pixel_gen)
                pixels[i, j, k] = (pixels[i, j, k] & 0xFE) | int(bit)

                # Update progress periodically
                if bit_index % 1000 == 0:
                    self.progress_bar.setValue(bit_index)
                    QApplication.processEvents()

            # Save embedded image
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Embedded Image", "",
                "PNG Images (*.png);;All Files (*)"
            )

            if not save_path:
                self.status_message.setText("❌ Embedding canceled")
                return

            # Ensure PNG format
            if not save_path.lower().endswith('.png'):
                save_path += '.png'

            embedded_image = Image.fromarray(pixels)
            embedded_image.save(save_path)

            # Add results section
            self.add_results_section(save_path, data_length, total_bits, total_pixels)

            self.progress_bar.setValue(total_bits)
            self.status_message.setText(
                f"✅ Data embedded successfully!\n"
                f"Saved as: {os.path.basename(save_path)}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Embedding failed: {str(e)}")
            self.status_message.setText("❌ Embedding failed")
            import traceback
            traceback.print_exc()

    def add_results_section(self, save_path, data_length, total_bits, total_pixels):
        """Add results display section after embedding"""
        # Remove existing results if any
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget and widget.objectName() == "results_frame":
                widget.deleteLater()

        # Results display
        results_frame = QFrame()
        results_frame.setObjectName("results_frame")
        results_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 15px;
            }
        """)
        results_layout = QVBoxLayout(results_frame)

        # Results title
        results_title = QLabel("📊 Processing Results")
        results_title.setStyleSheet("""
            color: #1f2937;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin-bottom: 10px;
        """)

        # Results text area
        bit_diff_text = QTextEdit()
        bit_diff_text.setReadOnly(True)
        bit_diff_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                color: #1f2937;
            }
        """)

        # Calculate and display metrics
        img = Image.open(self.carrier_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        pixels = np.array(img)
        height, width, channels = pixels.shape
        total_pixels = height * width * channels
        capacity_used = total_bits / total_pixels * 100
        metrics = (
            f"✅ Embedding Complete!\n\n"
            f"📦 File: {os.path.basename(save_path)}\n"
            f"📏 Size: {self.format_file_size(os.path.getsize(save_path))}\n"
            f"📊 Data Embedded: {self.format_file_size(data_length)}\n"
            f"🧮 Bits Embedded: {total_bits}\n"
            f"📈 Capacity Used: {capacity_used:.2f}%\n"
            f"🖼️ Image Dimensions: {pixels.shape[1]}x{pixels.shape[0]}"
        )
        bit_diff_text.setPlainText(metrics)

        results_layout.addWidget(results_title)
        results_layout.addWidget(bit_diff_text)

        self.content_layout.addWidget(results_frame)

    def extract_data(self):
        """Extract embedded data using LSB steganography"""
        try:
            embedded_image_path, _ = QFileDialog.getOpenFileName(
                self, "Select Embedded Image", "",
                "PNG Images (*.png);;All Files (*)"
            )

            if not embedded_image_path:
                self.embedded_label.setText("No embedded image selected")
                return

            self.embedded_label.setText(f"✅ {os.path.basename(embedded_image_path)}")
            self.embedded_label.setStyleSheet("color: #059669; font-size: 14px; font-weight: bold;")
            self.extract_status.setText("🔄 Processing image...")
            QApplication.processEvents()

            # Open embedded image
            img = Image.open(embedded_image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            pixels = np.array(img)
            height, width, channels = pixels.shape
            total_pixels = height * width * channels

            # Extract all LSBs
            binary_data = []
            for i in range(height):
                for j in range(width):
                    for k in range(channels):  # R, G, B channels
                        lsb = pixels[i, j, k] & 1
                        binary_data.append(str(lsb))

            # Convert binary data to a single string
            binary_string = ''.join(binary_data)

            # Extract 4-byte length prefix (32 bits)
            length_bits = binary_string[:32]
            if len(length_bits) < 32:
                QMessageBox.critical(self, "Error", "Image too small to contain valid data")
                self.extract_status.setText("❌ Extraction failed")
                return

            data_length = int(length_bits, 2)

            # Validate data length
            max_capacity = (total_pixels - 32) // 8
            if data_length <= 0 or data_length > max_capacity:
                QMessageBox.warning(
                    self, "Error",
                    f"Invalid data length detected: {data_length}\n"
                    f"Max capacity: {self.format_file_size(max_capacity)}"
                )
                self.extract_status.setText("❌ Invalid embedded data")
                return

            # Setup progress bar
            total_bits = data_length * 8
            self.extract_progress.setMaximum(total_bits)
            self.extract_progress.setValue(0)
            self.extract_status.setText(f"🔄 Extracting {self.format_file_size(data_length)}...")
            QApplication.processEvents()

            # Extract actual data
            data_bits = binary_string[32:32 + total_bits]
            if len(data_bits) < total_bits:
                QMessageBox.warning(self, "Error", "Image doesn't contain enough data")
                self.extract_status.setText("❌ Extraction failed")
                return

            extracted_data = bytearray()

            # Convert binary string to bytes
            for i in range(0, total_bits, 8):
                byte_str = data_bits[i:i + 8]
                if len(byte_str) == 8:
                    extracted_data.append(int(byte_str, 2))

                # Update progress periodically
                if i % 1000 == 0:
                    self.extract_progress.setValue(i)
                    QApplication.processEvents()

            # Verify extracted data length
            if len(extracted_data) != data_length:
                QMessageBox.warning(
                    self, "Error",
                    f"Extracted data length mismatch!\n"
                    f"Expected: {data_length} bytes\n"
                    f"Actual: {len(extracted_data)} bytes"
                )
                self.extract_status.setText("❌ Data length mismatch")
                return

            # Save extracted data
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Extracted Data", "", "All Files (*)"
            )

            if not save_path:
                self.extract_status.setText("❌ Extraction canceled")
                return

            with open(save_path, 'wb') as f:
                f.write(extracted_data)

            self.extract_progress.setValue(total_bits)
            self.extract_status.setText(
                f"✅ Data extracted successfully!\n"
                f"Saved as: {os.path.basename(save_path)}\n"
                f"Size: {self.format_file_size(len(extracted_data))}"
            )

            # Add results section
            self.add_extract_results(save_path, extracted_data, height, width)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Extraction failed: {str(e)}")
            self.extract_status.setText("❌ Extraction failed")
            import traceback
            traceback.print_exc()

    def add_extract_results(self, save_path, extracted_data, height, width):
        """Add results display section after extraction"""
        # Remove existing results if any
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget and widget.objectName() == "results_frame":
                widget.deleteLater()

        # Results display
        results_frame = QFrame()
        results_frame.setObjectName("results_frame")
        results_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 15px;
            }
        """)
        results_layout = QVBoxLayout(results_frame)

        # Results title
        results_title = QLabel("📊 Extraction Results")
        results_title.setStyleSheet("""
            color: #1f2937;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin-bottom: 10px;
        """)

        # Results text area
        bit_diff_text = QTextEdit()
        bit_diff_text.setReadOnly(True)
        bit_diff_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                color: #1f2937;
            }
        """)

        # Calculate and display metrics
        metrics = (
            f"✅ Extraction Complete!\n\n"
            f"📦 File: {os.path.basename(save_path)}\n"
            f"📏 Size: {self.format_file_size(len(extracted_data))}\n"
            f"🖼️ Image Dimensions: {width}x{height}\n"
            f"🔍 Extracted from: {self.embedded_label.text()}"
        )
        bit_diff_text.setPlainText(metrics)

        results_layout.addWidget(results_title)
        results_layout.addWidget(bit_diff_text)

        self.content_layout.addWidget(results_frame)


class PreviewDialog(QDialog):
    """Enhanced image preview dialog with responsive design"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setup_ui(image_path)

    def setup_ui(self, image_path):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(layout)

        # Title
        title = QLabel("Image Preview")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title_font.setPixelSize(self.calculate_font_size(14))
        title.setFont(title_font)
        title.setStyleSheet("color: #1f2937; margin-bottom: 10px; border: none; background: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", "Failed to load image!")
            return

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_image(pixmap)
        layout.addWidget(self.image_label)

        # Set adaptive styles
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 15px;
            }
            QLabel {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 10px;
                background: #f8fafc;
            }
        """)

    def calculate_font_size(self, base_size):
        """Calculate font size based on screen DPI and resolution"""
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        return max(12, int(base_size * dpi / 96))

    def update_image(self, pixmap):
        """Update image with proper scaling"""
        size = self.size() * 0.8  # Use 80% of dialog size
        scaled = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        """Resize image when dialog is resized"""
        super().resizeEvent(event)
        if hasattr(self, 'image_label') and self.image_label.pixmap():
            self.update_image(self.image_label.pixmap())

class TextSteganographyWidget(QWidget):
    """Text Steganography Widget with responsive design"""

    def __init__(self):
        super().__init__()
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("📝 Text Steganography")
        header_label.setStyleSheet("""
            color: #1f2937;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin-bottom: 10px;
        """)
        header_label.setWordWrap(True)

        subtitle_label = QLabel("Hide messages within plain text using various techniques")
        subtitle_label.setStyleSheet("""
            color: #6b7280;
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
        """)
        subtitle_label.setWordWrap(True)

        # Coming Soon Message
        coming_soon_frame = QFrame()
        coming_soon_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        coming_soon_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fbbf24, stop:1 #f59e0b);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        coming_soon_layout = QVBoxLayout(coming_soon_frame)

        icon_label = QLabel("🚧")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin-bottom: 20px;")

        title_label = QLabel("Coming Soon!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        title_label.setWordWrap(True)

        desc_label = QLabel("Text steganography features are under development")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
            margin-top: 10px;
        """)
        desc_label.setWordWrap(True)

        coming_soon_layout.addWidget(icon_label)
        coming_soon_layout.addWidget(title_label)
        coming_soon_layout.addWidget(desc_label)

        content_layout.addWidget(header_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addWidget(coming_soon_frame)
        content_layout.addStretch()


class DocumentSteganographyWidget(QWidget):
    """Document Steganography Widget with responsive design"""

    def __init__(self):
        super().__init__()
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("📄 Document Steganography")
        header_label.setStyleSheet("""
            color: #1f2937;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin-bottom: 10px;
        """)
        header_label.setWordWrap(True)

        subtitle_label = QLabel("Embed data within document files and formats")
        subtitle_label.setStyleSheet("""
            color: #6b7280;
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
        """)
        subtitle_label.setWordWrap(True)

        # Coming Soon Message
        coming_soon_frame = QFrame()
        coming_soon_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        coming_soon_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        coming_soon_layout = QVBoxLayout(coming_soon_frame)

        icon_label = QLabel("📋")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin-bottom: 20px;")

        title_label = QLabel("In Development")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        title_label.setWordWrap(True)

        desc_label = QLabel("Advanced document steganography coming soon")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
            margin-top: 10px;
        """)
        desc_label.setWordWrap(True)

        coming_soon_layout.addWidget(icon_label)
        coming_soon_layout.addWidget(title_label)
        coming_soon_layout.addWidget(desc_label)

        content_layout.addWidget(header_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addWidget(coming_soon_frame)
        content_layout.addStretch()


class ProgramSteganographyWidget(QWidget):
    """Program Steganography Widget with responsive design"""

    def __init__(self):
        super().__init__()
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("💻 Program Steganography")
        header_label.setStyleSheet("""
            color: #1f2937;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            margin-bottom: 10px;
        """)
        header_label.setWordWrap(True)

        subtitle_label = QLabel("Hide data within executable files and source code")
        subtitle_label.setStyleSheet("""
            color: #6b7280;
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
        """)
        subtitle_label.setWordWrap(True)

        # Coming Soon Message
        coming_soon_frame = QFrame()
        coming_soon_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        coming_soon_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        coming_soon_layout = QVBoxLayout(coming_soon_frame)

        icon_label = QLabel("⚡")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin-bottom: 20px;")

        title_label = QLabel("Advanced Feature")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        title_label.setWordWrap(True)

        desc_label = QLabel("Program steganography capabilities under development")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            font-family: 'Segoe UI', Arial;
            margin-top: 10px;
        """)
        desc_label.setWordWrap(True)

        coming_soon_layout.addWidget(icon_label)
        coming_soon_layout.addWidget(title_label)
        coming_soon_layout.addWidget(desc_label)

        content_layout.addWidget(header_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addWidget(coming_soon_frame)
        content_layout.addStretch()


class MainApp(QMainWindow):
    """Responsive main application window with modern design"""

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Hideout - Steganography Suite")
        self.setMinimumSize(1000, 700)  # Make resizable

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background: #f8fafc;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create sidebar
        self.sidebar = ModernSidebar(username)
        self.sidebar.page_changed.connect(self.change_page)

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background: white;
                border-radius: 0px;
            }
        """)

        # Add pages
        self.dashboard = DashboardWidget(username)
        self.image_stego = SteganographyWidget()
        self.text_stego = TextSteganographyWidget()
        self.doc_stego = DocumentSteganographyWidget()
        self.prog_stego = ProgramSteganographyWidget()

        self.stacked_widget.addWidget(self.dashboard)  # Index 0
        self.stacked_widget.addWidget(self.image_stego)  # Index 1
        self.stacked_widget.addWidget(self.text_stego)  # Index 2
        self.stacked_widget.addWidget(self.doc_stego)  # Index 3
        self.stacked_widget.addWidget(self.prog_stego)  # Index 4

        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget, 1)

    def change_page(self, index):
        """Change the displayed page"""
        self.stacked_widget.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Apply global styles
    app.setStyleSheet("""
        QMessageBox {
            background: white;
            color: #1f2937;
            font-family: 'Segoe UI', Arial;
        }
        QMessageBox QPushButton {
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QMessageBox QPushButton:hover {
            background: #2563eb;
        }
        QFileDialog {
            background: white;
            color: #1f2937;
        }
    """)

    # Show the login window first
    login_window = LoginWindow()
    login_window.show()

    # Start the application event loop
    sys.exit(app.exec())