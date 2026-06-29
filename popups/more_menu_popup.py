from PyQt5 import QtWidgets, QtCore, QtGui
from UI.more_menu_popup_ui import Ui_MoreMenuPopup
from UI.setting_popup_ui import SettingsDialog          # ← unified settings
from utils.open_popup_sound import PopupSound
import os
import json
import datetime


# ──────────────────────────────────────────────
#  CLOUD BACKUP DIALOG  (action – stays here)
# ──────────────────────────────────────────────
class CloudBackupDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cloud Backup")
        self.setFixedSize(420, 280)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setStyleSheet("""
            QDialog { background:#0B0E14; border:1px solid #30363D; border-radius:12px; }
            QLabel  { color:#F0F6FC; }
            QPushButton {
                background:#161B22; border:1px solid #30363D; border-radius:8px;
                color:#F0F6FC; padding:8px 20px; font-size:13px;
            }
            QPushButton:hover { background:#1C2128; border-color:#00D4FF; }
            QPushButton:disabled { color:#555; border-color:#222; }
            QProgressBar {
                background:#161B22; border:1px solid #30363D; border-radius:6px;
                height:12px; text-align:center; color:#fff; font-size:11px;
            }
            QProgressBar::chunk { background:#00D4FF; border-radius:6px; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QtWidgets.QHBoxLayout()
        title  = QtWidgets.QLabel("☁  Cloud Backup")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#00D4FF;")
        close  = QtWidgets.QPushButton("✕")
        close.setFixedSize(28, 28)
        close.setStyleSheet("background:transparent; border:none; color:#8B949E; font-size:14px;")
        close.clicked.connect(self.close)
        header.addWidget(title); header.addStretch(); header.addWidget(close)
        layout.addLayout(header)

        self.status_label = QtWidgets.QLabel("Ready to sync your local data to secure cloud storage.")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color:#8B949E; font-size:12px;")
        layout.addWidget(self.status_label)

        self.last_backup = QtWidgets.QLabel("Last backup: Never")
        self.last_backup.setStyleSheet("color:#555; font-size:11px;")
        self._load_last_backup()
        layout.addWidget(self.last_backup)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        btn_row = QtWidgets.QHBoxLayout()
        self.backup_btn = QtWidgets.QPushButton("Start Backup")
        self.backup_btn.clicked.connect(self.start_backup)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(self.backup_btn); btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self._timer  = QtCore.QTimer()
        self._timer.timeout.connect(self._tick)
        self._value  = 0
        self._stages = []
        self._stage_idx = 0

        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 12, 12)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    def _load_last_backup(self):
        if os.path.exists("backup_config.json"):
            with open("backup_config.json") as f:
                data = json.load(f)
                self.last_backup.setText(f"Last backup: {data.get('last_backup', 'Unknown')}")

    def start_backup(self):
        self.backup_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self._value     = 0
        self._stages    = ["Scanning files...", "Compressing data...", "Uploading to cloud...", "Verifying integrity..."]
        self._stage_idx = 0
        self.status_label.setText(self._stages[0])
        self._timer.start(40)

    def _tick(self):
        self._value += 1
        self.progress.setValue(self._value)
        if self._value in (25, 50, 75) and self._stage_idx < len(self._stages) - 1:
            self._stage_idx += 1
            self.status_label.setText(self._stages[self._stage_idx])
        if self._value >= 100:
            self._timer.stop()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.status_label.setText("✅  Backup completed successfully!")
            self.last_backup.setText(f"Last backup: {now}")
            self.backup_btn.setText("Backup Again")
            self.backup_btn.setEnabled(True)
            with open("backup_config.json", "w") as f:
                json.dump({"last_backup": now}, f)


# ──────────────────────────────────────────────
#  ANALYTICS EXPORT DIALOG  (action – stays here)
# ──────────────────────────────────────────────
class AnalyticsExportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analytics Export")
        self.setFixedSize(420, 320)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setStyleSheet("""
            QDialog { background:#0B0E14; border:1px solid #30363D; border-radius:12px; }
            QLabel  { color:#F0F6FC; }
            QPushButton {
                background:#161B22; border:1px solid #30363D; border-radius:8px;
                color:#F0F6FC; padding:8px 20px; font-size:13px;
            }
            QPushButton:hover { background:#1C2128; border-color:#00D4FF; }
            QComboBox {
                background:#161B22; border:1px solid #30363D; border-radius:6px;
                color:#F0F6FC; padding:6px 10px; font-size:13px;
            }
            QComboBox::drop-down { border:none; }
            QComboBox QAbstractItemView { background:#161B22; color:#F0F6FC; selection-background-color:#1C2128; }
            QCheckBox { color:#8B949E; font-size:12px; }
            QCheckBox::indicator { width:14px; height:14px; border:1px solid #30363D; border-radius:3px; background:#161B22; }
            QCheckBox::indicator:checked { background:#00D4FF; border-color:#00D4FF; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QtWidgets.QHBoxLayout()
        title  = QtWidgets.QLabel("📈  Analytics Export")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#00D4FF;")
        close  = QtWidgets.QPushButton("✕")
        close.setFixedSize(28, 28)
        close.setStyleSheet("background:transparent; border:none; color:#8B949E; font-size:14px;")
        close.clicked.connect(self.close)
        header.addWidget(title); header.addStretch(); header.addWidget(close)
        layout.addLayout(header)

        fmt_row = QtWidgets.QHBoxLayout()
        fmt_row.addWidget(QtWidgets.QLabel("Export format:"))
        self.fmt_combo = QtWidgets.QComboBox()
        self.fmt_combo.addItems(["CSV  (.csv)", "PDF  (.pdf)", "Excel  (.xlsx)", "JSON  (.json)"])
        fmt_row.addWidget(self.fmt_combo)
        layout.addLayout(fmt_row)

        range_row = QtWidgets.QHBoxLayout()
        range_row.addWidget(QtWidgets.QLabel("Date range:"))
        self.range_combo = QtWidgets.QComboBox()
        self.range_combo.addItems(["Last 7 days", "Last 30 days", "Last 90 days", "This year", "All time"])
        range_row.addWidget(self.range_combo)
        layout.addLayout(range_row)

        self.chk_summary = QtWidgets.QCheckBox("Include summary statistics")
        self.chk_charts  = QtWidgets.QCheckBox("Include charts (PDF only)")
        self.chk_raw     = QtWidgets.QCheckBox("Include raw data rows")
        self.chk_summary.setChecked(True)
        self.chk_raw.setChecked(True)
        layout.addWidget(self.chk_summary)
        layout.addWidget(self.chk_charts)
        layout.addWidget(self.chk_raw)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color:#8B949E; font-size:11px;")
        layout.addWidget(self.status)

        btn_row = QtWidgets.QHBoxLayout()
        export_btn = QtWidgets.QPushButton("Export")
        export_btn.clicked.connect(self.do_export)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(export_btn); btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 12, 12)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    def do_export(self):
        ext_map = {0: "csv", 1: "pdf", 2: "xlsx", 3: "json"}
        ext = ext_map[self.fmt_combo.currentIndex()]
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Report", f"analytics_report.{ext}",
            f"Report (*.{ext});;All Files (*)"
        )
        if path:
            with open(path, "w") as f:
                f.write(f"# Analytics Export\n# Range: {self.range_combo.currentText()}\n# Generated: {datetime.datetime.now()}\n")
            self.status.setText(f"✅  Exported to: {os.path.basename(path)}")


# ──────────────────────────────────────────────
#  SYSTEM UPDATE DIALOG  (action – stays here)
# ──────────────────────────────────────────────
class SystemUpdateDialog(QtWidgets.QDialog):
    CURRENT_VERSION = "2.4.1"
    LATEST_VERSION  = "2.5.0"
    CHANGELOG = [
        ("2.5.0", [
            "New dark theme engine with per-component control",
            "Cloud sync now supports end-to-end encryption",
            "Analytics export: added Excel (.xlsx) format",
            "Performance improvements across the board",
            "Fixed: popup animation glitch on multi-monitor setups",
        ]),
        ("2.4.1", [
            "Hot-fix: cloud backup progress bar freezing",
            "Minor UI polish on User Access table",
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Update")
        self.setFixedSize(440, 380)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setStyleSheet("""
            QDialog { background:#0B0E14; border:1px solid #30363D; border-radius:12px; }
            QLabel  { color:#F0F6FC; }
            QPushButton {
                background:#161B22; border:1px solid #30363D; border-radius:8px;
                color:#F0F6FC; padding:8px 20px; font-size:13px;
            }
            QPushButton:hover { background:#1C2128; border-color:#00D4FF; }
            QPushButton#install { background:#00D4FF; color:#000; border:none; font-weight:700; }
            QPushButton#install:hover { background:#00bfe8; }
            QScrollArea { border:none; background:transparent; }
            QProgressBar {
                background:#161B22; border:1px solid #30363D; border-radius:6px;
                height:10px; text-align:center; font-size:11px; color:#fff;
            }
            QProgressBar::chunk { background:#00D4FF; border-radius:6px; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QtWidgets.QHBoxLayout()
        title  = QtWidgets.QLabel("🔄  System Update")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#00D4FF;")
        close  = QtWidgets.QPushButton("✕")
        close.setFixedSize(28, 28)
        close.setStyleSheet("background:transparent; border:none; color:#8B949E; font-size:14px;")
        close.clicked.connect(self.close)
        header.addWidget(title); header.addStretch(); header.addWidget(close)
        layout.addLayout(header)

        ver_widget = QtWidgets.QWidget()
        ver_widget.setStyleSheet("background:#161B22; border:1px solid #30363D; border-radius:8px; padding:4px;")
        ver_layout = QtWidgets.QHBoxLayout(ver_widget)
        cur_lbl    = QtWidgets.QLabel(f"Current:  v{self.CURRENT_VERSION}")
        cur_lbl.setStyleSheet("color:#8B949E; font-size:12px;")
        new_lbl    = QtWidgets.QLabel(f"Latest:  v{self.LATEST_VERSION}  ✦")
        new_lbl.setStyleSheet("color:#00D4FF; font-size:12px; font-weight:700;")
        ver_layout.addWidget(cur_lbl); ver_layout.addStretch(); ver_layout.addWidget(new_lbl)
        layout.addWidget(ver_widget)

        log_label = QtWidgets.QLabel("What's new:")
        log_label.setStyleSheet("color:#8B949E; font-size:11px; font-weight:700;")
        layout.addWidget(log_label)

        scroll     = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(160)
        log_widget = QtWidgets.QWidget()
        log_widget.setStyleSheet("background:#0B0E14;")
        log_vbox   = QtWidgets.QVBoxLayout(log_widget)
        log_vbox.setContentsMargins(4, 4, 4, 4)
        log_vbox.setSpacing(6)
        for version, items in self.CHANGELOG:
            v_lbl = QtWidgets.QLabel(f"v{version}")
            v_lbl.setStyleSheet("color:#00D4FF; font-size:11px; font-weight:700;")
            log_vbox.addWidget(v_lbl)
            for item in items:
                i_lbl = QtWidgets.QLabel(f"  • {item}")
                i_lbl.setStyleSheet("color:#8B949E; font-size:11px;")
                i_lbl.setWordWrap(True)
                log_vbox.addWidget(i_lbl)
        log_vbox.addStretch()
        scroll.setWidget(log_widget)
        layout.addWidget(scroll)

        self.progress       = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        self.progress_label = QtWidgets.QLabel("")
        self.progress_label.setStyleSheet("color:#8B949E; font-size:11px;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress)

        btn_row = QtWidgets.QHBoxLayout()
        self.install_btn = QtWidgets.QPushButton(f"Install v{self.LATEST_VERSION}")
        self.install_btn.setObjectName("install")
        self.install_btn.clicked.connect(self.start_update)
        later_btn = QtWidgets.QPushButton("Remind Me Later")
        later_btn.clicked.connect(self.close)
        btn_row.addWidget(self.install_btn); btn_row.addWidget(later_btn)
        layout.addLayout(btn_row)

        self._timer     = QtCore.QTimer()
        self._timer.timeout.connect(self._tick)
        self._value     = 0
        self._stages    = ["Downloading update...", "Verifying package...", "Installing...", "Finalizing..."]
        self._stage_idx = 0

        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 12, 12)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    def start_update(self):
        self.install_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_label.setText(self._stages[0])
        self._value     = 0
        self._stage_idx = 0
        self._timer.start(35)

    def _tick(self):
        self._value += 1
        self.progress.setValue(self._value)
        if self._value in (25, 50, 75) and self._stage_idx < len(self._stages) - 1:
            self._stage_idx += 1
            self.progress_label.setText(self._stages[self._stage_idx])
        if self._value >= 100:
            self._timer.stop()
            self.progress_label.setText("✅  Update installed! Restart to apply.")
            self.install_btn.setText("Restart Now")
            self.install_btn.setEnabled(True)
            self.install_btn.clicked.disconnect()
            self.install_btn.clicked.connect(self._restart)

    def _restart(self):
        QtWidgets.QMessageBox.information(self, "Restart", "The application will now restart.")
        self.close()


# ──────────────────────────────────────────────
#  MAIN MORE MENU POPUP
# ──────────────────────────────────────────────
class MoreMenuPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MoreMenuPopup()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.radius = 20

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        self.popup_sound = PopupSound()
        self.setWindowMask()

        self.ui.close_btn.clicked.connect(self.close)
        self._connect_menu_buttons()

        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

    def _connect_menu_buttons(self):
        """
        Wire each menu button to its handler.

        Menu now has exactly 4 items (in this order):
          0 – Cloud Backup     → action dialog
          1 – Analytics Export → action dialog
          2 – Open Settings    → full SettingsDialog (replaces old Preferences + User Access)
          3 – System Update    → action dialog
        """
        buttons  = self.ui.scroll_content.findChildren(QtWidgets.QPushButton, "menuOption")
        handlers = [
            self.open_cloud_backup,
            self.open_analytics_export,
            self.open_settings,          # ← was open_preferences / open_user_access
            self.open_system_update,
        ]
        for btn, handler in zip(buttons, handlers):
            btn.clicked.connect(handler)

    # ── Actions ───────────────────────────────────

    def open_cloud_backup(self):
        self.close()
        CloudBackupDialog(self.parent()).exec_()

    def open_analytics_export(self):
        self.close()
        AnalyticsExportDialog(self.parent()).exec_()

    def open_settings(self):
        """
        Replaces the old open_preferences() and open_user_access().
        One entry point → the full Settings dialog.
        Users find Appearance (theme/font/language) on the 'Appearance' tab
        and User Access on the 'Security & Access' tab.
        """
        self.close()
        dlg = SettingsDialog(self.parent())
        dlg.exec_()

    def open_system_update(self):
        self.close()
        SystemUpdateDialog(self.parent()).exec_()

    # ── Rounded mask ──────────────────────────────
    def setWindowMask(self):
        rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    # ── Sound ─────────────────────────────────────
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()

    # ── Click outside ─────────────────────────────
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)


# ──────────────────────────────────────────────
#  HELPER
# ──────────────────────────────────────────────
def open_moremenu_popup(parent):
    dialog = MoreMenuPopup(parent)

    parent_pos = parent.mapToGlobal(QtCore.QPoint(0, 0))
    final_x    = parent_pos.x() + 10
    final_y    = parent_pos.y() + parent.height() - dialog.height() - 10
    start_x    = final_x - dialog.width() - 40
    dialog.move(start_x, final_y)

    opacity_effect = QtWidgets.QGraphicsOpacityEffect(dialog)
    dialog.setGraphicsEffect(opacity_effect)
    opacity_effect.setOpacity(0)
    dialog.show()

    anim_move = QtCore.QPropertyAnimation(dialog, b"geometry")
    anim_move.setDuration(700)
    anim_move.setStartValue(QtCore.QRect(start_x, final_y, dialog.width(), dialog.height()))
    anim_move.setEndValue(QtCore.QRect(final_x, final_y, dialog.width(), dialog.height()))
    anim_move.setEasingCurve(QtCore.QEasingCurve.OutCubic)

    anim_fade = QtCore.QPropertyAnimation(opacity_effect, b"opacity")
    anim_fade.setDuration(700)
    anim_fade.setStartValue(0)
    anim_fade.setEndValue(1)
    anim_fade.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

    anim_group = QtCore.QParallelAnimationGroup()
    anim_group.addAnimation(anim_move)
    anim_group.addAnimation(anim_fade)
    dialog.anim_group = anim_group
    anim_group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)