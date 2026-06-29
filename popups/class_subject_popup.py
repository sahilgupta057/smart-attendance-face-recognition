from PyQt5 import QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect

from UI.class_subject_popup_ui import Ui_ClassSubjectPopup


class ClassSubjectPopup(QtWidgets.QDialog):
    def __init__(self, teacher_accounts, parent=None):
        super().__init__(parent)

        self.teacher_accounts = teacher_accounts
        self.selected_account_id = None
        self.selected_class_name = None
        self.selected_subject_name = None

        self.ui = Ui_ClassSubjectPopup()
        self.ui.setupUi(self)

        self.populate_accounts()

        # ================= CONNECTIONS =================
        self.ui.continue_btn.clicked.connect(self.confirm)

    # ================= DATA =================
    def populate_accounts(self):
        self.ui.combo.clear()
        for acc in self.teacher_accounts:
            label = f"{acc['class']}  —  {acc['subject']}"
            self.ui.combo.addItem(label, acc["id"])

    def confirm(self):
        idx = self.ui.combo.currentIndex()
        acc = self.teacher_accounts[idx]

        self.selected_account_id = acc["id"]
        self.selected_class_name = acc["class"]
        self.selected_subject_name = acc["subject"]

        self.accept()

    # ================= ANIMATION =================
    def showEvent(self, event):
        super().showEvent(event)
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
