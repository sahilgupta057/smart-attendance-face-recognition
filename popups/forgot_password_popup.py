import random

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from utils.auth_db import AuthDatabase
from utils.email_sender import send_otp_email

from UI.forgot_password_popup_ui import Ui_ForgotPasswordPopup


class ForgotPasswordPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_ForgotPasswordPopup()
        self.ui.setupUi(self)

        self.auth_db = AuthDatabase()
        self.otp_code = None
        self.email = None

        # ================= CONNECTIONS =================
        self.ui.send_otp_btn.clicked.connect(self.send_otp)
        self.ui.reset_btn.clicked.connect(self.reset_password)

    # ================= OTP =================
    def send_otp(self):
        email = self.ui.email_input.text().strip().lower()

        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email.")
            return

        if not self.auth_db.user_exists(email):
            QMessageBox.warning(self, "Error", "Email not found.")
            return

        self.email = email
        self.otp_code = str(random.randint(100000, 999999))

        send_otp_email(email, self.otp_code)

        QMessageBox.information(self, "OTP Sent", "OTP has been sent to your email.")

        self.ui.otp_input.setEnabled(True)
        self.ui.new_pass_input.setEnabled(True)
        self.ui.confirm_pass_input.setEnabled(True)
        self.ui.reset_btn.setEnabled(True)

    # ================= RESET =================
    def reset_password(self):
        otp = self.ui.otp_input.text().strip()
        new_pass = self.ui.new_pass_input.text()
        confirm_pass = self.ui.confirm_pass_input.text()

        if otp != self.otp_code:
            QMessageBox.warning(self, "Error", "Invalid OTP.")
            return

        if not new_pass or new_pass != confirm_pass:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        # Plain password → DB handles hashing
        self.auth_db.update_password(self.email, new_pass)

        QMessageBox.information(self, "Success", "Password updated successfully.")
        self.accept()
