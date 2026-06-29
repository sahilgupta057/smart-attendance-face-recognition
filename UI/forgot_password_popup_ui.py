from PyQt5 import QtWidgets


class Ui_ForgotPasswordPopup(object):
    def setupUi(self, Dialog):
        Dialog.setFixedSize(380, 360)

        # ================= ROOT =================
        self.layout = QtWidgets.QVBoxLayout(Dialog)

        # ================= TITLE =================
        self.title = QtWidgets.QLabel(
            "<h3 style='color:#00b4d8;text-align:center;'>Reset Password</h3>"
        )
        self.layout.addWidget(self.title)

        # ================= EMAIL =================
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Registered Email")
        self.layout.addWidget(self.email_input)

        self.send_otp_btn = QtWidgets.QPushButton("Send OTP")
        self.layout.addWidget(self.send_otp_btn)

        # ================= OTP =================
        self.otp_input = QtWidgets.QLineEdit()
        self.otp_input.setPlaceholderText("Enter OTP")
        self.otp_input.setEnabled(False)
        self.layout.addWidget(self.otp_input)

        # ================= PASSWORD =================
        self.new_pass_input = QtWidgets.QLineEdit()
        self.new_pass_input.setPlaceholderText("New Password")
        self.new_pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_pass_input.setEnabled(False)

        self.confirm_pass_input = QtWidgets.QLineEdit()
        self.confirm_pass_input.setPlaceholderText("Confirm Password")
        self.confirm_pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_pass_input.setEnabled(False)

        self.layout.addWidget(self.new_pass_input)
        self.layout.addWidget(self.confirm_pass_input)

        self.reset_btn = QtWidgets.QPushButton("Reset Password")
        self.reset_btn.setEnabled(False)
        self.layout.addWidget(self.reset_btn)

        # ================= STYLE =================
        Dialog.setStyleSheet("""
            QDialog {
                background-color:#1a1a1a;
                border-radius:12px;
                border:2px solid #00b4d8;
            }
            QLineEdit {
                background-color:#000;
                border:1px solid #444;
                border-radius:6px;
                padding:8px;
                color:#eee;
            }
            QPushButton {
                background-color:#000;
                border:1px solid #333;
                border-radius:6px;
                padding:10px;
                color:#fff;
            }
            QPushButton:hover {
                border:1px solid #00b4d8;
                color:#00b4d8;
            }
        """)
