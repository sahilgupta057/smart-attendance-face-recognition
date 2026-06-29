import os, json, shutil
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from UI.profile_popup_ui import Ui_ProfilePopup
from utils.open_popup_sound import PopupSound
from utils.auth_db import AuthDatabase
from popups.confirm_password_popup import ConfirmPasswordPopup
import cv2


class ProfilePopup(QtWidgets.QDialog):
    def __init__(self, user_data, signin_file="signin.json", parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.signin_file = signin_file
        self.radius = 20
        self.data_file = "user_profile.json"

        # Load UI
        self.ui = Ui_ProfilePopup()
        self.ui.setupUi(self)

        # Window mask and sound
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setWindowMask()
        self.popup_sound = PopupSound()

        # Connections
        self.ui.edit_btn.clicked.connect(self.enable_editing)
        self.ui.save_btn.clicked.connect(self.save_data)
        self.ui.ok_btn.clicked.connect(self.close)
        self.ui.delete_btn.clicked.connect(self.confirm_and_delete_account)

        # Load data
        self.load_data()
        self.set_read_only(True)

        # Outside click
        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

    # ------------------------------------------------------------------ #
    #  Window Mask
    # ------------------------------------------------------------------ #
    def setWindowMask(self):
        rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # ------------------------------------------------------------------ #
    #  Sound
    # ------------------------------------------------------------------ #
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()

    # ------------------------------------------------------------------ #
    #  Read-only toggle
    # ------------------------------------------------------------------ #
    def set_read_only(self, readonly: bool):
        self.ui.name_input.setReadOnly(readonly)
        self.ui.email_input.setReadOnly(readonly)
        self.ui.role_input.setReadOnly(readonly)
        self.ui.last_login_input.setReadOnly(readonly)
        self.ui.save_btn.setVisible(not readonly)

        if readonly:
            self.ui.profile_pic.setCursor(QtCore.Qt.ArrowCursor)
            self.ui.profile_pic.mousePressEvent = lambda event: None
        else:
            self.ui.profile_pic.setCursor(QtCore.Qt.PointingHandCursor)
            self.ui.profile_pic.mousePressEvent = self.change_profile_picture

    # ------------------------------------------------------------------ #
    #  Enable Editing
    # ------------------------------------------------------------------ #
    def enable_editing(self):
        self.set_read_only(False)

    # ------------------------------------------------------------------ #
    #  Profile Picture helpers
    # ------------------------------------------------------------------ #
    def _make_circle_pixmap(self, source_path: str, size: int = 100, border: int = 4) -> QtGui.QPixmap:
        inner = size - border * 2

        raw = QtGui.QPixmap(source_path).scaled(
            inner, inner,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation,
        )

        if raw.width() != inner or raw.height() != inner:
            x_off = (raw.width() - inner) // 2
            y_off = (raw.height() - inner) // 2
            raw = raw.copy(x_off, y_off, inner, inner)

        circle_photo = QtGui.QPixmap(inner, inner)
        circle_photo.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(circle_photo)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        clip = QtGui.QPainterPath()
        clip.addEllipse(0, 0, inner, inner)
        p.setClipPath(clip)
        p.drawPixmap(0, 0, raw)
        p.end()

        final = QtGui.QPixmap(size, size)
        final.fill(QtCore.Qt.transparent)
        p2 = QtGui.QPainter(final)
        p2.setRenderHint(QtGui.QPainter.Antialiasing)
        p2.setBrush(QtGui.QColor("#2196F3"))
        p2.setPen(QtCore.Qt.NoPen)
        p2.drawEllipse(0, 0, size, size)
        p2.drawPixmap(border, border, circle_photo)
        p2.end()

        return final

    def change_profile_picture(self, event):
        menu = QtWidgets.QMenu(self)
        upload_action = menu.addAction("Upload Image")
        camera_action = menu.addAction("Capture Photo")
        action = menu.exec_(QtGui.QCursor.pos())

        if action == upload_action:
            self.select_image()
        elif action == camera_action:
            self.capture_photo()

    def select_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Profile Picture",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if file_path:
            self.save_profile_image(file_path)

    def capture_photo(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            QtWidgets.QMessageBox.warning(self, "Camera Error", "Cannot access webcam.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Press SPACE to Capture", frame)
            key = cv2.waitKey(1)

            if key == 32:
                os.makedirs("profile_images", exist_ok=True)
                image_path = os.path.join(
                    "profile_images",
                    f"{self.user_data['email'].replace('@', '_')}.jpg",
                )
                cv2.imwrite(image_path, frame)
                self.save_profile_image(image_path)
                break

            elif key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def save_profile_image(self, source_path: str):
        email = self.user_data["email"]

        os.makedirs("profile_images", exist_ok=True)

        ext = os.path.splitext(source_path)[1]
        filename = email.replace("@", "_").replace(".", "_") + ext
        destination = os.path.join("profile_images", filename)

        if source_path != destination:
            shutil.copy(source_path, destination)

        pixmap = self._make_circle_pixmap(destination, size=100, border=4)
        self.ui.profile_pic.setPixmap(pixmap)

        auth = AuthDatabase()
        auth.update_profile_image(email, destination)

    # ------------------------------------------------------------------ #
    #  Load Data
    # ------------------------------------------------------------------ #
    def load_data(self):
        self.ui.name_input.setText(self.user_data.get("name", ""))
        self.ui.email_input.setText(self.user_data.get("email", ""))
        self.ui.role_input.setText(self.user_data.get("role", "User"))
        self.ui.last_login_input.setText(
            self.user_data.get(
                "last_login",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

        auth = AuthDatabase()
        image_path = auth.get_profile_image(self.user_data["email"])

        if image_path and os.path.exists(image_path):
            pixmap = self._make_circle_pixmap(image_path, size=100, border=4)
            self.ui.profile_pic.setPixmap(pixmap)

    # ------------------------------------------------------------------ #
    #  Save Data  — uses ConfirmPasswordPopup, NOT the full LoginPopup
    # ------------------------------------------------------------------ #
    def save_data(self):
        # Always verify against the original logged-in email,
        # even if the user edited the email field.
        current_email = self.user_data.get("email", "").strip()

        confirm_dialog = ConfirmPasswordPopup(current_email, parent=self)

        if confirm_dialog.exec_() == QtWidgets.QDialog.Accepted and confirm_dialog.valid:
            new_email = self.ui.email_input.text().strip()

            data = {
                "name": self.ui.name_input.text(),
                "email": new_email,
                "role": self.ui.role_input.text(),
                "last_login": self.ui.last_login_input.text(),
            }

            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=4)

            # Keep user_data in sync if email was changed
            if new_email and new_email != current_email:
                self.user_data["email"] = new_email

            QtWidgets.QMessageBox.information(self, "Saved", "Profile data saved successfully!")
            self.set_read_only(True)
        else:
            QtWidgets.QMessageBox.information(self, "Not Saved", "Profile data was not saved.")
            self.load_data()
            self.set_read_only(True)

    # ------------------------------------------------------------------ #
    #  Delete Account
    # ------------------------------------------------------------------ #
    def confirm_and_delete_account(self):
        email = self.ui.email_input.text().strip() or self.user_data.get("email")
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "No email found for this account.")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Account",
            "This will permanently delete your account and all associated data. Continue?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        safe_email = email.replace("@", "_").replace(".", "_")
        try:
            shutil.rmtree(os.path.join("data", safe_email))
        except Exception as e:
            print(f"Error deleting data dir: {e}")

        auth = AuthDatabase()
        if auth.delete_user(email):
            if os.path.exists("current_user.json"):
                with open("current_user.json", "r") as f:
                    cu = json.load(f)
                if cu.get("email") == email:
                    os.remove("current_user.json")
            QtWidgets.QMessageBox.information(self, "Deleted", "Your account and data have been deleted.")
            if self.parent() and hasattr(self.parent(), "restart_application"):
                self.parent().restart_application()
            else:
                QtWidgets.QApplication.quit()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Account deletion failed.")

    # ------------------------------------------------------------------ #
    #  Outside-click close
    # ------------------------------------------------------------------ #
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)


# ======================================================================= #
#  HELPER
# ======================================================================= #
def open_profile_popup(parent, user_data):
    dialog = ProfilePopup(user_data, parent=parent)

    parent_pos = parent.mapToGlobal(QtCore.QPoint(0, 0))
    final_x = parent_pos.x() + parent.width() - dialog.width() - 10
    final_y = parent_pos.y() + parent.height() - dialog.height() - 10
    start_x = final_x - dialog.width() - 40

    dialog.move(start_x, final_y)

    opacity_effect = QtWidgets.QGraphicsOpacityEffect(dialog)
    dialog.setGraphicsEffect(opacity_effect)
    opacity_effect.setOpacity(0)
    dialog.show()

    # Slide animation
    anim_move = QtCore.QPropertyAnimation(dialog, b"geometry")
    anim_move.setDuration(700)
    anim_move.setStartValue(QtCore.QRect(start_x, final_y, dialog.width(), dialog.height()))
    anim_move.setEndValue(QtCore.QRect(final_x, final_y, dialog.width(), dialog.height()))
    anim_move.setEasingCurve(QtCore.QEasingCurve.OutCubic)

    # Fade-in animation
    anim_fade = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
    anim_fade.setDuration(700)
    anim_fade.setStartValue(0)
    anim_fade.setEndValue(1)
    anim_fade.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

    # Group animations
    anim_group = QtCore.QParallelAnimationGroup()
    anim_group.addAnimation(anim_move)
    anim_group.addAnimation(anim_fade)
    dialog.anim_group = anim_group
    anim_group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)