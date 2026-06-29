import sys
import os
import re
from popups.chatbot_popup import ChatbotWidget


# ---- Fix paths for embedded Python ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_PACKAGES = os.path.join(BASE_DIR, "python-embedded", "Lib", "site-packages")

if SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.chdir(BASE_DIR)

# ---- Fix PyQt5 plugin path ----
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
    SITE_PACKAGES, "PyQt5", "Qt5", "plugins", "platforms"
)

import cv2
import threading
from datetime import datetime, timedelta

# PyQt5 Core
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEvent
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPen, QFont, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel
from PyQt5.QtChart import (
    QChart, QChartView, QPieSeries, QLineSeries,
    QCategoryAxis, QValueAxis
)

# External Libraries
import face_recognition
import pyttsx3
from PIL import Image
import qdarkstyle

# Project UI
from UI.interface2 import *
from UI.information_popup_ui import Ui_InformationPopup

# Custom Widgets
from Custom_Widgets.Widgets import *

# Popups
from popups.login_popup import *
from popups.logout_popup import *
from popups.signup_popup import *
from popups.help_popup import *
from popups.information_popup import *
from popups.setting_popup import *
from popups.profile_popup import *
from popups.more_menu_popup import *
from popups.view_reports_popup import ViewReportsPopup
from popups.camera_capture_popup import CameraCapturePopup
from popups.student_details_popup import *

# Utilities
from utils.database import *
from utils.main_dashboard import *
from utils.toast_notification import *
from utils.email_sender import *
from utils.resource_path import *
from utils.daily_report_scheduler import initialize_scheduler, stop_scheduler
from utils.reports_page import AttendanceReportsPage

# Camera Modules
from camera.face_recognition import *
from camera.camera_thread import *

# Attendance Manager
from attendance_manager import AttendanceManager


def speak_message_async(message):
    """Speak a message in a separate thread without blocking the GUI."""
    def worker():
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'en' in voice.id:
                engine.setProperty('voice', voice.id)
                break
        engine.say(message)
        engine.runAndWait()
        engine.stop()
    threading.Thread(target=worker, daemon=True).start()


