from PyQt5 import QtWidgets, QtCore, QtGui

from utils.open_popup_sound import PopupSound
from utils.email_sender import send_email
from UI.help_popup_ui import Ui_HelpPopup

# ── Set this to your real developer / support email ───────────────────────────
DEVELOPER_EMAILS = [
    "sahilgupta74635@gmail.com",
    "prayashranapaheli@gmail.com",
    "yamanchettri1@gmail.com"  # add as many as you need
    "raiamar082@gmail.com"
]
# ─────────────────────────────────────────────────────────────────────────────


class HelpPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_HelpPopup()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)

        self.radius = 20
        self.popup_sound = PopupSound()

        self.setWindowMask()

        # ================= CONNECTIONS =================
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.contact_submit_btn.clicked.connect(self.submit_contact)
        self.ui.feedback_submit_btn.clicked.connect(self.submit_feedback)

        # Close when clicking outside
        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

    # ================= ROUNDED MASK =================
    def setWindowMask(self):
        rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # ================= SOUND =================
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()

    # ================= CONTACT SUBMIT =================
    def submit_contact(self):
        issue_type = self.ui.issue_type.currentText()
        priority   = self.ui.priority.currentText()
        message    = self.ui.message.toPlainText().strip()

        if not message:
            QtWidgets.QMessageBox.warning(
                self, "Empty Message",
                "Please write a message before submitting."
            )
            return

        subject = (
            f"[Smart Attendance] Contact Request"
            f" — {issue_type} [{priority} Priority]"
        )
        body = (
            f"Issue Type : {issue_type}\n"
            f"Priority   : {priority}\n"
            f"{'─' * 40}\n"
            f"{message}\n"
        )

        ok = self._send(subject, body, success_msg="Your message has been sent to the developer! ✅")
        if ok:
            self.ui.message.clear()

    # ================= FEEDBACK SUBMIT =================
    def submit_feedback(self):
        rating     = sum(1 for s in self.ui.stars if s.text() == "⭐")
        suggestion = self.ui.suggestion.toPlainText().strip()

        if rating == 0 and not suggestion:
            QtWidgets.QMessageBox.warning(
                self, "Nothing to Submit",
                "Please give a star rating or write a suggestion before submitting."
            )
            return

        star_str   = "⭐" * rating + "☆" * (5 - rating)
        emoji_text = self.ui.emoji_label.text()

        subject = f"[Smart Attendance] Feedback — {rating}/5 Stars"
        body = (
            f"Rating     : {star_str}  ({rating}/5)\n"
            f"Feeling    : {emoji_text}\n"
            f"{'─' * 40}\n"
            f"Suggestion :\n{suggestion if suggestion else '(none provided)'}\n"
        )

        ok = self._send(subject, body, success_msg="Thank you for your feedback! ✅")
        if ok:
            # Reset stars and suggestion only after confirmed send
            for star in self.ui.stars:
                star.setText("☆")
            self.ui.emoji_label.setText("🙂")
            self.ui.suggestion.clear()

    # ================= INTERNAL SEND HELPER =================
    def _send(self, subject, body, success_msg) -> bool:
        """
        Calls send_email() which returns True/False (no exceptions raised).
        Shows a success or error dialog and returns the same bool to the caller
        so the caller can decide whether to clear the form.
        """
        ok = send_email(DEVELOPER_EMAILS, subject, body)
        if ok:
            QtWidgets.QMessageBox.information(self, "Sent!", success_msg)
        else:
            QtWidgets.QMessageBox.critical(
                self, "Send Failed",
                "Could not send the email.\n\n"
                "Please check:\n"
                "  • APP_EMAIL environment variable is set\n"
                "  • APP_EMAIL_PASS environment variable is set\n"
                "  • Your internet connection is working"
            )
        return ok

    # ================= CLICK OUTSIDE =================
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)


# ================= HELPER =================
def open_help_popup(parent):
    dialog = HelpPopup(parent)

    parent_pos = parent.mapToGlobal(QtCore.QPoint(0, 0))
    x = parent_pos.x() + 10
    y = parent_pos.y() + parent.height() - dialog.height() - 10

    dialog.move(x, y)
    dialog.show()
