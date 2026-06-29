"""
popups/chatbot_popup.py
AI-powered attendance chatbot.
ChatbotWidget  — embeddable QWidget (used inside stackedWidget_3)
ChatbotPopup   — legacy QDialog wrapper (kept for compatibility)
"""

import json
import os
from datetime import datetime, timedelta

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QWidget,
    QSizePolicy, QFrame
)

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from utils.attendance_report_generator import AttendanceReportGenerator
    REPORT_GEN_AVAILABLE = True
except ImportError:
    REPORT_GEN_AVAILABLE = False


# ---------------------------------------------------------------------------
# Background worker — calls Gemini without blocking the GUI
# ---------------------------------------------------------------------------

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, system_prompt, parent=None):
        super().__init__(parent)
        self.messages      = messages
        self.system_prompt = system_prompt

    def run(self):
        if not GEMINI_AVAILABLE:
            self.error_occurred.emit(
                "Gemini SDK not installed.\nRun: pip install google-genai"
            )
            return
        try:
            api_key = "AQ.Ab8RN6Ik_6-vAswFT7JDNdXEuwv9VyZrlDs1MrHgdNjVjfQDZQ"
            if not api_key:
                self.error_occurred.emit("GEMINI_API_KEY environment variable not found.")
                return

            client       = genai.Client(api_key=api_key)
            conversation = ""
            for msg in self.messages:
                conversation += f"{msg.get('role','user')}: {msg.get('content','')}\n"

            prompt = f"{self.system_prompt}\n\nConversation:\n{conversation}\nAnswer the teacher's latest question."
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            self.response_ready.emit(response.text)
        except Exception as exc:
            self.error_occurred.emit(f"Gemini API error: {exc}")


# ---------------------------------------------------------------------------
# Chat bubble
# ---------------------------------------------------------------------------

class ChatBubble(QLabel):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setText(text)
        self.setTextFormat(Qt.RichText)
        self.setOpenExternalLinks(False)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMaximumWidth(520)

        if is_user:
            self.setStyleSheet("""
                QLabel {
                    background-color: #003d52;
                    color: #E6EDF3;
                    border: 1px solid #005f7a;
                    border-radius: 12px;
                    border-bottom-right-radius: 3px;
                    padding: 10px 14px;
                    font-size: 13px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #161B22;
                    color: #E6EDF3;
                    border: 1px solid #30363D;
                    border-radius: 12px;
                    border-bottom-left-radius: 3px;
                    padding: 10px 14px;
                    font-size: 13px;
                }
            """)


# ---------------------------------------------------------------------------
# Suggestion chip
# ---------------------------------------------------------------------------

