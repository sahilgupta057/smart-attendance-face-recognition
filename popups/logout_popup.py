from PyQt5 import QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect

from UI.logout_popup_ui import Ui_LogoutPopup
from utils.open_popup_sound import PopupSound


class LogoutPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_LogoutPopup()
        self.ui.setupUi(self)

        self.popup_sound = PopupSound()
        self.action = None

        # ================= CONNECTIONS =================
        self.ui.close_btn.clicked.connect(self.reject)
        self.ui.cancel_btn.clicked.connect(self.reject)
        self.ui.logout_btn.clicked.connect(self._logout)

    # ================= ACTION =================
    def _logout(self):
        self.action = "logout"
        self.accept()

    # ================= ANIMATION =================
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()
        self.animate_open()

    def animate_open(self):
        start = QRect(
            self.x() + self.width() // 2,
            self.y() + self.height() // 2,
            0,
            0
        )
        end = self.geometry()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(400)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()