class InfoDialog(QtWidgets.QDialog, Ui_InformationPopup):
    def __init__(self, recognition_thread):
        super().__init__()
        self.setupUi(self)
        self.recognition_thread = recognition_thread
        self.recognition_thread.stats_updated.connect(self.refresh_stats)

    def refresh_stats(self, inf_time, accuracy):
        self.v_lab_time.setText(f"{inf_time:.3f}s")
        if accuracy > 0:
            self.v_lab_acc.setText(f"{accuracy:.1f}%")
        else:
            self.v_lab_acc.setText("Scanning...")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect signals
        self.ui.add_image_btn.clicked.connect(self.capture_face_image)
        self.ui.add_student_btn.clicked.connect(self.add_student_to_table)

        # Initialize other variables
        self.captured_face_image = None
        self.email_sent = set()

        # Internal chart references (set after DB is ready)
        self._donut_chart  = None
        self._donut_series = None
        self._trend_chart  = None
        self._trend_series = None

        # Connect search bar
        self.ui.search_bar.textChanged.connect(self.filter_students)

        # Assign layouts/widgets
        self.cards_layout = self.ui.cards_layout
        self.home_layout  = self.ui.home_page.layout()
        FIXED_CARD_HEIGHT = 200

        # Make cards expandable
        self.cards = [self.ui.card1, self.ui.card2, self.ui.card3, self.ui.card4]
        for card in self.cards:
            card.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Fixed)
            card.setFixedHeight(FIXED_CARD_HEIGHT)
            card.setCursor(QtCore.Qt.PointingHandCursor)

        for card in self.cards:
            card.installEventFilter(self)

        # Map cards to stacked widget pages
        self.cards[0].mousePressEvent = lambda e: self.ui.stackedWidget_3.setCurrentWidget(self.ui.face_page)
        self.cards[1].mousePressEvent = lambda e: self.ui.stackedWidget_3.setCurrentWidget(self.ui.student_page)
        self.cards[2].mousePressEvent = lambda e: self.ui.stackedWidget_3.setCurrentWidget(self.ui.attendance_page)
        self.cards[3].mousePressEvent = lambda e: self.ui.stackedWidget_3.setCurrentWidget(self.ui.reports_page)

        self.cards_layout.setSpacing(20)
        self.home_layout.setContentsMargins(20, 20, 20, 20)

        # Initialize popup tracker BEFORE using show_popup
        self.current_popup = None

        # Ensure home_page has a layout
        if self.ui.home_page.layout() is None:
            main_layout = QtWidgets.QVBoxLayout(self.ui.home_page)
            self.ui.home_page.setLayout(main_layout)
        else:
            main_layout = self.ui.home_page.layout()

        dashboard_title = QLabel("Dashboard")
        dashboard_title.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #0d47a1; margin-bottom: 10px;"
        )
        main_layout.addWidget(dashboard_title)

        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setContentsMargins(20, 20, 20, 0)

        for card in self.cards:
            cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

        self.charts_container = QtWidgets.QHBoxLayout()
        self.charts_container.setSpacing(20)

        # Build charts with placeholder data first (DB not ready yet)
        self.donut_view = self._build_donut_chart(0, 0, 0)
        self.trend_view = self._build_trend_chart(
            [{"label": d, "date": "", "pct": 0, "present": 0, "absent": 0, "total": 0}
             for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]]
        )

        self.charts_container.addWidget(self.donut_view, 2)
        self.charts_container.addWidget(self.trend_view, 3)

        main_layout.addSpacing(20)
        main_layout.addLayout(self.charts_container)
        main_layout.addStretch()

        # ── LOGIN ──────────────────────────────────────────────────────────────
        login_dialog = LoginPopup(self)
        login_dialog.adjustSize()
        popup_rect = login_dialog.frameGeometry()
        popup_rect.moveCenter(self.frameGeometry().center())
        login_dialog.move(popup_rect.topLeft())

        if login_dialog.exec_() == QtWidgets.QDialog.Accepted and login_dialog.valid:
            self.current_user          = login_dialog.logged_in_user
            self.selected_class_name   = self.current_user["class_name"]
            self.selected_subject_name = self.current_user["subject_name"]

            safe_email = self.current_user["email"].replace("@", "_").replace(".", "_")
            self.db                 = UserDatabase(safe_email)
            self.attendance_manager = AttendanceManager(safe_email)

            self.db.add_teacher(self.current_user["name"], self.current_user["email"])
            teacher_id = self.db.get_teacher_id_by_email(self.current_user["email"])
            self.teacher_account_id = self.db.get_or_create_teacher_account(
                teacher_id=teacher_id,
                department_name=self.selected_class_name,
                subject_name=self.selected_subject_name
            )

            self.db.initialize_today_attendance(self.teacher_account_id)

            if not self.teacher_account_id:
                QMessageBox.critical(self, "Account Error",
                                     "Teacher account not found for selected class/subject")
                QtCore.QTimer.singleShot(0, self.close)
                return

            self.load_students()
            initialize_scheduler(safe_email, account_id=self.teacher_account_id, time_str="23:59")
            self.setup_reports_page(safe_email, self.teacher_account_id)

            # ── Refresh charts with real data now that DB is ready ─────────────
            self.refresh_dashboard_charts()

        else:
            QtCore.QTimer.singleShot(0, self.close)
            return

        loadJsonStyle(self, self.ui)
        self.is_maximized = False

        self.ui.help.clicked.connect(lambda: self.show_popup(HelpPopup))
        self.ui.information.clicked.connect(lambda: self.show_popup(InformationPopup))
        self.ui.setting.clicked.connect(lambda: self.show_popup(SettingsPopup))
        self.ui.profile.clicked.connect(lambda: ProfilePopup(self.current_user, self).exec_())
        self.ui.moreMenu.clicked.connect(lambda: self.show_popup(MoreMenuPopup))
        self.ui.logout.clicked.connect(self.open_logout_popup)

        # ── AI Chatbot button ──────────────────────────────────────────────────
        # If you have a dedicated button in Qt Designer named "chatbot_btn", use:
        #   self.ui.chatbot_btn.clicked.connect(self.open_chatbot)
        #
        # If not, this dynamically creates a chatbot button in the top bar.
        self._inject_chatbot_button()

        self.ui.home.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(0))
        self.ui.facerecognition.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(1))
        self.ui.studentmanagement.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(2))
        self.ui.attendancerecords.clicked.connect(self.load_attendance_records_page)
        self.ui.reports.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(4))

        self.ui.add_student_btn.clicked.connect(self.add_student_to_table)
        self.ui.start_camera_btn.clicked.connect(self.start_attendance)
        self.ui.stop_camera_btn.clicked.connect(self.stop_attendance)

        self.show()

        self.chatbot_page = ChatbotWidget(
            db=self.db,
            attendance_manager=self.attendance_manager,
            teacher_account_id=self.teacher_account_id,
            current_user=self.current_user
        )

        self.ui.stackedWidget_3.addWidget(self.chatbot_page)

    # ── Chatbot Button Injection ───────────────────────────────────────────────

    def _inject_chatbot_button(self):
        """
        Try to connect self.ui.chatbot_btn if it exists in the .ui file.
        Otherwise, dynamically create a button and insert it next to moreMenu.
        """
        # Option A: dedicated button already in Qt Designer
        if hasattr(self.ui, "chatbot_btn"):
            self.ui.chatbot_btn.clicked.connect(self.open_chatbot)
            return

        # Option B: create the button dynamically and place it beside moreMenu
        self._chatbot_btn = QtWidgets.QPushButton()
        self._chatbot_btn.setObjectName("chatbot_btn")
        self._chatbot_btn.setToolTip("AI Chatbot")
        self._chatbot_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self._chatbot_btn.setFixedSize(36, 36)

        # Use a robot icon if available, otherwise fall back to text
        robot_icon_path = resource_path("icon/robot.svg")
        if os.path.exists(robot_icon_path):
            self._chatbot_btn.setIcon(QIcon(robot_icon_path))
            self._chatbot_btn.setIconSize(QtCore.QSize(20, 20))
        else:
            self._chatbot_btn.setText("🤖")

        self._chatbot_btn.setStyleSheet("""
            QPushButton {
                background-color: #00D4FF22;
                border: 1px solid #00D4FF55;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #00D4FF44;
                border-color: #00D4FF;
            }
            QPushButton:pressed {
                background-color: #00D4FF66;
            }
        """)
        self._chatbot_btn.clicked.connect(self.open_chatbot)

        # Insert next to the moreMenu button if we can find its parent layout
        more_menu_btn = self.ui.moreMenu
        parent_widget = more_menu_btn.parentWidget()
        if parent_widget and parent_widget.layout():
            layout = parent_widget.layout()
            idx = layout.indexOf(more_menu_btn)
            if idx >= 0:
                layout.insertWidget(idx, self._chatbot_btn)
                return

        # Last resort: add to the main window's top-level layout
        if self.ui.centralwidget.layout():
            self.ui.centralwidget.layout().addWidget(self._chatbot_btn)

    # ── Open Chatbot ──────────────────────────────────────────────────────────

    def open_chatbot(self):
        self.ui.stackedWidget_3.setCurrentWidget(self.chatbot_page)

    # ── Chart Helpers ─────────────────────────────────────────────────────────

    def _get_today_stats(self):
        """Return (present, late, absent) from today's attendance records."""
        try:
            today   = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_manager.get_full_report(self.teacher_account_id)

            present = late = absent = 0
            for r in records:
                if r.get("date") == today:
                    status = str(r.get("status", "")).strip().lower()
                    if status == "present":
                        present += 1
                    elif status == "late":
                        late += 1
                    else:
                        absent += 1

            # If nothing recorded yet, show all students as absent
            if present + late + absent == 0:
                total = len(self.db.get_students_by_account(self.teacher_account_id))
                absent = total

            return present, late, absent
        except Exception as e:
            print(f"⚠️ _get_today_stats error: {e}")
            return 0, 0, 0

    def _get_trend_data(self):
        """
        Return list of dicts for the last 5 calendar days:
          { "label": "Mon", "date": "2024-01-01", "pct": 75.0,
            "present": 15, "absent": 5, "total": 20 }
        """
        try:
            total_students = len(self.db.get_students_by_account(self.teacher_account_id))
            if total_students == 0:
                blank = [{"label": d, "date": "", "pct": 0, "present": 0,
                          "absent": 0, "total": 0}
                         for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]]
                return blank

            records = self.attendance_manager.get_full_report(self.teacher_account_id)
            day_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            by_date = {}

            for r in records:
                d = r.get("date", "")
                if not d:
                    continue
                status = str(r.get("status", "")).strip().lower()
                by_date.setdefault(d, {"present": 0, "total": 0})
                by_date[d]["total"] += 1
                if status == "present":
                    by_date[d]["present"] += 1

            today  = datetime.now().date()
            points = []
            for offset in range(4, -1, -1):
                day   = today - timedelta(days=offset)
                key   = day.strftime("%Y-%m-%d")
                label = day_map[day.weekday()]
                if key in by_date:
                    p   = by_date[key]["present"]
                    pct = round(p / total_students * 100, 1)
                    ab  = total_students - p
                else:
                    p = pct = ab = 0
                points.append({
                    "label":   label,
                    "date":    key,
                    "pct":     pct,
                    "present": p,
                    "absent":  ab,
                    "total":   total_students,
                })

            return points
        except Exception as e:
            print(f"⚠️ _get_trend_data error: {e}")
            return [{"label": d, "date": "", "pct": 0, "present": 0,
                     "absent": 0, "total": 0}
                    for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]]

    def _build_donut_chart(self, present, late, absent):
        """Create and return a QChartView donut chart from given counts."""
        series = QPieSeries()
        series.setHoleSize(0.50)

        total = present + late + absent

        def on_hovered(sl, state):
            sl.setExploded(state)
            sl.setExplodeDistanceFactor(0.07)

        if total == 0:
            ph = series.append("No Data", 1)
            ph.setBrush(QColor("#2D3748"))
            ph.setLabelVisible(False)
        else:
            if present > 0:
                sl = series.append(f"Present  {present}", present)
                sl.setBrush(QColor("#00D4FF"))
                sl.setLabelVisible(True)
                sl.setLabelColor(QColor("#FFFFFF"))
            if late > 0:
                sl = series.append(f"Late  {late}", late)
                sl.setBrush(QColor("#FFB000"))
                sl.setLabelVisible(True)
                sl.setLabelColor(QColor("#FFFFFF"))
            if absent > 0:
                sl = series.append(f"Absent  {absent}", absent)
                sl.setBrush(QColor("#FF4D4D"))
                sl.setLabelVisible(True)
                sl.setLabelColor(QColor("#FFFFFF"))

        series.hovered.connect(on_hovered)

        pct_str = f"{int(present / total * 100)}%" if total > 0 else "—"

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Today's Attendance  ·  {pct_str} Present")
        title_font = QFont("Segoe UI", 10, QFont.Bold)
        chart.setTitleFont(title_font)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAnimationDuration(800)
        chart.setBackgroundVisible(True)
        chart.setBackgroundBrush(QColor("#161B22"))
        chart.setTitleBrush(QColor("#E6EDF3"))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignBottom)
        chart.legend().setLabelColor(QColor("#ABB2BF"))
        chart.legend().setFont(QFont("Segoe UI", 9))

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet(
            "QChartView { background-color: #161B22; border-radius: 14px;"
            " border: 1px solid #30363D; }"
        )
        view.setMinimumHeight(320)

        # Store references for in-place refresh
        self._donut_chart  = chart
        self._donut_series = series

        return view

    def _build_trend_chart(self, points):
        """
        Create and return a TrendChartView (QChartView subclass) that shows a
        styled tooltip on mouse-hover with present / absent / total counts.
        `points` is the list of dicts returned by _get_trend_data().
        """
        series = QLineSeries()
        for i, pt in enumerate(points):
            series.append(i, pt["pct"])

        pen = QPen(QColor("#00D4FF"))
        pen.setWidth(3)
        series.setPen(pen)
        series.setPointsVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Attendance Trend — Last 5 Days")
        title_font = QFont("Segoe UI", 10, QFont.Bold)
        chart.setTitleFont(title_font)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAnimationDuration(800)
        chart.setBackgroundBrush(QColor("#161B22"))
        chart.setTitleBrush(QColor("#E6EDF3"))

        label_font = QFont("Segoe UI", 9)

        axis_x = QCategoryAxis()
        for i, pt in enumerate(points):
            axis_x.append(pt["label"], i)
        axis_x.setRange(-0.5, len(points) - 0.5)
        axis_x.setLabelsBrush(QColor("#ABB2BF"))
        axis_x.setLinePen(QPen(QColor("#30363D")))
        axis_x.setGridLinePen(QPen(QColor("#21262D")))
        axis_x.setLabelsFont(label_font)
        chart.addAxis(axis_x, QtCore.Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTickCount(6)
        axis_y.setLabelFormat("%d%%")
        axis_y.setLabelsBrush(QColor("#ABB2BF"))
        axis_y.setLinePen(QPen(QColor("#30363D")))
        axis_y.setGridLinePen(QPen(QColor("#21262D")))
        axis_y.setLabelsFont(label_font)
        chart.addAxis(axis_y, QtCore.Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        # ── Custom QChartView subclass with hover tooltip ──────────────────────
        class TrendChartView(QChartView):
            """QChartView that shows a rich tooltip when hovering near a data point."""

            SNAP_RADIUS_PX = 30

            def __init__(self, chart, point_data, parent=None):
                super().__init__(chart, parent)
                self._point_data  = point_data
                self._tooltip     = QtWidgets.QLabel(self)
                self._tooltip.setWordWrap(False)
                self._tooltip.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                self._tooltip.setStyleSheet("""
                    QLabel {
                        background-color: #1F2937;
                        color: #F9FAFB;
                        border: 1px solid #374151;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-family: 'Segoe UI';
                        font-size: 12px;
                    }
                """)
                self._tooltip.hide()
                self.setMouseTracking(True)

            def _nearest_index(self, cursor_pos):
                chart      = self.chart()
                best_idx   = -1
                best_dist  = float("inf")
                series_obj = chart.series()[0]
                for i in range(series_obj.count()):
                    qpt      = series_obj.at(i)
                    scene_pt = chart.mapToPosition(qpt, series_obj)
                    view_pt  = self.mapFromScene(scene_pt)
                    dist     = ((view_pt.x() - cursor_pos.x()) ** 2 +
                                (view_pt.y() - cursor_pos.y()) ** 2) ** 0.5
                    if dist < best_dist:
                        best_dist = dist
                        best_idx  = i
                if best_dist <= self.SNAP_RADIUS_PX:
                    return best_idx
                return -1

            def mouseMoveEvent(self, event):
                idx = self._nearest_index(event.pos())
                if idx >= 0 and idx < len(self._point_data):
                    pt      = self._point_data[idx]
                    label   = pt["label"]
                    date    = pt["date"] or "—"
                    present = pt["present"]
                    absent  = pt["absent"]
                    total   = pt["total"]
                    pct     = pt["pct"]

                    html = (
                        f"<b style='color:#00D4FF;'>{label}  ·  {date}</b><br>"
                        f"✅ Present: <b style='color:#4ADE80;'>{present}</b>&nbsp;&nbsp;"
                        f"❌ Absent: <b style='color:#F87171;'>{absent}</b>&nbsp;&nbsp;"
                        f"👥 Total: <b>{total}</b>&nbsp;&nbsp;"
                        f"<span style='color:#FCD34D;'>{pct}%</span>"
                    )
                    self._tooltip.setText(html)
                    self._tooltip.adjustSize()

                    tip_w = self._tooltip.width()
                    tip_h = self._tooltip.height()
                    x     = event.pos().x() + 14
                    y     = event.pos().y() - tip_h - 8
                    if x + tip_w > self.width():
                        x = event.pos().x() - tip_w - 14
                    if y < 0:
                        y = event.pos().y() + 14
                    self._tooltip.move(x, y)
                    self._tooltip.show()
                    self._tooltip.raise_()
                else:
                    self._tooltip.hide()
                super().mouseMoveEvent(event)

            def leaveEvent(self, event):
                self._tooltip.hide()
                super().leaveEvent(event)

            def update_points(self, new_point_data):
                self._point_data = new_point_data

        view = TrendChartView(chart, points, parent=None)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet(
            "QChartView { background-color: #161B22; border-radius: 14px;"
            " border: 1px solid #30363D; }"
        )
        view.setMinimumHeight(320)

        self._trend_chart      = chart
        self._trend_series     = series
        self._trend_chart_view = view

        return view

    def refresh_dashboard_charts(self):
        """
        Update both dashboard charts in-place using the latest database values.
        Call this after every attendance mark or student add.
        """
        # ── Donut ──────────────────────────────────────────────────────────────
        try:
            present, late, absent = self._get_today_stats()
            total = present + late + absent

            series = self._donut_series
            series.clear()

            def on_hovered(sl, state):
                sl.setExploded(state)
                sl.setExplodeDistanceFactor(0.07)

            if total == 0:
                ph = series.append("No Data", 1)
                ph.setBrush(QColor("#2D3748"))
                ph.setLabelVisible(False)
            else:
                if present > 0:
                    sl = series.append(f"Present  {present}", present)
                    sl.setBrush(QColor("#00D4FF"))
                    sl.setLabelVisible(True)
                    sl.setLabelColor(QColor("#FFFFFF"))
                if late > 0:
                    sl = series.append(f"Late  {late}", late)
                    sl.setBrush(QColor("#FFB000"))
                    sl.setLabelVisible(True)
                    sl.setLabelColor(QColor("#FFFFFF"))
                if absent > 0:
                    sl = series.append(f"Absent  {absent}", absent)
                    sl.setBrush(QColor("#FF4D4D"))
                    sl.setLabelVisible(True)
                    sl.setLabelColor(QColor("#FFFFFF"))

            series.hovered.connect(on_hovered)

            pct_str = f"{int(present / total * 100)}%" if total > 0 else "—"
            self._donut_chart.setTitle(f"Today's Attendance  ·  {pct_str} Present")

        except Exception as e:
            print(f"⚠️ refresh donut error: {e}")

        # ── Trend line ─────────────────────────────────────────────────────────
        try:
            points = self._get_trend_data()
            series = self._trend_series
            series.clear()
            for i, pt in enumerate(points):
                series.append(i, pt["pct"])
            if hasattr(self, "_trend_chart_view"):
                self._trend_chart_view.update_points(points)
        except Exception as e:
            print(f"⚠️ refresh trend error: {e}")

    # ── Event Filter (card hover animation) ───────────────────────────────────

    def eventFilter(self, obj, event):
        if obj in self.cards:
            if event.type() == QEvent.Enter:
                anim = QPropertyAnimation(obj, b"geometry")
                anim.setDuration(150)
                anim.setStartValue(obj.geometry())
                anim.setEndValue(obj.geometry().adjusted(-5, -5, 5, 5))
                anim.start()
                obj.anim = anim
            elif event.type() == QEvent.Leave:
                anim = QPropertyAnimation(obj, b"geometry")
                anim.setDuration(150)
                anim.setStartValue(obj.geometry())
                anim.setEndValue(obj.geometry().adjusted(5, 5, -5, -5))
                anim.start()
                obj.anim = anim
        return super().eventFilter(obj, event)

    # ── Close ─────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        stop_scheduler()
        if hasattr(self, "attendance_thread") and self.attendance_thread.isRunning():
            self.attendance_thread.running = False
            self.attendance_thread.quit()
            self.attendance_thread.wait()
        event.accept()

    # ── Session ───────────────────────────────────────────────────────────────

    def initialize_user_session(self, user_data):
        self.current_user          = user_data
        self.selected_class_name   = user_data["class_name"]
        self.selected_subject_name = user_data["subject_name"]

        safe_email = user_data["email"].replace("@", "_").replace(".", "_")
        self.db                 = UserDatabase(safe_email)
        self.attendance_manager = AttendanceManager(safe_email)

        self.db.add_teacher(user_data["name"], user_data["email"])
        teacher_id = self.db.get_teacher_id_by_email(user_data["email"])
        self.teacher_account_id = self.db.get_or_create_teacher_account(
            teacher_id=teacher_id,
            department_name=self.selected_class_name,
            subject_name=self.selected_subject_name
        )

        if not self.teacher_account_id:
            QMessageBox.critical(self, "Account Error",
                                 "Teacher account not found for selected class/subject")
            QApplication.quit()
            return

        self.load_students()
        self.known_faces, self.known_names = self.load_known_faces()
        self.refresh_dashboard_charts()

    def reset_session(self):
        if hasattr(self, "attendance_thread"):
            if self.attendance_thread.isRunning():
                self.attendance_thread.running = False
                self.attendance_thread.quit()
                self.attendance_thread.wait()
            del self.attendance_thread

        if self.db:
            self.db.close()
            self.db = None

        self.ui.student_table.setRowCount(0)
        self.ui.stackedWidget_3.setCurrentWidget(self.ui.home_page)

        self.current_user           = None
        self.db                     = None
        self.teacher_account_id     = None
        self.selected_class_name    = None
        self.selected_subject_name  = None
        self.known_faces            = []
        self.known_names            = []
        self.captured_face_image    = None

    # ── Known Faces ───────────────────────────────────────────────────────────

    def load_known_faces(self):
        known_faces = []
        known_meta  = []

        if not self.current_user:
            return known_faces, known_meta

        safe_email       = self.current_user["email"].replace("@", "_").replace(".", "_")
        known_faces_dir  = os.path.join("data", safe_email, "known_faces")
        os.makedirs(known_faces_dir, exist_ok=True)

        for filename in sorted(os.listdir(known_faces_dir)):
            if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
                continue
            path      = os.path.join(known_faces_dir, filename)
            image     = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces.append(encodings[0])
                base = os.path.splitext(filename)[0]
                base = base.rsplit("_", 1)[0] if base[-1].isdigit() else base
                known_meta.append((base, base))

        return known_faces, known_meta

    # ── Info Dialog ───────────────────────────────────────────────────────────

    def show_app_info(self):
        self.info_popup = InfoDialog(self.face_thread)
        self.info_popup.close_btn.clicked.connect(self.info_popup.close)
        self.info_popup.show()

    # ── Logout ────────────────────────────────────────────────────────────────

    def open_logout_popup(self):
        popup = LogoutPopup(self)

        if popup.exec_() == QtWidgets.QDialog.Accepted:
            if popup.action == "logout":
                self.stop_attendance()

                if self.db:
                    self.db.close()
                    self.db = None

                self.reset_session()
                self.hide()

                login_dialog = LoginPopup(self)
                login_dialog.adjustSize()
                rect = login_dialog.frameGeometry()
                rect.moveCenter(self.frameGeometry().center())
                login_dialog.move(rect.topLeft())

                if login_dialog.exec_() == QtWidgets.QDialog.Accepted and login_dialog.valid:
                    self.initialize_user_session(login_dialog.logged_in_user)
                    self.show()
                else:
                    QtCore.QTimer.singleShot(0, QApplication.quit)

    # ── UI Helpers ────────────────────────────────────────────────────────────

    def checkButtonGroup(self):
        sender = self.sender()
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn.objectName() in ["home", "facerecognition", "studentmanagement",
                                    "attendancerecords", "reports", "setting", "help", "information"]:
                btn.setStyleSheet("background-color: white;" if btn is sender else "")

    def update_left_menu_active(self, active_btn):
        buttons = [self.ui.home, self.ui.facerecognition, self.ui.studentmanagement,
                   self.ui.attendancerecords, self.ui.reports]
        for btn in buttons:
            if btn == active_btn:
                btn.setStyleSheet("background-color: #00b4d8; color: white;")
            else:
                btn.setStyleSheet("")

    def show_toast(self, message):
        toast = ToastNotification(self, message)
        toast.show()

    def update_camera_feed(self, frame):
        """Render a frame from the attendance thread into the face-page preview."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        pixmap   = QtGui.QPixmap.fromImage(qt_image)
        self.ui.camera_preview.setPixmap(pixmap.scaled(
            self.ui.camera_preview.width(),
            self.ui.camera_preview.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        ))

    def open_student_profile(self, row_index):
        name = self.home_table.item(row_index, 0).text()
        roll = self.home_table.item(row_index, 1).text()

        students     = self.db.get_all_students()
        student_info = None

        for s in students:
            if s["roll"] == roll:
                student_info = {
                    "name": s["name"], "roll": s["roll"],
                    "dept": s["dept"], "year": s["year"],
                    "face_image": s["face_image"], "email": s["email"]
                }
                break

        if not student_info:
            QMessageBox.warning(self, "Not Found", f"No record found for {name}")
            return

        popup = StudentDetailsPopup(student_info, self)
        popup.exec_()

    # ── Popup System ──────────────────────────────────────────────────────────

    def show_popup(self, popup_class):
        if self.current_popup and self.current_popup.isVisible():
            self.current_popup.close()

        if popup_class is ViewReportsPopup:
            popup = popup_class(self.db, self.current_user.get("email"),
                                account_id=self.teacher_account_id, parent=self)
        else:
            popup = popup_class(self)

        self.current_popup = popup

        parent_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
        if popup_class in (SettingsPopup, InformationPopup, HelpPopup):
            x = parent_pos.x() + 10
            y = parent_pos.y() + self.height() - popup.height() - 10
        elif popup_class in (ProfilePopup, MoreMenuPopup):
            x = parent_pos.x() + self.width() - popup.width() - 10
            y = parent_pos.y() + self.height() - popup.height() - 10
        else:
            x = parent_pos.x() + (self.width()  - popup.width())  // 2
            y = parent_pos.y() + (self.height() - popup.height()) // 2

        popup.move(x, y)
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(popup)
        popup.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        popup.show()

        anim_fade = QPropertyAnimation(opacity_effect, b"opacity")
        anim_fade.setDuration(500)
        anim_fade.setStartValue(0)
        anim_fade.setEndValue(1)
        anim_fade.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        popup.anim_fade = anim_fade
        anim_fade.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def close_current_popup(self):
        if hasattr(self, "current_popup") and self.current_popup and self.current_popup.isVisible():
            self.current_popup.close()
            self.current_popup = None

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if hasattr(self, "current_popup") and self.current_popup and self.current_popup.isVisible():
            popup            = self.current_popup
            resizable_popups = (ProfilePopup, MoreMenuPopup)
            parent_pos       = self.mapToGlobal(QtCore.QPoint(0, 0))

            if isinstance(popup, resizable_popups):
                popup.resize(int(self.width() * 0.6), int(self.height() * 0.7))
                x = parent_pos.x() + self.width()  - popup.width()  - 10
                y = parent_pos.y() + self.height() - popup.height() - 10
            else:
                x = parent_pos.x() + (10 if isinstance(popup, (SettingsPopup, InformationPopup, HelpPopup))
                                       else self.width() - popup.width() - 10)
                y = parent_pos.y() + self.height() - popup.height() - 10
            popup.move(x, y)

        try:
            total_width    = self.home_page.width()
            spacing        = self.cards_layout.spacing()
            cols           = len(self.cards)
            width_per_card = (total_width - spacing * (cols - 1) - 40) / cols
            fixed_card_height = 150

            for card in self.cards:
                card.setMaximumWidth(width_per_card)
                card.setMinimumWidth(width_per_card)
                card.setMaximumHeight(fixed_card_height)
                card.setMinimumHeight(fixed_card_height)
        except Exception:
            pass

    # ── FACE CAPTURE (Student Management) ────────────────────────────────────

    def capture_face_image(self):
        """Open camera capture popup — self-contained, no interference with attendance camera."""
        name = self.ui.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Enter student name first.")
            return

        if hasattr(self, "attendance_thread") and self.attendance_thread.isRunning():
            QMessageBox.information(
                self, "Camera In Use",
                "Attendance camera is running.\nPlease stop it before capturing a new face."
            )
            return

        safe_email = self.current_user["email"].replace("@", "_").replace(".", "_")
        save_dir   = os.path.join(os.getcwd(), "data", safe_email, "known_faces")
        os.makedirs(save_dir, exist_ok=True)

        popup = CameraCapturePopup(name, save_dir, parent=self)
        popup.captured.connect(self.on_face_captured)

        popup.adjustSize()
        geo = self.frameGeometry()
        popup.move(
            geo.x() + (geo.width()  - popup.width())  // 2,
            geo.y() + (geo.height() - popup.height()) // 2,
        )
        popup.exec_()

    def on_face_captured(self, save_path: str):
        """Called by CameraCapturePopup when a face image is successfully saved."""
        self.captured_face_image = save_path

        self.ui.add_image_btn.setText("✅ Image Captured")
        self.ui.add_image_btn.setStyleSheet(
            "color: #16a34a; font-weight: bold; background-color: #dcfce7;"
            "border-radius: 8px; padding: 8px 16px;"
        )
        self.ui.add_image_btn.setEnabled(True)

        if hasattr(self.ui, "face_preview") and os.path.exists(save_path):
            pix = QtGui.QPixmap(save_path).scaled(
                self.ui.face_preview.width(),
                self.ui.face_preview.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.ui.face_preview.setPixmap(pix)

    def save_compressed_image(self, input_path, output_path, max_size=(350, 350), quality=85):
        try:
            img = Image.open(input_path)
            img.thumbnail(max_size, Image.LANCZOS)
            img = img.convert("RGB")
            img.save(output_path, "JPEG", optimize=True, quality=quality)
        except Exception as e:
            print(f"⚠️ Error compressing image: {e}")

    # ── Student Management ────────────────────────────────────────────────────

    def add_student_to_table(self):

        name = self.ui.name_input.text().strip()
        registration_no = self.ui.id_input.text().strip().upper()
        dept = self.ui.department_input.currentText().strip()
        year = self.ui.year_input.currentText().strip()
        email = self.ui.email_input.text().strip()

        if not all([name, registration_no, dept, year, email]):
            QMessageBox.warning(
                self, "Missing Data",
                "Please fill all fields including Registration Number."
            )
            return

        pattern = r"^D\d{9}$"
        if not re.match(pattern, registration_no):
            QMessageBox.warning(
                self, "Invalid Registration Number",
                "Registration number must:\n"
                "- Start with 'D'\n"
                "- Contain exactly 10 characters\n"
                "- Example: D241234567"
            )
            return

        if self.db.student_exists(registration_no, self.teacher_account_id):
            QMessageBox.warning(self, "Duplicate", "Registration number already exists!")
            return

        if self.captured_face_image is None:
            QMessageBox.warning(self, "Input Error", "Please capture a face image first.")
            return

        face_image = self.captured_face_image
        safe_email = self.current_user["email"].replace("@", "_").replace(".", "_")
        known_faces_dir = os.path.join("data", safe_email, "known_faces")
        os.makedirs(known_faces_dir, exist_ok=True)

        image_path = os.path.join(known_faces_dir, f"{registration_no}.jpg")

        if isinstance(face_image, str) and os.path.exists(face_image):
            import shutil
            shutil.copy(face_image, image_path)
        else:
            cv2.imwrite(image_path, face_image)

        success = self.db.add_student(
            name=name,
            roll=registration_no,
            dept=dept,
            year=year,
            face_image=image_path,
            email=email,
            teacher_account_id=self.teacher_account_id
        )

        if not success:
            QMessageBox.warning(self, "Duplicate", "Registration number already exists!")
            return

        self.db.initialize_today_attendance(self.teacher_account_id)
        self.load_students()

        self.ui.name_input.clear()
        self.ui.id_input.clear()
        self.ui.email_input.clear()

        self.captured_face_image = None
        self.ui.add_image_btn.setText("📷 Add Image")
        self.ui.add_image_btn.setStyleSheet("")
        self.ui.add_image_btn.setEnabled(True)

        subject = "Welcome to the System!"
        body = (
            f"Dear {name},\n\n"
            f"Your profile has been successfully created.\n"
            f"Registration Number: {registration_no}"
        )
        send_email(email, subject, body)

        speak_message_async(f"Student {name} added successfully")
        self.refresh_dashboard_charts()

    def load_students(self):
        if not self.db or not hasattr(self, "teacher_account_id"):
            print("⚠️ Database not initialized yet — skipping load_students()")
            return

        self.ui.student_table.setRowCount(0)

        students = self.db.get_students_by_account(self.teacher_account_id)
        for student in students:
            name       = student.get("name", "")
            roll       = student.get("roll", "")
            dept       = student.get("dept", "")
            year       = student.get("year", "")
            image_path = student.get("face_image", "") or ""
            email      = student.get("email", "") or ""

            row = self.ui.student_table.rowCount()
            self.ui.student_table.insertRow(row)
            self.ui.student_table.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
            self.ui.student_table.setItem(row, 1, QtWidgets.QTableWidgetItem(roll))
            self.ui.student_table.setItem(row, 2, QtWidgets.QTableWidgetItem(dept))
            self.ui.student_table.setItem(row, 3, QtWidgets.QTableWidgetItem(year))
            self.ui.student_table.setItem(row, 4, QtWidgets.QTableWidgetItem(email))

            action_widget = QtWidgets.QWidget()
            action_layout = QtWidgets.QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

            view_btn = QtWidgets.QPushButton()
            view_btn.setIcon(QIcon(resource_path("icon/eye.svg")))
            view_btn.setCursor(QtCore.Qt.PointingHandCursor)
            view_btn.setToolTip("View Face")
            view_btn.clicked.connect(lambda _, path=image_path, r=row: self.view_face(path, r))

            delete_btn = QtWidgets.QPushButton()
            delete_btn.setIcon(QIcon(resource_path("icon/delete.svg")))
            delete_btn.setCursor(QtCore.Qt.PointingHandCursor)
            delete_btn.clicked.connect(self.handle_delete_button)

            action_layout.addWidget(view_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            action_widget.face_image_path = image_path

            self.ui.student_table.setCellWidget(row, 5, action_widget)

    def delete_student_from_db(self, roll):
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete student {roll}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_student(roll)
            self.load_students()

    def handle_delete_button(self):
        btn = self.sender()
        if not btn:
            return
        index = self.ui.student_table.indexAt(btn.parent().pos())
        if not index.isValid():
            return
        row = index.row()
        roll_item = self.ui.student_table.item(row, 1)
        if not roll_item:
            return
        roll  = roll_item.text()
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete student {roll}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        action_widget = self.ui.student_table.cellWidget(row, 5)
        image_path    = getattr(action_widget, 'face_image_path', None)
        try:
            self.db.delete_student(roll)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"⚠️ Error deleting student: {e}")
        self.load_students()
        self.refresh_dashboard_charts()

    def setup_reports_page(self, username, account_id=None):
        try:
            if self.ui.reports_layout.count() > 0:
                for i in range(self.ui.reports_layout.count()):
                    widget = self.ui.reports_layout.itemAt(i).widget()
                    if widget:
                        widget.deleteLater()
            self.reports_widget = AttendanceReportsPage(self.db, username, account_id, self)
            self.ui.reports_layout.addWidget(self.reports_widget)
            print("✓ Reports page initialized successfully")
        except Exception as e:
            print(f"⚠️ Error initializing reports page: {e}")
            QMessageBox.warning(self, "Error", f"Failed to initialize reports page: {e}")

    def filter_students(self, text):
        text = text.strip().lower()
        for row in range(self.ui.student_table.rowCount()):
            name_item = self.ui.student_table.item(row, 0)
            id_item   = self.ui.student_table.item(row, 1)
            if name_item is None or id_item is None:
                continue
            match = text in name_item.text().lower() or text in id_item.text().lower()
            self.ui.student_table.setRowHidden(row, not match)

    def load_attendance_records_page(self):
        self.ui.stackedWidget_3.setCurrentWidget(self.ui.attendance_page)
        self.ui.load_attendance_records(parent=self)

    def add_student_row(self, student):
        row = self.ui.student_table.rowCount()
        self.ui.student_table.insertRow(row)
        self.ui.student_table.setItem(row, 0, QtWidgets.QTableWidgetItem(student["name"]))
        self.ui.student_table.setItem(row, 1, QtWidgets.QTableWidgetItem(student["id"]))
        self.ui.student_table.setItem(row, 2, QtWidgets.QTableWidgetItem(student["dept"]))
        self.ui.student_table.setItem(row, 3, QtWidgets.QTableWidgetItem(student["year"]))
        self.ui.student_table.setItem(row, 4, QtWidgets.QTableWidgetItem(student["email"]))

        action_widget = QtWidgets.QWidget()
        action_layout = QtWidgets.QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(5)

        face_image_path = student.get("face_image", "")

        view_btn = QtWidgets.QPushButton()
        view_btn.setIcon(QIcon(resource_path("icon/eye.svg")))
        view_btn.setCursor(QtCore.Qt.PointingHandCursor)
        view_btn.setToolTip("View Face")
        view_btn.clicked.connect(lambda _, path=face_image_path, r=row: self.view_face(path, r))

        delete_btn = QtWidgets.QPushButton()
        delete_btn.setIcon(QIcon(resource_path("icon/delete.svg")))
        delete_btn.setCursor(QtCore.Qt.PointingHandCursor)
        delete_btn.setToolTip("Delete Student")
        delete_btn.clicked.connect(self.handle_delete_button)

        action_layout.addStretch()
        action_layout.addWidget(view_btn)
        action_layout.addStretch()
        action_layout.addWidget(delete_btn)
        action_widget.setLayout(action_layout)
        action_widget.face_image_path = face_image_path

        self.ui.student_table.setCellWidget(row, 5, action_widget)

    def view_face(self, student_id, row=None):
        if row is None:
            btn = self.sender()
            if btn:
                index = self.ui.student_table.indexAt(btn.parent().pos())
                if index.isValid():
                    row = index.row()

        if row is None:
            QMessageBox.warning(self, "Error", "Cannot identify which student to show.")
            return

        name       = self.ui.student_table.item(row, 0).text()
        student_id = self.ui.student_table.item(row, 1).text()
        dept       = self.ui.student_table.item(row, 2).text()
        year       = self.ui.student_table.item(row, 3).text()
        email      = self.ui.student_table.item(row, 4).text()

        safe_email = self.current_user["email"].replace("@", "_").replace(".", "_")
        image_path = os.path.join("data", safe_email, "known_faces", f"{student_id}.jpg")

        student_data = {
            "name": name, "id": student_id, "dept": dept,
            "Year": year, "face_image": image_path, "email": email
        }

        popup = StudentDetailsPopup(student_data, db_instance=self.db, parent=self)
        popup.exec_()

    # ── Attendance ────────────────────────────────────────────────────────────

    def on_attendance_marked(self, student_id, student_name):
        self.load_attendance_table()
        self.show_toast(f"✅ {student_name} attendance recorded")
        self.refresh_dashboard_charts()

        if student_id in self.email_sent:
            return
        self.email_sent.add(student_id)

        student_email = self.db.get_student_email_by_roll(student_id)
        if student_email:
            subject = "Attendance Marked Successfully"
            body = (f"Hello {student_name},\n\nYour attendance has been successfully recorded.\n\n"
                    f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                    f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"Regards,\nAutomated Attendance System")
            send_email(student_email, subject, body)

    def load_attendance_table(self):
        self.ui.attendance_table.setRowCount(0)
        records = self.attendance_manager.get_full_report(self.teacher_account_id)

        for row_num, row in enumerate(records):
            self.ui.attendance_table.insertRow(row_num)
            values = [row["name"], row["dept"], row["year"],
                      row["date"], row["time"], row["status"]]
            for col_num, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.attendance_table.setItem(row_num, col_num, item)

    def start_attendance(self):
        self.email_sent.clear()

        known_faces = []
        known_meta  = []

        safe_email      = self.current_user["email"].replace("@", "_").replace(".", "_")
        known_faces_dir = os.path.join("data", safe_email, "known_faces")

        students = self.db.get_students_by_account(self.teacher_account_id)
        for student in students:
            name = student.get("name", "")
            roll = student.get("roll", "")

            safe_name  = name.replace(" ", "_")
            all_images = []

            for i in range(10):
                p = os.path.join(known_faces_dir, f"{safe_name}_{i}.jpg")
                if os.path.exists(p):
                    all_images.append(p)

            if not all_images:
                legacy = student.get("face_image") or \
                         os.path.join(known_faces_dir, f"{roll}.jpg")
                if legacy and os.path.exists(legacy):
                    all_images.append(legacy)

            if not all_images:
                print(f"⚠️ No images found for {name} ({roll})")
                continue

            loaded = 0
            for img_path in all_images:
                image     = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_faces.append(encodings[0])
                    known_meta.append((name, roll))
                    loaded += 1

            print(f"✅ {name}: {loaded} encoding(s) loaded")

        if not known_faces:
            self.show_toast("⚠️ No registered faces found for this class/subject.")
            return

        try:
            self.db.initialize_today_attendance(self.teacher_account_id)
        except Exception:
            pass

        safe_email = self.current_user["email"].replace("@", "_").replace(".", "_")
        self.attendance_thread = FaceRecognitionThread(
            username=safe_email,
            account_id=self.teacher_account_id,
            known_faces=known_faces,
            known_names=known_meta
        )
        self.attendance_thread.attendance_marked.connect(self.on_attendance_marked)
        self.attendance_thread.frame_updated.connect(self.update_camera_feed)
        self.attendance_thread.status_message.connect(self.show_toast)
        self.attendance_thread.start()

        self.show_toast("📸 Attendance started...")

    def stop_attendance(self):
        for attr in ("attendance_thread", "face_thread"):
            thread = getattr(self, attr, None)
            if thread and thread.isRunning():
                thread.running = False
                thread.quit()
                thread.wait()
                self.show_toast("✅ Attendance stopped.")
                break

        self.ui.start_camera_btn.setEnabled(True)
        self.ui.camera_preview.clear()

    def get_student_email(self, student_name):
        student = self.db.get_student_by_name(student_name)
        if student:
            return student["email"]
        return None

    def update_status_label(self, text):
        self.ui.status_label.setText(f"Status: {text}")
        if "Unregistered" in text:
            QMessageBox.warning(self, "Unregistered Face", "You are not registered!")

    def show_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch  = rgb_image.shape
        qt_image  = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.ui.camera_frame.setPixmap(QPixmap.fromImage(qt_image))

    def animate_open(self):
        start_rect = QRect(self.x() + self.width() // 2,
                           self.y() + self.height() // 2, 0, 0)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(280)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(self.geometry())
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()

    def styleVariablesFromTheme(self, style):
        return style


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Face Recognition App")
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    sys.exit(app.exec_())