class SuggestionChip(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #21262D;
                color: #8B949E;
                border: 1px solid #30363D;
                border-radius: 14px;
                padding: 5px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                border-color: #00D4FF;
                color: #00D4FF;
                background-color: #00D4FF11;
            }
        """)


# ---------------------------------------------------------------------------
# ChatbotWidget  — embeddable QWidget (the real implementation)
# ---------------------------------------------------------------------------

class ChatbotWidget(QWidget):
    """
    Full chatbot UI as a plain QWidget so it can be embedded
    directly inside stackedWidget_3 (no separate window).
    """

    SUGGESTIONS = [
        "Today's attendance summary",
        "Who is absent today?",
        "Who is not marked today?",
        "Students below 75% attendance",
        "Today's full sheet",
        "Finalize attendance",
        "Generate daily PDF report",
        "Generate monthly PDF report",
    ]

    def __init__(self, db, attendance_manager, teacher_account_id,
                 current_user=None, parent=None):
        super().__init__(parent)
        self.db                   = db
        self.attendance_manager   = attendance_manager
        self.teacher_account_id   = teacher_account_id
        self.current_user         = current_user or {}
        self.conversation_history = []
        self._worker              = None
        self._thinking_label      = None

        try:
            if not self.attendance_manager.db:
                self.attendance_manager.connect()
        except Exception:
            pass

        if REPORT_GEN_AVAILABLE:
            safe_email = self.current_user.get("email", "unknown") \
                             .replace("@", "_").replace(".", "_")
            self.report_generator = AttendanceReportGenerator(
                username=safe_email,
                account_id=self.teacher_account_id,
            )
        else:
            self.report_generator = None

        self.setStyleSheet("QWidget { background-color: #0D1117; }")
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(
            "QFrame { background-color: #161B22; border-bottom: 1px solid #30363D; }"
        )
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(16, 0, 16, 0)

        icon_lbl = QLabel("🤖")
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent;")

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        t1 = QLabel("Attendance AI")
        t1.setStyleSheet(
            "color: #E6EDF3; font-size: 14px; font-weight: 600; background: transparent;"
        )
        t2 = QLabel("Ask me anything about your class")
        t2.setStyleSheet("color: #8B949E; font-size: 11px; background: transparent;")
        title_col.addWidget(t1)
        title_col.addWidget(t2)

        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #8B949E;
                border: 1px solid #30363D; border-radius: 6px;
                padding: 4px 10px; font-size: 12px;
            }
            QPushButton:hover { color: #E6EDF3; border-color: #8B949E; }
        """)
        clear_btn.clicked.connect(self._clear_chat)

        tb_lay.addWidget(icon_lbl)
        tb_lay.addSpacing(10)
        tb_lay.addLayout(title_col)
        tb_lay.addStretch()
        tb_lay.addWidget(clear_btn)
        root.addWidget(topbar)

        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea { background: #0D1117; border: none; }"
            "QScrollBar:vertical { width: 6px; background: #0D1117; }"
            "QScrollBar::handle:vertical { background: #30363D; border-radius: 3px; }"
        )

        self.msg_container = QWidget()
        self.msg_container.setStyleSheet("background: #0D1117;")
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.setContentsMargins(16, 16, 16, 16)
        self.msg_layout.setSpacing(10)
        self.msg_layout.addStretch()

        self.scroll_area.setWidget(self.msg_container)
        root.addWidget(self.scroll_area, 1)

        # Suggestion chips
        chips_frame = QFrame()
        chips_frame.setStyleSheet(
            "QFrame { background: #0D1117; border-top: 1px solid #21262D; }"
        )
        chips_lay = QVBoxLayout(chips_frame)
        chips_lay.setContentsMargins(14, 8, 14, 8)
        chips_lay.setSpacing(6)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row1.setSpacing(6)
        row2.setSpacing(6)
        mid = len(self.SUGGESTIONS) // 2
        for i, text in enumerate(self.SUGGESTIONS):
            chip = SuggestionChip(text)
            chip.clicked.connect(lambda _, t=text: self._send(t))
            (row1 if i < mid else row2).addWidget(chip)
        row1.addStretch()
        row2.addStretch()
        chips_lay.addLayout(row1)
        chips_lay.addLayout(row2)
        root.addWidget(chips_frame)

        # Input row
        input_frame = QFrame()
        input_frame.setFixedHeight(56)
        input_frame.setStyleSheet(
            "QFrame { background: #161B22; border-top: 1px solid #30363D; }"
        )
        inp_lay = QHBoxLayout(input_frame)
        inp_lay.setContentsMargins(14, 10, 14, 10)
        inp_lay.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about attendance, reports, students…")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: #0D1117; color: #E6EDF3;
                border: 1px solid #30363D; border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #00D4FF; }
        """)
        self.input_field.returnPressed.connect(self._on_send_click)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(70)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #00D4FF; color: #000; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 600; padding: 8px 0;
            }
            QPushButton:hover { background: #00b8d9; }
            QPushButton:disabled { background: #30363D; color: #8B949E; }
        """)
        self.send_btn.clicked.connect(self._on_send_click)

        inp_lay.addWidget(self.input_field)
        inp_lay.addWidget(self.send_btn)
        root.addWidget(input_frame)

        # Welcome message
        self._add_bot_message(
            "👋 Hi! I'm your <b>Attendance AI</b>.<br><br>"
            "I can answer questions about today's attendance, "
            "absent students, low-attendance alerts, trends, "
            "and more — all based on your live class data.<br><br>"
            "Type a question or tap one of the suggestions below."
        )

    # ── Data helpers ───────────────────────────────────────────────────────

    def _gather_context(self) -> str:
        try:
            today    = datetime.now().strftime("%Y-%m-%d")
            records  = self.attendance_manager.get_full_report(self.teacher_account_id)
            students = self.db.get_students_by_account(self.teacher_account_id)

            agg = {}
            for s in students:
                roll = s.get("roll", "")
                agg[roll] = {
                    "name": s.get("name", ""), "dept": s.get("dept", ""),
                    "year": s.get("year", ""), "email": s.get("email", ""),
                    "present": 0, "late": 0, "absent": 0, "total": 0,
                    "today": "absent", "late_dates": [],
                }

            date_set = set()
            for r in records:
                roll   = r.get("roll", "")
                date   = r.get("date", "")
                status = str(r.get("status", "")).strip().lower()
                if roll not in agg:
                    continue
                date_set.add(date)
                agg[roll]["total"] += 1
                if status == "present":
                    agg[roll]["present"] += 1
                    if date == today:
                        agg[roll]["today"] = "present"
                elif status == "late":
                    agg[roll]["late"] += 1
                    agg[roll]["late_dates"].append(date)
                    if date == today:
                        agg[roll]["today"] = "late"
                else:
                    agg[roll]["absent"] += 1

            total_days = max(len(date_set), 1)
            for roll, info in agg.items():
                attended    = info["present"] + info["late"]
                info["pct"] = round(attended / total_days * 100, 1)

            context = {
                "teacher": self.current_user.get("name", "Teacher"),
                "class": self.current_user.get("class_name", ""),
                "subject": self.current_user.get("subject_name", ""),
                "today": today,
                "total_students": len(students),
                "total_class_days": total_days,
                "students": list(agg.values()),
            }
            return json.dumps(context, indent=2)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    def _build_system_prompt(self) -> str:
        ctx = self._gather_context()
        return f"""You are an intelligent attendance assistant for a teacher's face-recognition attendance system.
You have access to the following real-time class data (JSON):

{ctx}

Your job:
- Answer the teacher's questions accurately using ONLY the data above.
- Be concise and friendly. Use bullet points or short tables for lists.
- For percentages, round to 1 decimal place.
- If asked to "send an email" or perform an action that requires the app,
  tell the teacher to use the relevant button in the dashboard instead.
- Never fabricate student data. If data is missing, say so.
- Today's date is {datetime.now().strftime("%A, %d %B %Y")}.
- When listing absent/late students, include their roll number and department.
- Highlight students below 75% attendance as needing attention.
"""

    # ── Local intent handler ───────────────────────────────────────────────

    def _handle_local_command(self, text: str):
        query = text.lower().strip()
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            if not self.attendance_manager.db:
                self.attendance_manager.connect()
        except Exception:
            pass

        try:
            records = self.attendance_manager.get_full_report(self.teacher_account_id)
        except Exception as exc:
            return f"⚠️ Could not fetch records: {exc}"

        try:
            today_sheet = self.attendance_manager.get_today_sheet(self.teacher_account_id)
        except Exception:
            today_sheet = []

        today_records = today_sheet if today_sheet else [
            r for r in records if r.get("date") == today
        ]

        # Present count
        if ("how many" in query or "count" in query) and "present" in query:
            count = sum(1 for r in today_records if r.get("status", "").lower() == "present")
            late  = sum(1 for r in today_records if r.get("status", "").lower() == "late")
            return (f"✅ <b>Present today:</b> {count} student(s)<br>"
                    f"🕐 <b>Late today:</b> {late} student(s)")

        # Absent count
        if ("how many" in query or "count" in query) and "absent" in query:
            absent_statuses = {"absent", "not marked", ""}
            count   = sum(1 for r in today_records if r.get("status", "").strip().lower() in absent_statuses)
            present = sum(1 for r in today_records if r.get("status", "").strip().lower() == "present")
            late    = sum(1 for r in today_records if r.get("status", "").strip().lower() == "late")
            total   = len(today_records)
            return (f"❌ <b>Absent / not marked today:</b> {count} student(s)<br>"
                    f"✅ Present: {present} &nbsp; 🕐 Late: {late} &nbsp; 👥 Total: {total}")

        # Today's summary
        if "today" in query and ("summary" in query or "attendance" in query):
            absent_statuses = {"absent", "not marked", ""}
            present  = sum(1 for r in today_records if r.get("status", "").strip().lower() == "present")
            late     = sum(1 for r in today_records if r.get("status", "").strip().lower() == "late")
            absent   = sum(1 for r in today_records if r.get("status", "").strip().lower() in absent_statuses)
            total    = len(today_records)
            attended = present + late
            pct      = round(attended / total * 100, 1) if total > 0 else 0
            return (f"📊 <b>Today's Attendance Summary</b> — {today}<br><br>"
                    f"✅ Present: <b>{present}</b><br>"
                    f"🕐 Late: <b>{late}</b><br>"
                    f"❌ Absent / not marked: <b>{absent}</b><br>"
                    f"👥 Total students: <b>{total}</b><br>"
                    f"📈 Attendance rate: <b>{pct}%</b>")

        # How many attended
        if "how many attended" in query or "how many came" in query:
            present = sum(1 for r in today_records if r.get("status", "").lower() == "present")
            late    = sum(1 for r in today_records if r.get("status", "").lower() == "late")
            return (f"👥 <b>{present + late}</b> student(s) attended today "
                    f"({present} present, {late} late).")

        # List absent students today
        if "who is absent" in query or "who's absent" in query or \
           ("absent" in query and ("list" in query or "who" in query)):
            absent_statuses = {"absent", "not marked", ""}
            absent = [
                f"• {r.get('name','Unknown')} ({r.get('roll','—')}) — {r.get('dept','—')}"
                for r in today_records
                if r.get("status", "").strip().lower() in absent_statuses
            ]
            if not absent:
                return "🎉 No absent students today! Full attendance."
            return (f"❌ <b>Absent students today ({len(absent)}):</b><br><br>"
                    + "<br>".join(absent))

        # List present students today
        if "who is present" in query or "who's present" in query or \
           ("present" in query and ("list" in query or "who" in query)):
            present_list = [
                f"• {r.get('name','Unknown')} ({r.get('roll','—')})"
                for r in today_records
                if r.get("status", "").lower() == "present"
            ]
            if not present_list:
                return "No students marked present yet today."
            return (f"✅ <b>Present students today ({len(present_list)}):</b><br><br>"
                    + "<br>".join(present_list))

        # Students below 75%
        if "below 75" in query or "under 75" in query or \
           ("75" in query and ("attendance" in query or "percent" in query or "%" in query)):
            try:
                context  = json.loads(self._gather_context())
                students = context.get("students", [])
                low = [f"• {s['name']} — <b>{s['pct']}%</b>"
                       for s in students if s.get("pct", 0) < 75]
                if not low:
                    return "✅ All students are above 75% attendance. Great job!"
                return (f"⚠️ <b>Students below 75% attendance ({len(low)}):</b><br><br>"
                        + "<br>".join(low))
            except Exception as exc:
                return f"⚠️ Error computing attendance percentages: {exc}"

        # Highest attendance
        if "highest" in query and "attendance" in query:
            try:
                context  = json.loads(self._gather_context())
                students = context.get("students", [])
                if not students:
                    return "No student data available."
                top = max(students, key=lambda s: s.get("pct", 0))
                return (f"🏆 <b>Highest attendance:</b><br><br>"
                        f"• {top['name']} — <b>{top['pct']}%</b>")
            except Exception as exc:
                return f"⚠️ Error: {exc}"

        # Students late more than N times
        if "late" in query and ("more than" in query or "times" in query or "3" in query):
            threshold = 3
            for word in query.split():
                if word.isdigit():
                    threshold = int(word)
                    break
            try:
                context  = json.loads(self._gather_context())
                students = context.get("students", [])
                flagged  = [f"• {s['name']} — late <b>{s.get('late',0)}</b> time(s)"
                            for s in students if s.get("late", 0) > threshold]
                if not flagged:
                    return f"✅ No students have been late more than {threshold} time(s)."
                return (f"🕐 <b>Students late more than {threshold} time(s):</b><br><br>"
                        + "<br>".join(flagged))
            except Exception as exc:
                return f"⚠️ Error: {exc}"

        # Absent 3+ days this week
        if "absent" in query and ("week" in query or "3+" in query or "3 days" in query):
            today_date = datetime.now().date()
            week_start = today_date - timedelta(days=today_date.weekday())
            week_dates = {(week_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)}
            week_records = [r for r in records if r.get("date", "") in week_dates]
            from collections import defaultdict
            absent_counts = defaultdict(lambda: {"name": "", "count": 0})
            for r in week_records:
                if r.get("status", "").lower() == "absent":
                    roll = r.get("roll", "")
                    absent_counts[roll]["name"]   = r.get("name", roll)
                    absent_counts[roll]["count"] += 1
            flagged = [f"• {info['name']} — absent <b>{info['count']}</b> day(s) this week"
                       for roll, info in absent_counts.items() if info["count"] >= 3]
            if not flagged:
                return "✅ No students have been absent 3+ days this week."
            return (f"📅 <b>Students absent 3+ days this week:</b><br><br>"
                    + "<br>".join(flagged))

        # Generate daily report
        if ("generate" in query or "create" in query or "export" in query) and \
           ("daily" in query or "today" in query) and \
           ("report" in query or "pdf" in query or "excel" in query or "xlsx" in query):
            if not self.report_generator:
                return "⚠️ Report generator not available. Check your installation."
            try:
                dept     = self.current_user.get("class_name", "")
                subject  = self.current_user.get("subject_name", "")
                want_pdf = "pdf" in query
                if want_pdf:
                    path = self.report_generator.generate_daily_pdf_report(
                        today_records, today, department=dept, subject=subject)
                    fmt = "PDF"
                else:
                    path = self.report_generator.generate_daily_report(
                        today_records, date_str=today, department=dept, subject=subject)
                    fmt = "Excel"
                present = sum(1 for r in today_records if r.get("status", "").lower() == "present")
                absent  = sum(1 for r in today_records if r.get("status", "").lower() == "absent")
                folder  = os.path.dirname(os.path.abspath(path))
                try:
                    os.startfile(folder)
                except Exception:
                    pass
                return (f"✅ <b>Daily {fmt} Report Generated</b><br><br>"
                        f"📅 Date: {today}<br>"
                        f"✅ Present: {present} &nbsp; ❌ Absent: {absent}<br><br>"
                        f"📁 Saved to:<br><code>{path}</code>")
            except Exception as exc:
                return f"⚠️ Failed to generate daily report: {exc}"

        # Generate monthly report
        if ("generate" in query or "create" in query or "export" in query) and \
           "monthly" in query and \
           ("report" in query or "pdf" in query or "excel" in query or "xlsx" in query):
            if not self.report_generator:
                return "⚠️ Report generator not available. Check your installation."
            try:
                now      = datetime.now()
                dept     = self.current_user.get("class_name", "")
                want_pdf = "pdf" in query
                if want_pdf:
                    path = self.report_generator.generate_monthly_pdf_report(
                        records, now.year, now.month, department=dept)
                    fmt = "PDF"
                else:
                    path = self.report_generator.generate_monthly_report(
                        records, year=now.year, month=now.month, department=dept)
                    fmt = "Excel"
                month_label = now.strftime("%B %Y")
                folder = os.path.dirname(os.path.abspath(path))
                try:
                    os.startfile(folder)
                except Exception:
                    pass
                return (f"✅ <b>Monthly {fmt} Report Generated</b><br><br>"
                        f"📅 Month: {month_label}<br>"
                        f"👥 Students: {len(self.db.get_students_by_account(self.teacher_account_id))}<br><br>"
                        f"📁 Saved to:<br><code>{path}</code>")
            except Exception as exc:
                return f"⚠️ Failed to generate monthly report: {exc}"

        # List all saved reports
        if ("list" in query or "show" in query or "all" in query) and "report" in query:
            if not self.report_generator:
                return "⚠️ Report generator not available."
            try:
                reports = self.report_generator.get_all_reports()
                if not reports:
                    return "📂 No reports have been generated yet."
                lines = [
                    f"• {r['filename']}  "
                    f"<span style='color:#8B949E;'>({r['modified'].strftime('%d %b %Y %H:%M')})</span>"
                    for r in reports[:10]
                ]
                suffix = (f"<br><span style='color:#8B949E;'>… and {len(reports)-10} more</span>"
                          if len(reports) > 10 else "")
                return (f"📁 <b>Saved Reports ({len(reports)}):</b><br><br>"
                        + "<br>".join(lines) + suffix)
            except Exception as exc:
                return f"⚠️ Error listing reports: {exc}"

        # Total students
        if ("how many" in query or "total" in query or "count" in query) and "student" in query:
            try:
                students = self.db.get_students_by_account(self.teacher_account_id)
                return f"👥 <b>Total students registered:</b> {len(students)}"
            except Exception as exc:
                return f"⚠️ Error: {exc}"

        # Search student by name / roll
        if ("find" in query or "search" in query or "look up" in query or
                "show student" in query or "student info" in query):
            try:
                stop_words = {"find", "search", "look", "up", "show",
                              "student", "info", "details", "for", "me", "the"}
                tokens = [t for t in query.split() if t not in stop_words]
                term   = " ".join(tokens).strip()
                if not term:
                    return "Please specify a student name or roll number to search."

                student = self.db.get_student_by_roll(term.upper())
                if not student:
                    student = self.db.get_student_by_name(term)
                if not student:
                    all_students = self.db.get_students_by_account(self.teacher_account_id)
                    matches = [s for s in all_students
                               if term in s.get("name", "").lower()
                               or term in s.get("roll", "").lower()]
                    if len(matches) == 1:
                        student = matches[0]
                    elif len(matches) > 1:
                        lines = [f"• {s['name']} ({s['roll']}) — {s.get('dept','')}"
                                 for s in matches[:10]]
                        return (f"🔍 <b>Multiple matches for '{term}':</b><br><br>"
                                + "<br>".join(lines))
                if not student:
                    return f"❌ No student found matching '<b>{term}</b>'."

                roll        = student.get("roll", "")
                att_records = self.db.get_attendance(roll)
                present     = sum(1 for r in att_records if r.get("status", "").lower() == "present")
                absent      = sum(1 for r in att_records if r.get("status", "").lower() == "absent")
                total       = len(att_records)
                pct         = round(present / total * 100, 1) if total > 0 else 0
                flag        = " ⚠️" if pct < 75 else " ✅"
                return (f"🎓 <b>Student Profile</b><br><br>"
                        f"👤 <b>Name:</b> {student.get('name','—')}<br>"
                        f"🪪 <b>Roll:</b> {student.get('roll','—')}<br>"
                        f"🏫 <b>Dept:</b> {student.get('dept','—')}<br>"
                        f"📅 <b>Year:</b> {student.get('year','—')}<br>"
                        f"📧 <b>Email:</b> {student.get('email','—')}<br><br>"
                        f"📊 <b>Attendance:</b> {present}/{total} days ({pct}%){flag}<br>"
                        f"❌ <b>Absent:</b> {absent} day(s)")
            except Exception as exc:
                return f"⚠️ Error looking up student: {exc}"

        # Today's full attendance sheet
        if ("today" in query and "sheet" in query) or \
           ("full" in query and ("list" in query or "attendance" in query)):
            try:
                sheet = self.db.get_today_attendance_sheet(self.teacher_account_id)
                if not sheet:
                    return "No attendance sheet found for today."
                present_list, absent_list, late_list, unmarked = [], [], [], []
                for r in sheet:
                    name   = r.get("name", "—")
                    roll   = r.get("roll", "—")
                    status = r.get("status", "").lower()
                    entry  = f"• {name} ({roll})"
                    if status == "present":
                        present_list.append(entry)
                    elif status == "absent":
                        absent_list.append(entry)
                    elif status == "late":
                        late_list.append(entry)
                    else:
                        unmarked.append(entry)
                parts = []
                if present_list:
                    parts.append(f"✅ <b>Present ({len(present_list)}):</b><br>" + "<br>".join(present_list))
                if late_list:
                    parts.append(f"🕐 <b>Late ({len(late_list)}):</b><br>" + "<br>".join(late_list))
                if absent_list:
                    parts.append(f"❌ <b>Absent ({len(absent_list)}):</b><br>" + "<br>".join(absent_list))
                if unmarked:
                    parts.append(f"⬜ <b>Not marked ({len(unmarked)}):</b><br>" + "<br>".join(unmarked))
                return (f"📋 <b>Today's Full Attendance Sheet — {today}</b><br><br>"
                        + "<br><br>".join(parts))
            except Exception as exc:
                return f"⚠️ Error fetching sheet: {exc}"

        # Student attendance history
        if ("history" in query or "record" in query) and ("of" in query or "for" in query):
            try:
                term = ""
                for kw in ("history of", "record for", "record of", "history for",
                           "attendance of", "attendance for"):
                    if kw in query:
                        term = query.split(kw, 1)[1].strip()
                        break
                if not term:
                    return "Please specify a student name or roll number."
                student = self.db.get_student_by_roll(term.upper()) or \
                          self.db.get_student_by_name(term)
                if not student:
                    all_s = self.db.get_students_by_account(self.teacher_account_id)
                    hits  = [s for s in all_s if term in s.get("name", "").lower()]
                    if hits:
                        student = hits[0]
                if not student:
                    return f"❌ No student found matching '<b>{term}</b>'."
                roll    = student.get("roll", "")
                history = self.db.get_attendance(roll)
                if not history:
                    return f"No attendance records found for <b>{student.get('name')}</b>."
                present = sum(1 for r in history if r.get("status", "").lower() == "present")
                total   = len(history)
                pct     = round(present / total * 100, 1) if total else 0
                lines   = [f"• {r['date']} — <b>{r['status']}</b>" for r in history[:10]]
                suffix  = (f"<br><span style='color:#8B949E;'>… and {total-10} more records</span>"
                           if total > 10 else "")
                return (f"📅 <b>Attendance History — {student.get('name')}</b><br>"
                        f"<span style='color:#8B949E;'>Roll: {roll}</span><br><br>"
                        f"📊 Overall: <b>{pct}%</b> ({present}/{total} days)<br><br>"
                        + "<br>".join(lines) + suffix)
            except Exception as exc:
                return f"⚠️ Error fetching history: {exc}"

        # Finalize attendance
        if ("finalize" in query or "close attendance" in query or
                ("mark" in query and "absent" in query and
                 ("remaining" in query or "unmarked" in query or "rest" in query))):
            try:
                sheet    = self.attendance_manager.get_today_sheet(self.teacher_account_id)
                unmarked = [r for r in sheet
                            if r.get("status", "").strip().lower() in ("", "not marked")]
                self.attendance_manager.finalize(self.teacher_account_id)
                if unmarked:
                    names = "<br>".join(f"• {r.get('name','—')} ({r.get('roll','—')})"
                                        for r in unmarked[:20])
                    return (f"✅ <b>Attendance finalized.</b><br><br>"
                            f"The following {len(unmarked)} student(s) were marked <b>Absent</b>:<br><br>"
                            + names)
                return "✅ Attendance finalized. All students were already marked."
            except Exception as exc:
                return f"⚠️ Could not finalize attendance: {exc}"

        # Mark a student present manually
        if "mark" in query and "present" in query:
            try:
                stop    = {"mark", "present", "as", "student"}
                tokens  = [t for t in query.split() if t not in stop]
                term    = " ".join(tokens).strip()
                if not term:
                    return "Please specify a student name or roll number to mark present."
                student = self.db.get_student_by_roll(term.upper()) or \
                          self.db.get_student_by_name(term)
                if not student:
                    all_s   = self.db.get_students_by_account(self.teacher_account_id)
                    matches = [s for s in all_s
                               if term in s.get("name", "").lower()
                               or term in s.get("roll", "").lower()]
                    if len(matches) == 1:
                        student = matches[0]
                    elif len(matches) > 1:
                        lines = [f"• {s['name']} ({s['roll']})" for s in matches[:8]]
                        return (f"🔍 Multiple matches for '<b>{term}</b>'. "
                                f"Please be more specific:<br><br>" + "<br>".join(lines))
                if not student:
                    return f"❌ No student found matching '<b>{term}</b>'."
                success = self.attendance_manager.mark_attendance(
                    student["roll"], self.teacher_account_id, status="Present")
                if success:
                    return (f"✅ <b>{student['name']}</b> ({student['roll']}) "
                            f"marked <b>Present</b> for {today}.")
                return f"⚠️ Could not mark {student['name']} present. Check attendance records."
            except Exception as exc:
                return f"⚠️ Error marking present: {exc}"

        # Not-marked / unmarked students today
        if ("not marked" in query or "unmarked" in query or
                ("pending" in query and "attendance" in query)):
            try:
                sheet    = self.attendance_manager.get_today_sheet(self.teacher_account_id)
                unmarked = [r for r in sheet
                            if r.get("status", "").strip().lower() in ("", "not marked")]
                if not unmarked:
                    return "✅ All students have been marked today."
                lines = [f"• {r.get('name','—')} ({r.get('roll','—')})" for r in unmarked]
                return (f"⬜ <b>Unmarked students today ({len(unmarked)}):</b><br><br>"
                        + "<br>".join(lines)
                        + "<br><br><span style='color:#8B949E;'>Tip: Say "
                        "<i>'finalize attendance'</i> to mark all as Absent.</span>")
            except Exception as exc:
                return f"⚠️ Error: {exc}"

        # Attendance stats for a specific student
        if ("stats" in query or "percentage" in query or "percent" in query) and \
           ("for" in query or "of" in query):
            try:
                term = ""
                for kw in ("percentage of", "percentage for", "percent of", "percent for",
                           "stats for", "stats of", "attendance of", "attendance for"):
                    if kw in query:
                        term = query.split(kw, 1)[1].strip()
                        break
                if not term:
                    return "Please specify a student name or roll number."
                student = self.db.get_student_by_roll(term.upper()) or \
                          self.db.get_student_by_name(term)
                if not student:
                    all_s   = self.db.get_students_by_account(self.teacher_account_id)
                    matches = [s for s in all_s if term in s.get("name", "").lower()]
                    if matches:
                        student = matches[0]
                if not student:
                    return f"❌ No student found matching '<b>{term}</b>'."
                history = self.db.get_attendance(student["roll"])
                present = sum(1 for r in history if r.get("status", "").lower() == "present")
                late    = sum(1 for r in history if r.get("status", "").lower() == "late")
                absent  = sum(1 for r in history if r.get("status", "").lower() == "absent")
                total   = len(history)
                pct     = round((present + late) / total * 100, 1) if total else 0
                flag    = "⚠️ Below threshold" if pct < 75 else "✅ Good standing"
                return (f"📊 <b>Attendance Stats — {student.get('name')}</b><br>"
                        f"<span style='color:#8B949E;'>Roll: {student.get('roll')}</span><br><br>"
                        f"✅ Present: <b>{present}</b><br>"
                        f"🕐 Late: <b>{late}</b><br>"
                        f"❌ Absent: <b>{absent}</b><br>"
                        f"📅 Total days: <b>{total}</b><br>"
                        f"📈 Attendance: <b>{pct}%</b>  {flag}")
            except Exception as exc:
                return f"⚠️ Error: {exc}"

        return None  # Fall through to Gemini

    # ── Message helpers ────────────────────────────────────────────────────

    def _add_bubble(self, text: str, is_user: bool):
        row    = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        bubble = ChatBubble(text, is_user)
        if is_user:
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()
        count = self.msg_layout.count()
        self.msg_layout.insertLayout(count - 1, row)
        QtCore.QTimer.singleShot(50, self._scroll_to_bottom)

    def _add_user_message(self, text: str):
        self._add_bubble(text, is_user=True)

    def _add_bot_message(self, text: str):
        self._add_bubble(text, is_user=False)

    def _scroll_to_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Sending logic ──────────────────────────────────────────────────────

    def _on_send_click(self):
        text = self.input_field.text().strip()
        if text:
            self._send(text)

    def _send(self, text: str):
        self.input_field.clear()
        self._add_user_message(text)
        self.conversation_history.append({"role": "user", "content": text})

        local_result = self._handle_local_command(text)
        if local_result is not None:
            self._add_bot_message(local_result)
            self.conversation_history.append({"role": "assistant", "content": local_result})
            return

        # Fall back to Gemini
        self._thinking_label = QLabel("⏳  Thinking…")
        self._thinking_label.setStyleSheet(
            "color: #8B949E; font-size: 12px; padding: 6px 14px; background: transparent;"
        )
        count = self.msg_layout.count()
        self.msg_layout.insertWidget(count - 1, self._thinking_label)
        self._scroll_to_bottom()

        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)

        self._worker = ChatWorker(list(self.conversation_history),
                                  self._build_system_prompt(), parent=self)
        self._worker.response_ready.connect(self._on_response)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _on_response(self, text: str):
        self._remove_thinking()
        self._add_bot_message(text)
        self.conversation_history.append({"role": "assistant", "content": text})
        self._re_enable_input()

    def _on_error(self, msg: str):
        self._remove_thinking()
        self._add_bot_message(f"⚠️ {msg}")
        self._re_enable_input()

    def _remove_thinking(self):
        if self._thinking_label:
            self._thinking_label.deleteLater()
            self._thinking_label = None

    def _re_enable_input(self):
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def _clear_chat(self):
        self.conversation_history.clear()
        while self.msg_layout.count() > 1:
            item = self.msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        self._add_bot_message("Chat cleared. How can I help you?")


# ---------------------------------------------------------------------------
# ChatbotPopup  — legacy QDialog wrapper (opens ChatbotWidget inside a dialog)
# ---------------------------------------------------------------------------

class ChatbotPopup(QDialog):
    """
    Kept for any code that still calls ChatbotPopup(...).exec_().
    Internally it just hosts a ChatbotWidget inside a dialog.
    """

    def __init__(self, db, attendance_manager, teacher_account_id,
                 current_user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Attendance AI")
        self.setMinimumSize(560, 680)
        self.setStyleSheet("QDialog { background-color: #0D1117; }")
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = ChatbotWidget(
            db=db,
            attendance_manager=attendance_manager,
            teacher_account_id=teacher_account_id,
            current_user=current_user,
            parent=self,
        )
        layout.addWidget(self.widget)