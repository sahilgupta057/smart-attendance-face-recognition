import pyttsx3
from PyQt5 import QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtWidgets import QMessageBox

from UI.login_popup_ui import Ui_LoginPopup
from utils.auth_db import AuthDatabase
from popups.class_subject_popup import ClassSubjectPopup
from utils.open_popup_sound import PopupSound
from popups.signup_popup import SignupPopup
from popups.forgot_password_popup import ForgotPasswordPopup
from attendance_manager import AttendanceManager
from utils.database import UserDatabase



class LoginPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_LoginPopup()
        self.ui.setupUi(self)

        self.valid = False
        self.logged_in_user = None
        self._login_in_progress = False
        self.popup_sound = PopupSound()

        # CONNECTIONS
        self.ui.close_btn.clicked.connect(self.reject)
        self.ui.login_btn.clicked.connect(self.try_login)
        self.ui.signup_btn.clicked.connect(self.open_signup)
        self.ui.forgot_btn.clicked.connect(self.open_forgot_password)

    # ---------------- ANIMATION ----------------
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()
        self.animate_open()

    def animate_open(self):
        start = QRect(self.x()+self.width()//2, self.y()+self.height()//2, 0, 0)
        end = self.geometry()
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(400)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()

    # ---------------- LOGIN LOGIC ----------------
    def try_login(self):
        if self._login_in_progress:
            return

        self._login_in_progress = True
        self.ui.login_btn.setEnabled(False)

        email = self.ui.email_input.text().strip().lower()
        password = self.ui.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")
            return self._reset()

        user = AuthDatabase().authenticate(email, password)
        if not user:
            QMessageBox.warning(self, "Error", "Invalid email or password.")
            return self._reset()

        engine = pyttsx3.init()
        engine.say(f"Welcome {user['name']}")
        engine.runAndWait()

        accounts = user.get("assignments", [])
        if not accounts:
            QMessageBox.warning(self, "Error", "No class or subject assigned.")
            return self._reset()

        if len(accounts) > 1:
            popup = ClassSubjectPopup(accounts, self)
            if popup.exec_() != QtWidgets.QDialog.Accepted:
                return self._reset()
            account = next(a for a in accounts if a["id"] == popup.selected_account_id)
        else:
            account = accounts[0]

        print("Selected account:", account)  
        # ----------------- Initialize today's attendance -----------------
        # use same sanitization pattern as the rest of app
        folder_name = user['email'].replace("@", "_").replace(".", "_")
        db = UserDatabase(folder_name)

        # Only assign account_id to students who do not yet have one.
        # previous version overwrote all students on every login, causing cross-account
        # visibility issues when a user switched subjects.
        db.conn.execute(
            "UPDATE students SET teacher_account_id = ? WHERE teacher_account_id IS NULL",
            (account["id"],)
        )
        db.conn.commit()


        students = db.get_students_by_account(account["id"])
        print("Students after fix:", students)

        # Initialize today's attendance
        db.initialize_today_attendance(account["id"])
        sheet = db.get_today_attendance_sheet(account["id"])
        print("Today sheet:", sheet)

        db.close()



        self.logged_in_user = {
            **user,
            "teacher_account_id": account["id"],
            "class_name": account.get("class"),
            "subject_name": account.get("subject"),
            "department_id": account.get("department_id"),
            "subject_id": account.get("subject_id")
        }

        self.valid = True
        self.accept()

    def _reset(self):
        self._login_in_progress = False
        self.ui.login_btn.setEnabled(True)

    # ---------------- POPUPS ----------------
    def open_signup(self):
        SignupPopup(self).exec_()

    def open_forgot_password(self):
        ForgotPasswordPopup(self).exec_()
