import os
from PyQt5 import QtWidgets, QtGui, QtCore

from UI.student_details_popup_ui import Ui_StudentDetailsPopup
from utils.open_popup_sound import PopupSound


class StudentDetailsPopup(QtWidgets.QDialog):
    def __init__(self, student_data, db_instance, parent=None):
        super().__init__(parent)

        self.db = db_instance
        self.student_data = student_data
        self.popup_sound = PopupSound()

        self.ui = Ui_StudentDetailsPopup()
        self.ui.setupUi(self)

        self.populate_student_info()
        self.set_student_image(student_data.get("face_image"))
        self.load_attendance()

        self.ui.close_btn.clicked.connect(self.accept)

    # ================= STUDENT INFO =================
    def populate_student_info(self):
        for label, value in [
            ("Name", self.student_data.get("name", "Unknown")),
            ("ID", self.student_data.get("id", "Unknown")),
            ("Department", self.student_data.get("dept", "Unknown")),
            ("Year", self.student_data.get("Year", "Unknown")),
            ("Email", self.student_data.get("email", "Unknown")),
        ]:
            lbl = QtWidgets.QLabel(f"<b>{label}:</b> {value}")
            lbl.setStyleSheet("color:#eee; font-size:15px;")
            self.ui.info_layout.addWidget(lbl)

    # ================= ATTENDANCE =================
    def load_attendance(self):
        attendance = self.db.get_attendance(self.student_data.get("id"))
        self.ui.att_table.setRowCount(len(attendance))

        for row, record in enumerate(attendance):
            self.ui.att_table.setItem(row, 0, QtWidgets.QTableWidgetItem(record.get("date", "")))
            self.ui.att_table.setItem(row, 1, QtWidgets.QTableWidgetItem(record.get("time", "")))
            self.ui.att_table.setItem(row, 2, QtWidgets.QTableWidgetItem(record.get("status", "")))

    # ================= IMAGE =================
    def set_student_image(self, image_path):
        size = 200
        pixmap = None

        if image_path and os.path.exists(image_path):
            pixmap = QtGui.QPixmap(image_path)
        else:
            default_path = os.path.join(
                os.path.dirname(__file__), "../icon/default_face.png"
            )
            if os.path.exists(default_path):
                pixmap = QtGui.QPixmap(default_path)

        if pixmap:
            self.ui.image_label.setPixmap(self.circular_pixmap(pixmap, size))
        else:
            self.ui.image_label.setText("No Image Available")
            self.ui.image_label.setStyleSheet("color:#888; font-size:14px;")

    def circular_pixmap(self, pixmap, size):
        pixmap = pixmap.scaled(
            size, size,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )

        result = QtGui.QPixmap(size, size)
        result.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(result)
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing |
            QtGui.QPainter.SmoothPixmapTransform
        )

        path = QtGui.QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result

    # ================= EVENTS =================
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()
