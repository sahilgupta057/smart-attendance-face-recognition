from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush, QFont, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
import math


# ──────────────────────────────────────────────────────────────────────────────
# ANIMATED PIPELINE WIDGET
# ──────────────────────────────────────────────────────────────────────────────

class PipelineWidget(QtWidgets.QWidget):
    """
    Draws a vertical animated pipeline:
      Node → connector line with travelling pulse → Node → ...
    """

    STEPS = [
        ("01", "FRAME CAPTURE",    "OpenCV acquires frames at 30fps\nwith adaptive noise reduction",       "#00D4FF"),
        ("02", "FACE DETECTION",   "HOG + CNN detector locates faces\nwith bounding box precision",         "#00FFB3"),
        ("03", "NEURAL ENCODING",  "128-dimension vector embeddings\ngenerated via deep ResNet model",      "#FFB300"),
        ("04", "VECTOR MATCHING",  "Cosine similarity comparison\nagainst registered face database",        "#FF6B6B"),
        ("05", "DECISION ENGINE",  "Threshold validation (>0.92)\ndetermines identity confidence",          "#C77DFF"),
        ("06", "ATTENDANCE LOG",   "Timestamped record written to\nSQLite with SHA-256 integrity hash",    "#00D4FF"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pulse_pos  = 0.0          # 0.0 → 1.0 along current segment
        self._active_seg = 0            # which connector is animating
        self._node_glow  = [0.0] * len(self.STEPS)   # glow intensity per node
        self._completed  = set()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)           # ~60 fps

        self.setMinimumHeight(len(self.STEPS) * 110)

    def _tick(self):
        speed = 0.012
        self._pulse_pos += speed

        # Glow the current node
        seg = self._active_seg
        if seg < len(self.STEPS):
            self._node_glow[seg] = min(1.0, self._node_glow[seg] + 0.04)

        if self._pulse_pos >= 1.0:
            self._pulse_pos = 0.0
            self._completed.add(self._active_seg)
            self._active_seg = (self._active_seg + 1) % (len(self.STEPS) - 1)

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w        = self.width()
        node_x   = w // 2
        step_h   = 110
        node_r   = 22
        badge_r  = 14

        for i, (num, title, desc, color) in enumerate(self.STEPS):
            cy = 30 + i * step_h
            qc = QColor(color)

            # ── Connector line to next node ──────────────────────────────────
            if i < len(self.STEPS) - 1:
                next_cy = 30 + (i + 1) * step_h
                line_top    = cy + node_r
                line_bottom = next_cy - node_r

                # Background track
                track_pen = QPen(QColor("#1E1E1E"), 2)
                p.setPen(track_pen)
                p.drawLine(node_x, line_top, node_x, line_bottom)

                # Completed segments — solid glow line
                if i in self._completed:
                    glow_pen = QPen(QColor(color), 2)
                    glow_pen.setStyle(Qt.SolidLine)
                    p.setPen(glow_pen)
                    p.drawLine(node_x, line_top, node_x, line_bottom)

                # Active segment — travelling pulse dot
                if i == self._active_seg:
                    py = int(line_top + self._pulse_pos * (line_bottom - line_top))
                    # Trail
                    for t in range(8):
                        trail_y   = py - t * 4
                        alpha     = int(200 * (1 - t / 8))
                        trail_r   = max(1, 4 - t)
                        trail_col = QColor(color)
                        trail_col.setAlpha(alpha)
                        p.setPen(Qt.NoPen)
                        p.setBrush(QBrush(trail_col))
                        p.drawEllipse(node_x - trail_r, trail_y - trail_r,
                                      trail_r * 2, trail_r * 2)

                    # Pulse head
                    p.setPen(Qt.NoPen)
                    p.setBrush(QBrush(QColor(color)))
                    p.drawEllipse(node_x - 5, py - 5, 10, 10)

            # ── Node outer glow ring ─────────────────────────────────────────
            glow_alpha = int(60 * self._node_glow[i])
            glow_col   = QColor(color)
            glow_col.setAlpha(glow_alpha)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(glow_col))
            p.drawEllipse(node_x - node_r - 8, cy - node_r - 8,
                          (node_r + 8) * 2, (node_r + 8) * 2)

            # ── Node circle ──────────────────────────────────────────────────
            if i in self._completed or i == self._active_seg:
                node_col = QColor(color)
                node_col.setAlpha(220)
            else:
                node_col = QColor("#1C1C1C")

            p.setBrush(QBrush(node_col))
            border_pen = QPen(QColor(color), 2)
            p.setPen(border_pen)
            p.drawEllipse(node_x - node_r, cy - node_r, node_r * 2, node_r * 2)

            # ── Step number badge ────────────────────────────────────────────
            badge_col = QColor(color) if i in self._completed else QColor("#0F0F0F")
            p.setBrush(QBrush(badge_col))
            p.setPen(Qt.NoPen)
            p.drawEllipse(node_x - badge_r, cy - badge_r, badge_r * 2, badge_r * 2)

            font = QFont("Consolas", 8, QFont.Bold)
            p.setFont(font)
            text_col = QColor("#0F0F0F") if i in self._completed else QColor(color)
            p.setPen(text_col)
            p.drawText(QtCore.QRect(node_x - badge_r, cy - badge_r,
                                    badge_r * 2, badge_r * 2),
                       Qt.AlignCenter, num)

            # ── Right-side title + description ───────────────────────────────
            title_font = QFont("Segoe UI", 11, QFont.Bold)
            p.setFont(title_font)
            p.setPen(QColor(color) if i in self._completed or i == self._active_seg
                     else QColor("#555"))
            p.drawText(node_x + node_r + 16, cy - 10, title)

            desc_font = QFont("Segoe UI", 9)
            p.setFont(desc_font)
            p.setPen(QColor("#666") if i not in self._completed else QColor("#999"))
            for j, line in enumerate(desc.split("\n")):
                p.drawText(node_x + node_r + 16, cy + 8 + j * 16, line)

            # ── Left-side status badge ────────────────────────────────────────
            status_x = node_x - node_r - 70
            if i in self._completed:
                s_col  = QColor("#00FFB3")
                s_text = "DONE"
            elif i == self._active_seg:
                s_col  = QColor(color)
                s_text = "ACTIVE"
            else:
                s_col  = QColor("#white")
                s_text = "WAIT"

            s_rect = QtCore.QRect(status_x - 28, cy - 10, 56, 20)
            s_bg   = QColor(s_col)
            s_bg.setAlpha(30)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(s_bg))
            path = QPainterPath()
            path.addRoundedRect(s_rect.x(), s_rect.y(),
                                s_rect.width(), s_rect.height(), 4, 4)
            p.drawPath(path)
            p.setPen(s_col)
            badge_font = QFont("Consolas", 7, QFont.Bold)
            p.setFont(badge_font)
            p.drawText(s_rect, Qt.AlignCenter, s_text)


