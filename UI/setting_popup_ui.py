from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import json


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = True
        self.setWindowTitle("Settings")
        self.resize(980, 620)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ===== Header =====
        header = QtWidgets.QFrame()
        header.setFixedHeight(48)
        h_layout = QtWidgets.QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QtWidgets.QLabel("Settings")
        title.setObjectName("title")
        h_layout.addWidget(title)
        h_layout.addStretch()

        self.btn_theme = QtWidgets.QPushButton(" Dark")
        self.btn_theme.setFixedHeight(28)
        self.btn_theme.clicked.connect(self.toggle_theme)
        h_layout.addWidget(self.btn_theme)

        root.addWidget(header)

        # ===== Main =====
        main_layout = QtWidgets.QHBoxLayout()
        self.sidebar = QtWidgets.QListWidget()
        self.sidebar.setFixedWidth(240)

        items = [
            ("General",            ":/icon/icon/layers.svg"),
            ("Appearance",         ":/icon/icon/eye.svg"),
            ("Face Recognition",   ":/icon/icon/camera.svg"),
            ("Attendance Rules",   ":/icon/icon/check-square.svg"),
            ("Database & Backup",  ":/icon/icon/database.svg"),
            ("Notifications",      ":/icon/icon/bell.svg"),
            ("Security & Access",  ":/icon/icon/shield.svg"),
        ]

        for text, icon_path in items:
            item = QtWidgets.QListWidgetItem(self.tinted_icon(icon_path), text)
            self.sidebar.addItem(item)

        self.sidebar.setCurrentRow(0)

        self.pages = QtWidgets.QStackedWidget()
        self.pages.addWidget(self.general_page())
        self.pages.addWidget(self.appearance_page())
        self.pages.addWidget(self.face_page())
        self.pages.addWidget(self.attendance_page())
        self.pages.addWidget(self.database_page())
        self.pages.addWidget(self.notifications_page())
        self.pages.addWidget(self.security_page())

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)

        container = QtWidgets.QWidget()
        container.setLayout(main_layout)
        root.addWidget(container)

        # ===== Bottom =====
        bottom = QtWidgets.QFrame()
        bottom.setFixedHeight(60)
        b_layout = QtWidgets.QHBoxLayout(bottom)
        b_layout.setContentsMargins(16, 0, 16, 0)

        self.status = QtWidgets.QLabel("")
        self.status.setObjectName("status")

        btn_save  = QtWidgets.QPushButton("Save & Apply")
        btn_close = QtWidgets.QPushButton("Close")

        btn_close.clicked.connect(self.close)
        btn_save.clicked.connect(self.save_settings)

        b_layout.addWidget(self.status)
        b_layout.addStretch()
        b_layout.addWidget(btn_save)
        b_layout.addWidget(btn_close)

        root.addWidget(bottom)
        self.setStyleSheet(self.dark_style())

    # ─────────────────────────────────────────────
    #  PAGES
    # ─────────────────────────────────────────────

    # ── General ──────────────────────────────────
    def general_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setVerticalSpacing(12)

        self.org      = QtWidgets.QLineEdit()
        self.timezone = QtWidgets.QComboBox()
        self.timezone.addItems(["UTC", "Asia/Kolkata", "Europe/London"])

        cutoff_layout = QtWidgets.QVBoxLayout()
        self.cutoff   = QtWidgets.QTimeEdit()
        cutoff_help   = QtWidgets.QLabel("After this time students will be marked Late")
        cutoff_help.setObjectName("help")
        cutoff_layout.addWidget(self.cutoff)
        cutoff_layout.addWidget(cutoff_help)

        self.autostart = QtWidgets.QCheckBox("Enable")

        path_layout = QtWidgets.QHBoxLayout()
        self.data_path = QtWidgets.QLineEdit()
        btn_browse = QtWidgets.QPushButton("Browse")
        btn_browse.clicked.connect(self.choose_folder)
        path_layout.addWidget(self.data_path)
        path_layout.addWidget(btn_browse)

        folder_layout = QtWidgets.QVBoxLayout()
        folder_help = QtWidgets.QLabel("Where system stores faces, database and logs")
        folder_help.setObjectName("help")
        self.folder_size_label = QtWidgets.QLabel("")
        self.folder_size_label.setObjectName("help")
        folder_layout.addLayout(path_layout)
        folder_layout.addWidget(folder_help)
        folder_layout.addWidget(self.folder_size_label)

        layout.addRow("Organization", self.org)
        layout.addRow("Time Zone",    self.timezone)
        layout.addRow("Cutoff Time",  cutoff_layout)
        layout.addRow("Auto Start",   self.autostart)
        layout.addRow("Data Folder",  folder_layout)
        return page

    # ── Appearance ────────────────────────────────
    def appearance_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(16)

        # ---- Theme ----
        theme_group = QtWidgets.QGroupBox("Theme")
        theme_form  = QtWidgets.QFormLayout(theme_group)
        theme_form.setSpacing(10)

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Dark (default)", "Light", "System"])
        self.theme_combo.currentTextChanged.connect(self._apply_theme_from_combo)
        theme_form.addRow("Color theme:", self.theme_combo)

        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(["English", "Spanish", "French", "German", "Japanese"])
        theme_form.addRow("Language:", self.lang_combo)

        layout.addWidget(theme_group)

        # ---- Font size ----
        font_group  = QtWidgets.QGroupBox("Typography")
        font_form   = QtWidgets.QFormLayout(font_group)
        font_form.setSpacing(10)

        font_row = QtWidgets.QHBoxLayout()
        self.font_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.font_slider.setRange(10, 20)
        self.font_slider.setValue(13)
        self.font_size_label = QtWidgets.QLabel("13px")
        self.font_size_label.setFixedWidth(36)
        self.font_size_label.setStyleSheet("color:#8B949E; font-size:11px;")
        self.font_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(f"{v}px")
        )
        font_row.addWidget(self.font_slider)
        font_row.addWidget(self.font_size_label)
        font_form.addRow("Font size:", font_row)

        layout.addWidget(font_group)

        # ---- Behavior checkboxes ----
        behavior_group  = QtWidgets.QGroupBox("Behavior")
        behavior_layout = QtWidgets.QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(8)

        self.chk_notif    = QtWidgets.QCheckBox("Enable desktop notifications")
        self.chk_autosave = QtWidgets.QCheckBox("Auto-save every 5 minutes")
        self.chk_notif.setChecked(True)
        self.chk_autosave.setChecked(True)
        behavior_layout.addWidget(self.chk_notif)
        behavior_layout.addWidget(self.chk_autosave)

        layout.addWidget(behavior_group)
        layout.addStretch()
        return page

    # ── Face Recognition ─────────────────────────
    def face_page(self):
        page   = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setVerticalSpacing(12)

        self.camera = QtWidgets.QComboBox()
        self.camera.addItems(["Camera 0", "Camera 1"])

        confidence_layout = QtWidgets.QVBoxLayout()
        slider_row        = QtWidgets.QHBoxLayout()
        self.confidence   = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.confidence.setRange(0, 100)
        self.confidence.setValue(70)
        self.confidence_percent = QtWidgets.QLabel("70%")
        self.confidence_percent.setFixedWidth(50)
        self.confidence_percent.setAlignment(QtCore.Qt.AlignCenter)
        self.confidence_percent.setStyleSheet("font-weight:bold;")
        slider_row.addWidget(self.confidence)
        slider_row.addWidget(self.confidence_percent)
        confidence_help = QtWidgets.QLabel("Higher value = stricter matching (reduces false positives)")
        confidence_help.setObjectName("help")
        confidence_layout.addLayout(slider_row)
        confidence_layout.addWidget(confidence_help)
        self.confidence.valueChanged.connect(self.update_confidence_label)

        interval_layout = QtWidgets.QVBoxLayout()
        self.interval   = QtWidgets.QSpinBox()
        self.interval.setRange(1, 10)
        interval_help   = QtWidgets.QLabel("Lower value = faster detection but higher CPU usage")
        interval_help.setObjectName("help")
        interval_layout.addWidget(self.interval)
        interval_layout.addWidget(interval_help)

        self.max_faces = QtWidgets.QSpinBox()
        self.max_faces.setRange(1, 10)

        btn_train = QtWidgets.QPushButton("Re-train Faces")

        layout.addRow("Camera",                  self.camera)
        layout.addRow("Confidence Threshold",    confidence_layout)
        layout.addRow("Recognition Interval",    interval_layout)
        layout.addRow("Max Faces",               self.max_faces)
        layout.addRow(btn_train)
        return page

    # ── Attendance Rules ─────────────────────────
    def attendance_page(self):
        page   = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)

        self.auto_mark  = QtWidgets.QCheckBox("Enable")
        self.presence   = QtWidgets.QSpinBox(); self.presence.setRange(1, 120)
        self.multi_check= QtWidgets.QCheckBox("Allow")
        self.cooldown   = QtWidgets.QSpinBox(); self.cooldown.setRange(1, 60)
        self.late_time  = QtWidgets.QTimeEdit()

        layout.addRow("Auto Mark Attendance", self.auto_mark)
        layout.addRow("Min Presence (min)",   self.presence)
        layout.addRow("Multiple Check-ins",   self.multi_check)
        layout.addRow("Duplicate Cooldown",   self.cooldown)
        layout.addRow("Late Threshold",       self.late_time)
        return page

    # ── Database & Backup ────────────────────────
    def database_page(self):
        page   = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(12)

        # ── Database folder path row (with Browse) ──
        db_label = QtWidgets.QLabel("Database Folder")
        db_label.setStyleSheet("font-weight: bold;")

        db_path_row = QtWidgets.QHBoxLayout()
        self.db_path = QtWidgets.QLineEdit()
        self.db_path.setPlaceholderText("Select folder where students.db will be stored...")
        btn_browse_db = QtWidgets.QPushButton("Browse")
        btn_browse_db.clicked.connect(self._choose_db_folder)
        db_path_row.addWidget(self.db_path)
        db_path_row.addWidget(btn_browse_db)

        db_help = QtWidgets.QLabel(
            "Changing this folder will copy your existing database to the new location "
            "and reconnect automatically. Stop attendance recording before changing."
        )
        db_help.setObjectName("help")
        db_help.setWordWrap(True)

        layout.addWidget(db_label)
        layout.addLayout(db_path_row)
        layout.addWidget(db_help)
        layout.addSpacing(15)

        # ── Action buttons ──
        btn_backup = QtWidgets.QPushButton("Backup Database")
        btn_export = QtWidgets.QPushButton("Export CSV")
        btn_clean  = QtWidgets.QPushButton("Clean Old Records")

        layout.addWidget(btn_backup)
        layout.addWidget(btn_export)
        layout.addWidget(btn_clean)
        layout.addStretch()
        return page

    # ── Notifications ─────────────────────────────
    def notifications_page(self):
        page   = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)

        self.sound = QtWidgets.QCheckBox("Enable")
        self.popup = QtWidgets.QCheckBox("Enable")
        btn_test   = QtWidgets.QPushButton("Test Notification")

        layout.addRow("Sound", self.sound)
        layout.addRow("Popup", self.popup)
        layout.addRow(btn_test)
        return page

    # ── Security & Access ─────────────────────────
    def security_page(self):
        page = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(page)
        root.setContentsMargins(30, 25, 30, 25)
        root.setSpacing(20)

        # ---- Admin credentials ----
        cred_group  = QtWidgets.QGroupBox("Admin Credentials")
        cred_form   = QtWidgets.QFormLayout(cred_group)
        cred_form.setSpacing(10)

        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.role = QtWidgets.QComboBox()
        self.role.addItems(["Admin", "Operator"])

        self.lock_time = QtWidgets.QSpinBox()
        self.lock_time.setRange(1, 60)

        cred_form.addRow("Admin Password",   self.password)
        cred_form.addRow("User Role",        self.role)
        cred_form.addRow("Lock After (min)", self.lock_time)
        root.addWidget(cred_group)

        # ---- User access table ----
        access_group  = QtWidgets.QGroupBox("User Access Management")
        access_layout = QtWidgets.QVBoxLayout(access_group)
        access_layout.setSpacing(10)

        self.ROLES = ["Admin", "Editor", "Viewer", "Guest"]
        self._users = [
            ("admin", "admin@company.com", "Admin"),
            ("alice", "alice@company.com", "Editor"),
            ("bob",   "bob@company.com",   "Viewer"),
            ("carol", "carol@company.com", "Guest"),
        ]

        self.user_table = QtWidgets.QTableWidget(0, 3)
        self.user_table.setHorizontalHeaderLabels(["Username", "Email", "Role"])
        self.user_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.user_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.user_table.horizontalHeader().setFixedHeight(32)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.user_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.user_table.setMaximumHeight(200)
        self._reload_user_table()

        access_layout.addWidget(self.user_table)

        user_btn_row = QtWidgets.QHBoxLayout()
        add_user_btn = QtWidgets.QPushButton("+ Add User")
        add_user_btn.clicked.connect(self._add_user)
        del_user_btn = QtWidgets.QPushButton("Remove Selected")
        del_user_btn.clicked.connect(self._remove_user)
        user_btn_row.addWidget(add_user_btn)
        user_btn_row.addWidget(del_user_btn)
        user_btn_row.addStretch()
        access_layout.addLayout(user_btn_row)

        root.addWidget(access_group)
        root.addStretch()
        return page

    # ─────────────────────────────────────────────
    #  USER TABLE HELPERS
    # ─────────────────────────────────────────────
    def _reload_user_table(self):
        self.user_table.setRowCount(0)
        for username, email, role in self._users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QtWidgets.QTableWidgetItem(username))
            self.user_table.setItem(row, 1, QtWidgets.QTableWidgetItem(email))
            combo = QtWidgets.QComboBox()
            combo.addItems(self.ROLES)
            combo.setCurrentText(role)
            combo.currentTextChanged.connect(lambda text, r=row: self._role_changed(r, text))
            self.user_table.setCellWidget(row, 2, combo)
            self.user_table.setRowHeight(row, 36)

    def _role_changed(self, row, new_role):
        if row < len(self._users):
            u = self._users[row]
            self._users[row] = (u[0], u[1], new_role)

    def _add_user(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add User")
        dlg.setFixedSize(300, 180)
        dlg.setStyleSheet(self.styleSheet())
        v = QtWidgets.QVBoxLayout(dlg)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(10)
        user_edit  = QtWidgets.QLineEdit(); user_edit.setPlaceholderText("Username")
        email_edit = QtWidgets.QLineEdit(); email_edit.setPlaceholderText("Email")
        role_combo = QtWidgets.QComboBox(); role_combo.addItems(self.ROLES)
        for w in (user_edit, email_edit):
            w.setStyleSheet("background:#2d2d2d; border:1px solid #3c3c3c; border-radius:6px; color:#F0F6FC; padding:6px;")
        ok_btn = QtWidgets.QPushButton("Add")
        ok_btn.clicked.connect(dlg.accept)
        v.addWidget(user_edit); v.addWidget(email_edit)
        v.addWidget(role_combo); v.addWidget(ok_btn)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            name = user_edit.text().strip()  or "new_user"
            mail = email_edit.text().strip() or f"{name}@company.com"
            role = role_combo.currentText()
            self._users.append((name, mail, role))
            self._reload_user_table()

    def _remove_user(self):
        row = self.user_table.currentRow()
        if row < 0 or row >= len(self._users):
            return
        username = self._users[row][0]
        if username == "admin":
            QtWidgets.QMessageBox.warning(self, "Not Allowed", "Cannot remove the admin account.")
            return
        confirm = QtWidgets.QMessageBox.question(
            self, "Confirm Remove", f"Remove user '{username}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            self._users.pop(row)
            self._reload_user_table()

    # ─────────────────────────────────────────────
    #  SAVE / LOAD  (stub — real logic in SettingsPopup)
    # ─────────────────────────────────────────────
    def save_settings(self):
        self.status.setText("✔ Settings saved")
        QtCore.QTimer.singleShot(2500, lambda: self.status.setText(""))

    # ─────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────
    def update_confidence_label(self, value):
        try:
            self.confidence_percent.setText(f"{value}%")
            color = "#f39c12" if value < 50 else "#2ecc71" if value < 75 else "#e74c3c"
            self.confidence_percent.setStyleSheet(f"font-weight:bold; color:{color};")
        except Exception:
            pass

    def _apply_theme_from_combo(self, text):
        if "Light" in text:
            self.setStyleSheet(self.light_style())
            self.is_dark_mode = False
        else:
            self.setStyleSheet(self.dark_style())
            self.is_dark_mode = True

    def choose_folder(self):
        """Browse for the main data folder (General page)."""
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Data Folder")
        if path:
            self.data_path.setText(path)
            self.update_folder_size(path)

    def _choose_db_folder(self):
        """Browse for the database folder (Database & Backup page)."""
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Database Folder")
        if path:
            self.db_path.setText(path)

    def update_folder_size(self, path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
        self.folder_size_label.setText(f"Folder size: {total / (1024*1024):.2f} MB")

    def tinted_icon(self, path, color=QtGui.QColor("white")):
        pixmap  = QtGui.QPixmap(path)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return QtGui.QIcon(pixmap)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.setStyleSheet(self.dark_style())
            self.btn_theme.setText(" Dark")
            icon_color = QtGui.QColor("white")
            self.btn_theme.setIcon(self.tinted_icon(":/icon/icon/moon.svg", icon_color))
            self.theme_combo.setCurrentText("Dark (default)")
        else:
            self.setStyleSheet(self.light_style())
            self.btn_theme.setText(" Light")
            icon_color = QtGui.QColor("black")
            self.btn_theme.setIcon(self.tinted_icon(":/icon/icon/sun.svg", icon_color))
            self.theme_combo.setCurrentText("Light")

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

    # ─────────────────────────────────────────────
    #  STYLESHEETS
    # ─────────────────────────────────────────────
    def dark_style(self):
        return """
        QDialog { background:#1e1e1e; border:2px solid #3c3c3c; border-radius:8px; }
        #title  { color:#ddd; font-size:16px; font-weight:600; }

        QListWidget {
            background:#252526; border:none; color:#fff; padding:10px;
        }
        QListWidget::item { padding:10px; border-radius:6px; }
        QListWidget::item:selected { background:#094771; color:white; }

        QGroupBox {
            color:#8a8a8a; border:1px solid #3c3c3c; border-radius:6px;
            margin-top:8px; font-size:11px; padding:10px;
        }
        QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }

        QLabel   { color:#ccc; font-size:13px; }
        QCheckBox { color:#fff; }
        QCheckBox::indicator { width:16px; height:16px; }
        QCheckBox::indicator:unchecked { border:1px solid #aaa; background:#2d2d2d; }
        QCheckBox::indicator:checked   { border:1px solid #0e639c; background:#0e639c; }

        QLineEdit, QComboBox, QSpinBox, QTimeEdit {
            background:#2d2d2d; border:1px solid #3c3c3c;
            padding:6px; border-radius:4px; color:white;
        }
        QSlider::groove:horizontal {
            background:#2d2d2d; border:1px solid #3c3c3c; height:6px; border-radius:3px;
        }
        QSlider::handle:horizontal {
            background:#0e639c; width:14px; height:14px; margin:-4px 0; border-radius:7px;
        }
        QSlider::sub-page:horizontal { background:#0e639c; border-radius:3px; }

        QPushButton { background:#0e639c; border:none; padding:8px 16px; border-radius:4px; color:white; }
        QPushButton:hover { background:#1177bb; }

        QTableWidget {
            background:#1e1e1e; color:#F0F6FC; border:none;
            gridline-color:#2d2d2d; font-size:12px;
        }
        QTableWidget::item { padding:6px; }
        QTableWidget::item:selected { background:#094771; color:#fff; }
        QHeaderView::section {
            background:#252526; color:#8a8a8a; border:none;
            border-bottom:1px solid #3c3c3c; padding:6px; font-size:11px;
        }

        #status { color:#0e639c; font-size:13px; }
        #help   { color:#8a8a8a; font-size:11px; }
        """

    def light_style(self):
        return """
        QDialog { background:#f5f5f5; border:1px solid #d0d0d0; border-radius:8px; }
        #title  { color:#222; font-size:16px; font-weight:600; }

        QListWidget {
            background:#ffffff; border:1px solid #ddd; color:#222; padding:10px;
        }
        QListWidget::item { padding:10px; border-radius:6px; }
        QListWidget::item:selected { background:#dbeafe; color:#000; }

        QGroupBox {
            color:#666; border:1px solid #ccc; border-radius:6px;
            margin-top:8px; font-size:11px; padding:10px;
        }
        QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }

        QLabel   { color:#333; font-size:13px; }
        QCheckBox { color:#222; }
        QCheckBox::indicator { width:16px; height:16px; }
        QCheckBox::indicator:unchecked { border:1px solid #aaa; background:#ffffff; }
        QCheckBox::indicator:checked   { border:1px solid #0078d4; background:#0078d4; }

        QLineEdit, QComboBox, QSpinBox, QTimeEdit {
            background:#ffffff; border:1px solid #ccc; padding:6px; border-radius:4px; color:#222;
        }
        QSlider::groove:horizontal {
            background:#e0e0e0; border:1px solid #ccc; height:6px; border-radius:3px;
        }
        QSlider::handle:horizontal {
            background:#0078d4; width:14px; height:14px; margin:-4px 0; border-radius:7px;
        }
        QSlider::sub-page:horizontal { background:#0078d4; border-radius:3px; }

        QPushButton { background:#0078d4; border:none; padding:8px 16px; border-radius:4px; color:white; }
        QPushButton:hover { background:#0a84ff; }

        QTableWidget {
            background:#ffffff; color:#222; border:none;
            gridline-color:#e0e0e0; font-size:12px;
        }
        QTableWidget::item { padding:6px; }
        QTableWidget::item:selected { background:#dbeafe; color:#000; }
        QHeaderView::section {
            background:#f0f0f0; color:#666; border:none;
            border-bottom:1px solid #ccc; padding:6px; font-size:11px;
        }

        #status { color:#0078d4; font-size:13px; }
        #help   { color:#666; font-size:11px; }
        """