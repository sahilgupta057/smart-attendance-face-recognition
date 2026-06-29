from PyQt5 import QtWidgets, QtCore, QtGui
from utils.auth_db import AuthDatabase


class ConfirmPasswordPopup(QtWidgets.QDialog):
    """
    Lightweight re-authentication dialog.
    Pre-fills the email from the currently logged-in user so they only
    need to enter their password to confirm identity before saving.
    """

    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.valid = False

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setFixedSize(340, 220)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                border: 1px solid #2196F3;
                border-radius: 12px;
            }
            QLabel#title_label {
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
            }
            QLabel#sub_label {
                color: #aaaacc;
                font-size: 11px;
            }
            QLineEdit {
                background-color: #2a2a3e;
                color: #ffffff;
                border: 1px solid #3a3a5e;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
            QPushButton#confirm_btn {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 0;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#confirm_btn:hover {
                background-color: #1976D2;
            }
            QPushButton#cancel_btn {
                background-color: transparent;
                color: #aaaacc;
                border: 1px solid #3a3a5e;
                border-radius: 6px;
                padding: 7px 0;
                font-size: 12px;
            }
            QPushButton#cancel_btn:hover {
                color: #ffffff;
                border-color: #888;
            }
        """)

        self._build_ui()
        self._apply_mask()

    # ------------------------------------------------------------------ #
    #  UI Construction
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        # Title
        title = QtWidgets.QLabel("Confirm Your Identity")
        title.setObjectName("title_label")
        root.addWidget(title)

        # Subtitle
        sub = QtWidgets.QLabel(f"Enter your password to save changes for\n{self.email}")
        sub.setObjectName("sub_label")
        sub.setWordWrap(True)
        root.addWidget(sub)

        root.addSpacing(4)

        # Password field
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.returnPressed.connect(self._confirm)
        root.addWidget(self.password_input)

        # Error label (hidden by default)
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: #f44336; font-size: 11px;")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.hide()
        root.addWidget(self.error_label)

        root.addSpacing(2)

        # Buttons row
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(10)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)

        self.confirm_btn = QtWidgets.QPushButton("Confirm & Save")
        self.confirm_btn.setObjectName("confirm_btn")
        self.confirm_btn.clicked.connect(self._confirm)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.confirm_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------ #
    #  Rounded mask
    # ------------------------------------------------------------------ #
    def _apply_mask(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 12, 12)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    # ------------------------------------------------------------------ #
    #  Confirm logic — only checks password for the pre-filled email
    # ------------------------------------------------------------------ #
    def _confirm(self):
        password = self.password_input.text()

        if not password:
            self._show_error("Please enter your password.")
            return

        user = AuthDatabase().authenticate(self.email, password)
        if user:
            self.valid = True
            self.accept()
        else:
            self._show_error("Incorrect password. Please try again.")
            self.password_input.clear()
            self.password_input.setFocus()

    def _show_error(self, msg: str):
        self.error_label.setText(msg)
        self.error_label.show()