# ──────────────────────────────────────────────────────────────────────────────
# STAT CARD WIDGET
# ──────────────────────────────────────────────────────────────────────────────

class StatCard(QtWidgets.QFrame):
    def __init__(self, title, value, color, subtitle="", value_label_name="", parent=None):
        super().__init__(parent)
        self._value_label_name = value_label_name
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #161616, stop:1 #111111);
                border-radius: 12px;
                border: 1px solid #222;
                border-top: 2px solid {color};
            }}
        """)
        self.setMinimumHeight(90)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)

        t = QtWidgets.QLabel(title)
        t.setStyleSheet("color:#555; font-size:10px; font-weight:600; letter-spacing:1px;")
        lay.addWidget(t)

        v = QtWidgets.QLabel(value)
        v.setStyleSheet(f"color:{color}; font-size:26px; font-weight:700; font-family:'Consolas';")
        if hasattr(self, "_value_label_name") and self._value_label_name:
            v.setObjectName(self._value_label_name)
        self.value_label = v   # always expose directly
        lay.addWidget(v)

        if subtitle:
            s = QtWidgets.QLabel(subtitle)
            s.setStyleSheet("color:#444; font-size:10px;")
            lay.addWidget(s)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN UI CLASS
# ──────────────────────────────────────────────────────────────────────────────

class Ui_InformationPopup(object):

    # Public labels wired by InfoDialog in main.py
    v_lab_time = None
    v_lab_acc  = None

    def setupUi(self, Dialog):
        Dialog.setWindowTitle("System Intelligence")
        Dialog.resize(720, 580)
        Dialog.setMinimumSize(680, 520)
        Dialog.setMaximumSize(760, 640)

        Dialog.setStyleSheet("""
            QWidget {
                background-color: #0D0D0D;
                color: #EAEAEA;
                font-family: 'Segoe UI';
            }
            QScrollBar:vertical {
                background: #111;
                width: 6px;
                border: none;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #2A2A2A;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #3A3A3A; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """)

        # ── Root layout ───────────────────────────────────────────────────────
        root = QtWidgets.QVBoxLayout(Dialog)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────────
        top_bar = QtWidgets.QFrame()
        top_bar.setFixedHeight(48)
        top_bar.setStyleSheet("""
            QFrame {
                background: #111;
                border-bottom: 1px solid #1E1E1E;
            }
        """)
        top_lay = QtWidgets.QHBoxLayout(top_bar)
        top_lay.setContentsMargins(20, 0, 20, 0)

        dot_row = QtWidgets.QHBoxLayout()
        dot_row.setSpacing(6)
        for col in ("#FF5F57", "#FEBC2E", "#28C840"):
            dot = QtWidgets.QLabel("●")
            dot.setStyleSheet(f"color: {col}; font-size: 11px;")
            dot_row.addWidget(dot)
        top_lay.addLayout(dot_row)

        title_lbl = QtWidgets.QLabel("SYSTEM  INFORMATION")
        title_lbl.setStyleSheet("""
            color: #333;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 3px;
            font-family: 'Consolas';
        """)
        title_lbl.setAlignment(Qt.AlignCenter)
        top_lay.addWidget(title_lbl, 1)

        ver_lbl = QtWidgets.QLabel("v1.2.0")
        ver_lbl.setStyleSheet("color: #333; font-size: 10px; font-family:'Consolas';")
        top_lay.addWidget(ver_lbl)

        root.addWidget(top_bar)

        # ── Body ──────────────────────────────────────────────────────────────
        body = QtWidgets.QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet("QFrame { background: #0F0F0F; border-right: 1px solid #1A1A1A; }")
        sidebar_lay = QtWidgets.QVBoxLayout(sidebar)
        sidebar_lay.setContentsMargins(12, 20, 12, 20)
        sidebar_lay.setSpacing(4)

        self.sidebar_list = QtWidgets.QListWidget()
        self.sidebar_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 11px 14px;
                border-radius: 8px;
                color: #555;
                font-size: 12px;
                font-weight: 500;
            }
            QListWidget::item:selected {
                background: #161616;
                color: #00D4FF;
                border: 1px solid #1E2A33;
            }
            QListWidget::item:hover:!selected {
                background: #141414;
                color: #888;
            }
        """)

        nav_items = [
            ("📊", "System Status"),
            ("🧠", "Logic Pipeline"),
            ("🛠️", "Tech Specs"),
            ("🛡️", "Privacy"),
            ("👨‍💻", "Dev Credits"),
        ]
        for icon, label in nav_items:
            item = QtWidgets.QListWidgetItem(f"  {icon}  {label}")
            self.sidebar_list.addItem(item)

        sidebar_lay.addWidget(self.sidebar_list)
        sidebar_lay.addStretch()

        # Animated accent bar
        self.highlight_bar = QtWidgets.QFrame(self.sidebar_list)
        self.highlight_bar.setStyleSheet("background: #00D4FF; border-radius: 2px;")
        self.highlight_bar.setGeometry(0, 0, 3, 40)
        self.highlight_bar.show()

        self.anim = QPropertyAnimation(self.highlight_bar, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.sidebar_list.currentRowChanged.connect(self._animate_sidebar)

        body.addWidget(sidebar)

        # ── Stack ─────────────────────────────────────────────────────────────
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: #0D0D0D; }")
        self.sidebar_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        body.addWidget(self.stack, 1)

        # ── PAGE 0: System Status ─────────────────────────────────────────────
        self._build_status_page()

        # ── PAGE 1: Logic Pipeline ────────────────────────────────────────────
        self._build_pipeline_page()

        # ── PAGE 2: Tech Specs ────────────────────────────────────────────────
        self._build_tech_page()

        # ── PAGE 3: Privacy ───────────────────────────────────────────────────
        self._build_privacy_page()

        # ── PAGE 4: Dev Credits ───────────────────────────────────────────────
        self._build_dev_page()

        # ── Footer ────────────────────────────────────────────────────────────
        footer = QtWidgets.QFrame()
        footer.setFixedHeight(44)
        footer.setStyleSheet("QFrame { background: #0F0F0F; border-top: 1px solid #1A1A1A; }")
        footer_lay = QtWidgets.QHBoxLayout(footer)
        footer_lay.setContentsMargins(20, 0, 20, 0)

        status_dot = QtWidgets.QLabel("● SYSTEM OPERATIONAL")
        status_dot.setStyleSheet("color: #28C840; font-size: 10px; font-family:'Consolas'; letter-spacing:1px;")
        footer_lay.addWidget(status_dot)
        footer_lay.addStretch()

        self.close_btn = QtWidgets.QPushButton("✕  Close")
        self.close_btn.setFixedSize(90, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #1A1A1A;
                border: 1px solid #2A2A2A;
                border-radius: 6px;
                color: #888;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #222;
                color: #EEE;
                border-color: #444;
            }
        """)
        footer_lay.addWidget(self.close_btn)
        root.addWidget(footer)

        self.sidebar_list.setCurrentRow(0)

    # ── Page builders ─────────────────────────────────────────────────────────

    def _scrollable(self, widget):
        """Wrap a widget in a scroll area and return the scroll area."""
        sa = QtWidgets.QScrollArea()
        sa.setWidgetResizable(True)
        sa.setFrameShape(QtWidgets.QFrame.NoFrame)
        sa.setStyleSheet("QScrollArea { background: transparent; }")
        sa.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setWidget(widget)
        return sa

    def _section(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet("""
            color: #444;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 2px;
            font-family: 'Consolas';
            padding-bottom: 6px;
        """)
        return lbl

    def _build_status_page(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QtWidgets.QVBoxLayout(page)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(20)

        # Hero banner
        banner = QtWidgets.QFrame()
        banner.setFixedHeight(80)
        banner.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #001A26, stop:0.5 #00111A, stop:1 #000D14);
            border-radius: 12px;
            border: 1px solid #003347;
        }
        """)

        b_lay = QtWidgets.QHBoxLayout(banner)
        b_lay.setContentsMargins(24, 0, 24, 0)

        b_title = QtWidgets.QLabel("SMART ATTENDANCE SYSTEM")
        b_title.setAlignment(QtCore.Qt.AlignCenter)
        b_title.setStyleSheet("""
        color:#00D4FF;
        font-size:18px;
        font-weight:700;
        letter-spacing:2px;
        font-family:'Consolas';
        """)

        b_lay.addWidget(b_title)

        lay.addWidget(banner)

        # Stat cards grid
        lay.addWidget(self._section("LIVE METRICS"))
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(12)

        # Accuracy card — value_label exposed as .value_label
        acc_card  = StatCard("MODEL ACCURACY", "—", "#00D4FF",
                             subtitle="Waiting for camera…",
                             value_label_name="v_lab_acc")
        # Inference time card
        time_card = StatCard("INFERENCE TIME", "—", "#FFB300",
                             subtitle="Waiting for camera…",
                             value_label_name="v_lab_time")

        # Store direct references so update_live_stats() can reach them
        self.v_lab_acc  = acc_card.value_label
        self.v_lab_time = time_card.value_label

        grid.addWidget(acc_card,  0, 0)
        grid.addWidget(time_card, 0, 1)
        grid.addWidget(StatCard("ACTIVE THREADS", "4",   "#00FFB3", "Parallel workers"),    1, 0)
        grid.addWidget(StatCard("LATENCY STATUS", "LOW", "#FF6B6B", "Network + DB combined"), 1, 1)
        lay.addLayout(grid)

        # Capabilities
        lay.addWidget(self._section("OPERATIONAL CAPABILITIES"))
        caps = [
            ("⚡", "Neural Processing",    "#00D4FF", "128-d vector embeddings for high-precision recognition"),
            ("🔀", "Heuristic Balancing",  "#FFB300", "Dynamic workload distribution across hardware threads"),
            ("🔒", "Encrypted Pipeline",   "#00FFB3", "Local processing with SHA-256 integrity validation"),
        ]
        for icon, title, color, desc in caps:
            row = QtWidgets.QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: #111;
                    border-radius: 10px;
                    border-left: 3px solid {color};
                }}
            """)
            r_lay = QtWidgets.QHBoxLayout(row)
            r_lay.setContentsMargins(16, 12, 16, 12)

            ic = QtWidgets.QLabel(icon)
            ic.setStyleSheet("font-size: 20px;")
            ic.setFixedWidth(32)
            r_lay.addWidget(ic)

            txt = QtWidgets.QVBoxLayout()
            t1  = QtWidgets.QLabel(title)
            t1.setStyleSheet(f"color:{color}; font-size:12px; font-weight:600;")
            t2  = QtWidgets.QLabel(desc)
            t2.setStyleSheet("color:#555; font-size:11px;")
            txt.addWidget(t1)
            txt.addWidget(t2)
            r_lay.addLayout(txt)
            lay.addWidget(row)

        lay.addStretch()
        self.stack.addWidget(self._scrollable(page))

    def _build_pipeline_page(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QtWidgets.QVBoxLayout(page)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        hdr = QtWidgets.QLabel("RECOGNITION  PIPELINE")
        hdr.setStyleSheet("""
            color: #00D4FF;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 3px;
            font-family: 'Consolas';
        """)
        sub = QtWidgets.QLabel("Live animated flow of the face-recognition process from camera to database")
        sub.setStyleSheet("color: #444; font-size: 11px;")
        lay.addWidget(hdr)
        lay.addWidget(sub)

        # Separator
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color: #1A1A1A;")
        lay.addWidget(sep)

        # The animated pipeline
        self.pipeline_widget = PipelineWidget()
        lay.addWidget(self.pipeline_widget)
        lay.addStretch()

        self.stack.addWidget(self._scrollable(page))

    def _build_tech_page(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QtWidgets.QVBoxLayout(page)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        lay.addWidget(self._section("TECHNICAL SPECIFICATIONS"))

        specs = [
            ("Language",         "Python 3.10+",               "#00D4FF"),
            ("GUI Framework",    "PyQt5 (Qt 5.15)",             "#FFB300"),
            ("Face Recognition", "face_recognition + dlib",     "#00FFB3"),
            ("Camera Backend",   "OpenCV 4.x",                  "#FF6B6B"),
            ("Database",         "SQLite3 (local)",             "#C77DFF"),
            ("Email",            "smtplib / Gmail SMTP",        "#00D4FF"),
            ("Scheduler",        "APScheduler",                 "#FFB300"),
            ("Export",           "openpyxl (.xlsx)",            "#00FFB3"),
            ("Packaging",        "PyInstaller",                 "#FF6B6B"),
            ("Min RAM",          "4 GB recommended",            "#C77DFF"),
        ]

        for label, value, color in specs:
            row = QtWidgets.QFrame()
            row.setStyleSheet("""
                QFrame {
                    background: #111;
                    border-radius: 8px;
                    border: 1px solid #1A1A1A;
                }
                QFrame:hover { border-color: #2A2A2A; }
            """)
            r_lay = QtWidgets.QHBoxLayout(row)
            r_lay.setContentsMargins(16, 10, 16, 10)

            lbl = QtWidgets.QLabel(label)
            lbl.setStyleSheet("color:#555; font-size:11px; font-weight:600; font-family:'Consolas';")
            lbl.setFixedWidth(160)

            val = QtWidgets.QLabel(value)
            val.setStyleSheet(f"color:{color}; font-size:12px; font-family:'Segoe UI';")

            dot = QtWidgets.QLabel("━━")
            dot.setStyleSheet(f"color:{color}; opacity:0.3;")
            dot.setFixedWidth(30)

            r_lay.addWidget(lbl)
            r_lay.addWidget(dot)
            r_lay.addWidget(val)
            r_lay.addStretch()
            lay.addWidget(row)

        lay.addStretch()
        self.stack.addWidget(self._scrollable(page))

    def _build_privacy_page(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QtWidgets.QVBoxLayout(page)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        lay.addWidget(self._section("PRIVACY & DATA POLICY"))

        policies = [
            ("🔒", "Local Storage Only",
             "#00D4FF",
             "All biometric data is stored exclusively on the local device.\n"
             "No face images or embeddings are ever transmitted externally."),
            ("☁️", "No Cloud Transmission",
             "#00FFB3",
             "The system operates fully offline. Attendance records, face encodings,\n"
             "and student data never leave the host machine."),
            ("📋", "GDPR Compliant",
             "#FFB300",
             "Data collection is limited to what is necessary for attendance.\n"
             "Students are informed and consent is obtained before enrollment."),
            ("🗑️", "Right to Erasure",
             "#FF6B6B",
             "Any student record including face image can be permanently deleted\n"
             "at any time by the administrator via Student Management."),
            ("🔐", "Integrity Validation",
             "#C77DFF",
             "SHA-256 hashing is applied to attendance logs to detect\n"
             "any unauthorized tampering with historical records."),
        ]

        for icon, title, color, body_text in policies:
            card = QtWidgets.QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: #0F0F0F;
                    border-radius: 12px;
                    border: 1px solid #1A1A1A;
                    border-left: 3px solid {color};
                }}
            """)
            c_lay = QtWidgets.QHBoxLayout(card)
            c_lay.setContentsMargins(16, 14, 16, 14)
            c_lay.setSpacing(14)

            ic = QtWidgets.QLabel(icon)
            ic.setStyleSheet("font-size: 22px;")
            ic.setFixedWidth(30)
            ic.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            c_lay.addWidget(ic)

            txt_lay = QtWidgets.QVBoxLayout()
            txt_lay.setSpacing(4)
            t = QtWidgets.QLabel(title)
            t.setStyleSheet(f"color:{color}; font-size:13px; font-weight:600;")
            d = QtWidgets.QLabel(body_text)
            d.setStyleSheet("color:#555; font-size:11px; line-height:160%;")
            d.setWordWrap(True)
            txt_lay.addWidget(t)
            txt_lay.addWidget(d)
            c_lay.addLayout(txt_lay)
            lay.addWidget(card)

        lay.addStretch()
        self.stack.addWidget(self._scrollable(page))

    def _build_dev_page(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QtWidgets.QVBoxLayout(page)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(12)

        lay.addWidget(self._section("DEVELOPMENT TEAM"))

        # (initials, name, role, color, field_tags)
        team = [
            ("JC", "Jay Chettri",      "Lead Developer · System Architecture & Backend",
             "#FFB300",
             [("UI Design", "#FFB300"), ("Stylesheets", "#FFB300"),
              ("Animations", "#FFB300"), ("Dashboard", "#FFB300")]),

            ("SG", "Sahil Gupta",         "Face Recognition Engine & Frontend",
             "#00D4FF",
             [("Face Recognition", "#00D4FF"), ("PyQt5 UI", "#00D4FF"),
              ("Blink Detection", "#00D4FF"), ("Attendance Logic", "#00D4FF")]),

            ("PR", "Prayash Ranapaheli", "Database, Reports & Notification System",
             "#00FFB3",
             [("SQLite DB", "#00FFB3"), ("Schema Design", "#00FFB3"),
              ("Reports", "#00FFB3"), ("Scheduler", "#00FFB3")]),

            ("AR", "Amar Rai",            "Camera Capture & Student Registration",
             "#FF6B6B",
            [("camera Thread", "#FF6B6B"), ("Multi-Image Capture",  "#FF6B6B"),
              ("Blur Detection",  "#FF6B6B"), ("Image Preprocessing", "#FF6B6B")]),
        ]

        for initials, name, role, color, fields in team:
            card = QtWidgets.QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: #111;
                    border-radius: 12px;
                    border: 1px solid #1E1E1E;
                    border-left: 3px solid {color};
                }}
                QFrame:hover {{
                    border-color: {color};
                    background: #131313;
                }}
            """)
            c_lay = QtWidgets.QVBoxLayout(card)
            c_lay.setContentsMargins(16, 14, 16, 14)
            c_lay.setSpacing(8)

            # ── Top row: avatar + name/role ───────────────────────────
            top_row = QtWidgets.QHBoxLayout()
            top_row.setSpacing(14)

            # Avatar with solid color background
            avatar = QtWidgets.QLabel(initials)
            avatar.setFixedSize(46, 46)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: {color};
                    color: #0D0D0D;
                    border-radius: 23px;
                    font-size: 14px;
                    font-weight: 800;
                    font-family: 'Consolas';
                }}
            """)
            top_row.addWidget(avatar)

            # Name + role
            name_col = QtWidgets.QVBoxLayout()
            name_col.setSpacing(2)
            n_lbl = QtWidgets.QLabel(name)
            n_lbl.setStyleSheet("color:#EEE; font-size:13px; font-weight:700;")
            r_lbl = QtWidgets.QLabel(role)
            r_lbl.setStyleSheet(f"color:{color}; font-size:10px; font-weight:500; opacity:0.8;")
            name_col.addWidget(n_lbl)
            name_col.addWidget(r_lbl)
            top_row.addLayout(name_col)
            top_row.addStretch()

            # Online dot
            dot = QtWidgets.QLabel("● Active")
            dot.setStyleSheet(f"color:{color}; font-size:9px; font-family:'Consolas';")
            top_row.addWidget(dot)
            c_lay.addLayout(top_row)

            # ── Field tags row ────────────────────────────────────────
            tags_row = QtWidgets.QHBoxLayout()
            tags_row.setSpacing(6)
            tags_row.setContentsMargins(0, 0, 0, 0)
            for tag_text, tag_col in fields:
                tag = QtWidgets.QLabel(tag_text)
                tag.setStyleSheet(f"""
                    QLabel {{
                        background: transparent;
                        color: {tag_col};
                        border: none;
                        padding: 2px 4px;
                        font-size: 9px;
                        font-weight: 600;
                        font-family: 'Consolas';
                    }}
                """)
                tags_row.addWidget(tag)
            tags_row.addStretch()
            c_lay.addLayout(tags_row)

            lay.addWidget(card)

        # Built with section
        lay.addSpacing(8)
        lay.addWidget(self._section("BUILT WITH"))
        tech_row = QtWidgets.QHBoxLayout()
        tech_row.setSpacing(8)
        for tech, col in [("Python", "#3776AB"),   # Python official blue
                          ("PyQt5", "#41CD52"),    # Qt official green
                          ("OpenCV", "#5C8DBC"),   # OpenCV blue
                          ("dlib",  "#E8E8E8"),    # dlib is neutral/white
                          ("SQLite", "#0F80CC")]:
            chip = QtWidgets.QLabel(tech)
            chip.setStyleSheet(f"""
                QLabel {{
                    background: #161616;
                    color: {col};
                    border: 1px solid #2A2A2A;
                    border-radius: 12px;
                    padding: 4px 14px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)
            tech_row.addWidget(chip)
        tech_row.addStretch()
        lay.addLayout(tech_row)

        lay.addStretch()
        self.stack.addWidget(self._scrollable(page))

    # ── Sidebar animation ─────────────────────────────────────────────────────

    def _animate_sidebar(self, index):
        item = self.sidebar_list.item(index)
        if not item:
            return
        r = self.sidebar_list.visualItemRect(item)
        self.anim.stop()
        self.anim.setStartValue(self.highlight_bar.geometry())
        self.anim.setEndValue(QRect(0, r.top(), 3, r.height()))
        self.anim.start()

    # ── Public slots wired by InfoDialog ─────────────────────────────────────

    def refresh_stats(self, inf_time, accuracy):
        if self.v_lab_time:
            self.v_lab_time.setText(f"{inf_time:.3f}s")
        if self.v_lab_acc:
            if accuracy > 0:
                self.v_lab_acc.setText(f"{accuracy:.1f}%")
            else:
                self.v_lab_acc.setText("Scanning…")
