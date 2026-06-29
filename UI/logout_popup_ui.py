from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_LogoutPopup(object):
    def setupUi(self, Dialog):
        # Slightly adjusted size for better proportion
        Dialog.setFixedSize(380, 220)
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)

        # ================= ROOT =================
        self.root = QtWidgets.QVBoxLayout(Dialog)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # ================= TOP BAR (Window Controls) =================
        self.top_bar_widget = QtWidgets.QWidget()
        self.top_bar = QtWidgets.QHBoxLayout(self.top_bar_widget)
        self.top_bar.setContentsMargins(10, 10, 10, 0)
        self.top_bar.addStretch()

        self.close_btn = QtWidgets.QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setObjectName("closeButton")

        self.top_bar.addWidget(self.close_btn)
        self.root.addWidget(self.top_bar_widget)

        # ================= CONTENT =================
        self.content = QtWidgets.QVBoxLayout()
        self.content.setContentsMargins(40, 5, 40, 30)
        self.content.setSpacing(10)

        self.title = QtWidgets.QLabel("Confirm Logout")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            color: #fff; 
            font-size: 20px; 
            font-weight: 700; 
            letter-spacing: 0.5px;
        """)

        self.message = QtWidgets.QLabel("You are about to end your session.\nDo you wish to proceed?")
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.message.setWordWrap(True)
        self.message.setStyleSheet("color: #777; font-size: 13px; line-height: 140%;")

        self.content.addWidget(self.title)
        self.content.addWidget(self.message)
        self.content.addSpacing(15)

        # ================= BUTTONS =================
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.setSpacing(12)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(42)
        self.cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.cancel_btn.setObjectName("cancelButton")

        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setFixedHeight(42)
        self.logout_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.logout_btn.setObjectName("logoutButton")

        self.btn_layout.addWidget(self.cancel_btn)
        self.btn_layout.addWidget(self.logout_btn)

        self.content.addLayout(self.btn_layout)
        self.root.addLayout(self.content)

        # ================= STYLE =================
        Dialog.setStyleSheet("""
            QDialog {
                background-color: #0B0E14; /* Deep Midnight */
                border: 1px solid #30363D; /* Subtle stroke */
                border-radius: 16px;
            }

            /* PRIMARY ACTION (Login / Logout / Save) */
            QPushButton#loginPrimary, QPushButton#logoutButton {
                background-color: #00D4FF;
                color: #050505;
                border: none;
                border-radius: 10px;
                font-weight: 700;
                font-size: 13px;
            }

            QPushButton#loginPrimary:hover {
                background-color: #33E0FF; /* Slight lighten on hover */
            }

            /* SECONDARY/CANCEL BUTTONS */
            QPushButton#cancelButton, QPushButton#signupSecondary {
                background-color: rgba(255, 255, 255, 0.05); /* Ghost background */
                border: 1px solid #30363D;
                color: #C9D1D9;
            }

            QPushButton#cancelButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #00D4FF; /* Subtle brand hint */
            }

            /* INPUT FIELDS */
            QLineEdit {
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                padding: 10px;
                color: #F0F6FC;
            }

            QLineEdit:focus {
                border: 1px solid #00D4FF; /* Focus ring */
                background-color: #121820;
            }
    """)