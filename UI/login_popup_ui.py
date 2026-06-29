from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_LoginPopup(object):
    def setupUi(self, Dialog):
        Dialog.setFixedSize(400, 450) # Taller, slimmer profile for a modern look
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        
        # ROOT
        self.root_layout = QtWidgets.QVBoxLayout(Dialog)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # TOP BAR (Window Controls)
        self.top_bar_widget = QtWidgets.QWidget()
        self.top_bar = QtWidgets.QHBoxLayout(self.top_bar_widget)
        self.top_bar.setContentsMargins(10, 10, 10, 0)
        self.top_bar.addStretch()

        self.close_btn = QtWidgets.QPushButton("✕") # Clean multiplication X
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setObjectName("closeButton")

        self.top_bar.addWidget(self.close_btn)
        self.root_layout.addWidget(self.top_bar_widget)

        # CONTENT AREA
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(40, 0, 40, 40)
        self.content_layout.setSpacing(12)

        # Header Section
        self.title = QtWidgets.QLabel("Welcome Back")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("color:#fff; font-size:24px; font-weight:700; margin-bottom:2px;")

        self.subtitle = QtWidgets.QLabel("Please enter your details to continue")
        self.subtitle.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle.setStyleSheet("color:#666; font-size:12px; font-weight: 500;")

        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(self.subtitle)
        self.content_layout.addSpacing(15)

        # INPUT FIELDS
        # Using a slightly smaller, more professional font size
        input_font = QtGui.QFont("Segoe UI", 10)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        self.email_input.setFont(input_font)
        self.email_input.setFixedHeight(45)

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setFont(input_font)
        self.password_input.setFixedHeight(45)

        self.content_layout.addWidget(self.email_input)
        self.content_layout.addWidget(self.password_input)

        # FORGOT PASSWORD
        self.forgot_btn = QtWidgets.QPushButton("Forgot password?")
        self.forgot_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.forgot_btn.setObjectName("forgotBtn")
        self.content_layout.addWidget(self.forgot_btn, alignment=QtCore.Qt.AlignRight)

        self.content_layout.addSpacing(10)

        # ACTION BUTTONS
        btn_font = QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold)

        self.login_btn = QtWidgets.QPushButton("Log In")
        self.login_btn.setFont(btn_font)
        self.login_btn.setFixedHeight(48)
        self.login_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.login_btn.setObjectName("loginPrimary")

        self.signup_btn = QtWidgets.QPushButton("Create New Account")
        self.signup_btn.setFont(btn_font)
        self.signup_btn.setFixedHeight(48)
        self.signup_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.signup_btn.setObjectName("signupSecondary")

        self.content_layout.addWidget(self.login_btn)
        self.content_layout.addWidget(self.signup_btn)

        self.root_layout.addLayout(self.content_layout)

        # --- ADVANCED PRO STYLING ---
        Dialog.setStyleSheet("""
            QDialog {
                background-color: #0f0f0f;
                border: 1px solid #222;
                border-radius: 20px;
            }

            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 0px 15px;
                color: #fff;
            }

            QLineEdit:focus {
                border: 1px solid #00b4d8;
                background-color: #1e1e1e;
            }

            /* Primary Action Button */
            QPushButton#loginPrimary {
                background-color: #00b4d8;
                color: #000;
                border: none;
                border-radius: 8px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            QPushButton#loginPrimary:hover {
                background-color: #0096c7;
            }

            /* Secondary Action Button (Ghost Style) */
            QPushButton#signupSecondary {
                background-color: transparent;
                color: #eee;
                border: 1px solid #333;
                border-radius: 8px;
            }

            QPushButton#signupSecondary:hover {
                background-color: #222;
                border: 1px solid #444;
            }

            QPushButton#forgotBtn {
                color: #555;
                font-size: 11px;
                border: none;
                background: transparent;
                font-weight: bold;
            }

            QPushButton#forgotBtn:hover {
                color: #00b4d8;
            }

            QPushButton#closeButton {
                background: transparent;
                color: #444;
                font-size: 16px;
                border-radius: 15px;
            }

            QPushButton#closeButton:hover {
                background-color: #ff5f56;
                color: #fff;
            }
        """)