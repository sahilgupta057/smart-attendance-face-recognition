from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from utils.open_popup_sound import PopupSound
from UI.setting_popup_ui import SettingsDialog


class SettingsPopup(SettingsDialog):

    db_path_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QtCore.QSettings("AI_Attendance_System", "AppSettings")

        # Inject report format combo if the UI file doesn't define one
        self._ensure_report_format_widget()

        self.load_settings()

        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn.text().lower().startswith("save"):
                btn.clicked.connect(self.save_settings)

        self.radius = 20
        self.btn_theme.setIcon(self.tinted_icon(":/icon/icon/moon.svg", QtGui.QColor("white")))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setWindowMask()

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        self.popup_sound = PopupSound()

        if hasattr(self, 'btn_close'):
            self.btn_close.clicked.connect(self.close)
        else:
            for btn in self.findChildren(QtWidgets.QPushButton):
                try:
                    if btn.text().lower().strip() == 'close':
                        btn.clicked.connect(self.close)
                        break
                except Exception:
                    pass

        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

    # ──────────────────────────────────────────────────────
    #  REPORT FORMAT WIDGET INJECTION
    # ──────────────────────────────────────────────────────
    def _ensure_report_format_widget(self):
        """
        If the .ui file already has a QComboBox named 'report_format', use it.
        Otherwise inject a labeled row into the Reports / General section.
        The widget is always accessible as self.report_format after this call.
        """
        existing = self.findChild(QtWidgets.QComboBox, "report_format")
        if existing:
            self.report_format = existing
            return

        # Build a small row: label + combo
        self.report_format = QtWidgets.QComboBox()
        self.report_format.setObjectName("report_format")
        self.report_format.addItems(["Excel (.xlsx)", "PDF (.pdf)"])
        self.report_format.setToolTip(
            "Default format used when clicking 'Generate Report' on the Reports page."
        )

        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.addWidget(QtWidgets.QLabel("Default report format:"))
        row_layout.addWidget(self.report_format)
        row_layout.addStretch()

        # Try to append to the first QFormLayout or QVBoxLayout we find
        # inside whichever stacked-widget page is named "Reports" or at index 0.
        target_layout = self._find_reports_page_layout()
        if target_layout:
            target_layout.addWidget(row_widget)
        else:
            # Fallback: add to the dialog's own layout
            self.layout().addWidget(row_widget)

    def _find_reports_page_layout(self):
        """
        Heuristic: look for a QStackedWidget page whose object-name or
        title contains 'report'. Returns the page's layout, or None.
        """
        for stack in self.findChildren(QtWidgets.QStackedWidget):
            for i in range(stack.count()):
                page = stack.widget(i)
                name = (page.objectName() or "").lower()
                if "report" in name or "general" in name:
                    return page.layout()
        return None

    # ──────────────────────────────────────────────────────
    #  SAVE
    # ──────────────────────────────────────────────────────
    def save_settings(self):

        # -------- General --------
        self.settings.setValue("organization", self.org.text())
        self.settings.setValue("timezone",     self.timezone.currentText())
        self.settings.setValue("cutoff_time",  self.cutoff.time().toString())
        self.settings.setValue("autostart",    self.autostart.isChecked())
        self.settings.setValue("data_folder",  self.data_path.text())

        # -------- Face Recognition --------
        self.settings.setValue("camera",    self.camera.currentIndex())
        self.settings.setValue("confidence", self.confidence.value())
        self.settings.setValue("interval",   self.interval.value())
        self.settings.setValue("max_faces",  self.max_faces.value())

        # -------- Attendance --------
        self.settings.setValue("auto_mark",  self.auto_mark.isChecked())
        self.settings.setValue("presence",   self.presence.value())
        self.settings.setValue("multi_check",self.multi_check.isChecked())
        self.settings.setValue("cooldown",   self.cooldown.value())
        self.settings.setValue("late_time",  self.late_time.time().toString())

        # -------- Database --------
        new_db_path = self.db_path.text().strip()
        old_db_path = self.settings.value("db_path", "")
        self.settings.setValue("db_path", new_db_path)

        # -------- Notifications --------
        self.settings.setValue("sound", self.sound.isChecked())
        self.settings.setValue("popup", self.popup.isChecked())

        # -------- Security --------
        self.settings.setValue("role",      self.role.currentText())
        self.settings.setValue("lock_time", self.lock_time.value())

        # -------- Appearance --------
        self.settings.setValue("theme",     self.theme_combo.currentText())
        self.settings.setValue("language",  self.lang_combo.currentText())
        self.settings.setValue("font_size", self.font_slider.value())

        # -------- Reports --------
        self.settings.setValue("report_format", self.report_format.currentText())

        if new_db_path and new_db_path != old_db_path:
            self.db_path_changed.emit(new_db_path)

        self.status.setText("✔ Settings saved")
        QtCore.QTimer.singleShot(2500, lambda: self.status.setText(""))

    # ──────────────────────────────────────────────────────
    #  LOAD
    # ──────────────────────────────────────────────────────
    def load_settings(self):

        # -------- General --------
        self.org.setText(self.settings.value("organization", ""))
        self.timezone.setCurrentText(self.settings.value("timezone", "Asia/Kolkata"))

        cutoff = self.settings.value("cutoff_time")
        if cutoff:
            self.cutoff.setTime(QtCore.QTime.fromString(cutoff))

        self.autostart.setChecked(self.settings.value("autostart", False, type=bool))
        self.data_path.setText(self.settings.value("data_folder", ""))

        # -------- Face Recognition --------
        self.camera.setCurrentIndex(int(self.settings.value("camera", 0)))
        self.confidence.setValue(int(self.settings.value("confidence", 70)))
        self.interval.setValue(int(self.settings.value("interval", 2)))
        self.max_faces.setValue(int(self.settings.value("max_faces", 3)))

        # -------- Attendance --------
        self.auto_mark.setChecked(self.settings.value("auto_mark", True, type=bool))
        self.presence.setValue(int(self.settings.value("presence", 10)))
        self.multi_check.setChecked(self.settings.value("multi_check", False, type=bool))
        self.cooldown.setValue(int(self.settings.value("cooldown", 5)))

        late = self.settings.value("late_time")
        if late:
            self.late_time.setTime(QtCore.QTime.fromString(late))

        # -------- Database --------
        self.db_path.setText(self.settings.value("db_path", ""))

        # -------- Notifications --------
        self.sound.setChecked(self.settings.value("sound", True, type=bool))
        self.popup.setChecked(self.settings.value("popup", True, type=bool))

        # -------- Security --------
        self.role.setCurrentText(self.settings.value("role", "Admin"))
        self.lock_time.setValue(int(self.settings.value("lock_time", 10)))

        # -------- Appearance --------
        self.theme_combo.setCurrentText(self.settings.value("theme", "Dark (default)"))
        self.lang_combo.setCurrentText(self.settings.value("language", "English"))
        self.font_slider.setValue(int(self.settings.value("font_size", 13)))

        # -------- Reports (default = Excel) --------
        saved_format = self.settings.value("report_format", "Excel (.xlsx)")
        idx = self.report_format.findText(saved_format)
        if idx >= 0:
            self.report_format.setCurrentIndex(idx)

    # ──────────────────────────────────────────────────────
    #  ROUNDED CORNERS
    # ──────────────────────────────────────────────────────
    def setWindowMask(self):
        rect   = QtCore.QRectF(self.rect())
        path   = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # ──────────────────────────────────────────────────────
    #  EVENTS
    # ──────────────────────────────────────────────────────
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)

    # ──────────────────────────────────────────────────────
    #  THEME TOGGLE
    # ──────────────────────────────────────────────────────
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode

        if self.is_dark_mode:
            self.setStyleSheet(self.dark_style())
            self.btn_theme.setText(" Dark")
            icon_color = QtGui.QColor("white")
            self.btn_theme.setIcon(self.tinted_icon(":/icon/icon/moon.svg", icon_color))
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText("Dark (default)")
            self.theme_combo.blockSignals(False)
        else:
            self.setStyleSheet(self.light_style())
            self.btn_theme.setText(" Light")
            icon_color = QtGui.QColor("black")
            self.btn_theme.setIcon(self.tinted_icon(":/icon/icon/sun.svg", icon_color))
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText("Light")
            self.theme_combo.blockSignals(False)

        paths = [
            ":/icon/icon/layers.svg",
            ":/icon/icon/eye.svg",
            ":/icon/icon/camera.svg",
            ":/icon/icon/check-square.svg",
            ":/icon/icon/database.svg",
            ":/icon/icon/bell.svg",
            ":/icon/icon/shield.svg",
        ]
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            item.setIcon(self.tinted_icon(paths[i], icon_color))


def open_settings_popup(parent):
    """Open settings popup anchored to the bottom-left corner of parent."""
    dialog = SettingsPopup(parent)

    parent_geo = parent.geometry()
    x = parent_geo.x() + 10
    y = parent_geo.y() + parent_geo.height() - dialog.height() - 10
    dialog.move(x, y)

    dialog.show()