from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
from utils.auth_db import AuthDatabase
import re


class SignupPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setFixedWidth(480)

        self.class_subject_rows = []  # store rows of class/subject fields

        # ---------------- ROOT LAYOUT ----------------
        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------- TOP BAR ----------------
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addStretch()
        self.close_btn = QtWidgets.QPushButton("X")
        self.close_btn.setFixedSize(34, 34)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setObjectName("closeButton")
        top_bar.addWidget(self.close_btn)

        # ---------------- CONTENT ----------------
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setContentsMargins(30, 10, 30, 25)
        content_layout.setSpacing(18)

        # Title
        title = QtWidgets.QLabel("Create Account")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color:#00b4d8; font-size:22px; font-weight:600;")
        subtitle = QtWidgets.QLabel("Sign up to get started")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("color:#888; font-size:13px;")
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)

        # ---------------- INPUTS ----------------
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.mobile_input = QtWidgets.QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile Number")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_input = QtWidgets.QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        input_font = QtGui.QFont("Segoe UI", 14)
        for field in [self.name_input, self.email_input, self.mobile_input,
                      self.password_input, self.confirm_password_input]:
            field.setFont(input_font)
            content_layout.addWidget(field)

        # ---------------- TEACHER CLASS/SUBJECT ----------------
        self.class_subject_label = QtWidgets.QLabel("Assign Classes & Subjects:")
        self.class_subject_label.setStyleSheet("""
            color: #00b4d8;       /* same blue accent as title */
            font-size: 16px;       /* slightly larger than subtitle */
            font-weight: 600;      /* semi-bold */
        """)
        self.class_subject_label.setAlignment(QtCore.Qt.AlignLeft)  # align left
        content_layout.addWidget(self.class_subject_label)
                          
        self.class_subject_container = QtWidgets.QVBoxLayout()
        content_layout.addLayout(self.class_subject_container)

        self.add_class_subject_row()  # Add first row by default

        add_button = QtWidgets.QPushButton("+ Add Another Class/Subject")
        add_button.setCursor(QtCore.Qt.PointingHandCursor)
        add_button.clicked.connect(self.add_class_subject_row)
        content_layout.addWidget(add_button)

        # ---------------- SIGNUP BUTTON ----------------
        self.signup_btn = QtWidgets.QPushButton("Create Account")
        self.signup_btn.setObjectName("primaryButton")
        self.signup_btn.setCursor(QtCore.Qt.PointingHandCursor)
        button_font = QtGui.QFont("Segoe UI", 14, QtGui.QFont.Medium)
        self.signup_btn.setFont(button_font)
        content_layout.addWidget(self.signup_btn)
        self.signup_btn.clicked.connect(self.handle_signup)

        root_layout.addLayout(top_bar)
        root_layout.addLayout(content_layout)

        # ---------------- STYLE ----------------
        self.setStyleSheet("""
            QDialog { background-color: #121212; border-radius:14px; border:1px solid #1f1f1f; }
            QLineEdit { background-color:#1c1c1c; border:1px solid #333; border-radius:12px;
                        padding:12px 16px; color:#eee; font-size:17px; }
            QLineEdit::placeholder { color:#888; }
            QLineEdit:focus { border:1px solid #00b4d8; }
            QPushButton { background-color:#1c1c1c; border:1px solid #333; border-radius:12px; color:#eee; font-size:17px; }
            QPushButton:hover { border:1px solid #00b4d8; color:#00b4d8; }
            QPushButton#primaryButton { background-color:#00b4d8; color:#000; font-weight:600; border:none; }
            QPushButton#primaryButton:hover { background-color:#0096c7; }
            QPushButton#closeButton { background:transparent; border:none; color:#888; font-size:20px; font-weight:bold; }
            QPushButton#closeButton:hover { color:#ff5f56; }
        """)

    # ---------------- ADD CLASS/SUBJECT ROW ----------------
    def add_class_subject_row(self):
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        class_input = QtWidgets.QLineEdit()
        class_input.setPlaceholderText("Class Name")
        subject_input = QtWidgets.QLineEdit()
        subject_input.setPlaceholderText("Subject Name")

        remove_btn = QtWidgets.QPushButton("X")
        remove_btn.setFixedWidth(30)
        remove_btn.setCursor(QtCore.Qt.PointingHandCursor)
        remove_btn.clicked.connect(lambda: self.remove_class_subject_row(row_widget))

        row_layout.addWidget(class_input)
        row_layout.addWidget(subject_input)
        row_layout.addWidget(remove_btn)

        self.class_subject_container.addWidget(row_widget)
        self.class_subject_rows.append((row_widget, class_input, subject_input))

    def remove_class_subject_row(self, row_widget):
        for i, (widget, _, _) in enumerate(self.class_subject_rows):
            if widget == row_widget:
                self.class_subject_container.removeWidget(widget)
                widget.deleteLater()
                self.class_subject_rows.pop(i)
                break

    def animate_open(self):
        start_rect = QRect(
            self.x() + self.width() // 2,
            self.y() + self.height() // 2,
            0,
            0
        )
        end_rect = self.geometry()
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(280)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()


    # ---------------- HANDLE SIGNUP ----------------
    def handle_signup(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip().lower()
        mobile = self.mobile_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()

        if not all([name, email, mobile, password, confirm]):
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        
        # MOBILE NUMBER VALIDATION
        if not mobile.isdigit() or len(mobile) != 10:
            QMessageBox.warning(self, "Error", "Enter a valid 10-digit mobile number.")
            return
                
        # Email format validation
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "Error", "Invalid email format.")
            return

        # Password length validation
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return
        
        # Password strength validation (PASTE HERE)
        if not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
            QMessageBox.warning(
                self,
                "Error",
                "Password must contain at least one uppercase letter and one number."
            )
            return


        # Password match validation
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return


        # Collect class/subject pairs
        assignments = []
        for _, class_input, subject_input in self.class_subject_rows:
            class_name = class_input.text().strip()
            subject_name = subject_input.text().strip()
            if class_name and subject_name:
                assignments.append({"class": class_name, "subject": subject_name})
        if not assignments:
            QMessageBox.warning(self, "Error", "At least one class & subject is required.")
            return
        
        # Check for duplicate class & subject pairs
        seen = set()
        for a in assignments:
            key = (a["class"].lower(), a["subject"].lower())
            if key in seen:
                QMessageBox.warning(self, "Error", "Duplicate class & subject found.")
                return
            seen.add(key)


        # Here you would handle database signup
        db = AuthDatabase()

        # Check if user already exists
        if db.user_exists(email):
            QMessageBox.warning(self, "Error", "This email is already registered.")
            return

        # Create user with assignments (classes & subjects)
        if not db.create_user(name, email, mobile, password, assignments):
            QMessageBox.warning(self, "Error", "Signup failed.")
            return

        QMessageBox.information(self, "Success", "Account created successfully!")
        self.accept()


    def showEvent(self, event):
        super().showEvent(event)
        self.animate_open()



def open_signup_popup(parent):
    """Opens the signup popup centered on the parent window, returns True if signup succeeded."""
    dialog = SignupPopup(parent)

    # Center the popup
    parent_pos = parent.mapToGlobal(QtCore.QPoint(0, 0))
    x = parent_pos.x() + (parent.width() - dialog.width()) // 2
    y = parent_pos.y() + (parent.height() - dialog.height()) // 2
    dialog.move(x, y)

    # Execute signup dialog
    result = dialog.exec_()
    return result == QtWidgets.QDialog.Accepted

