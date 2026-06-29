from calendar import month

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QDateEdit,
                             QComboBox, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QColor
import os
import subprocess
import platform
from datetime import datetime


class AttendanceReportsPage(QWidget):
    """Integrated reports page for the main application"""

    def __init__(self, db_instance, username, account_id=None, parent=None):
        super().__init__(parent)
        self.db = db_instance
        self.username = username
        self.account_id = account_id

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d3d8f;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #333333;
                gridline-color: #cccccc;
                selection-background-color: #a6d1ff;
                alternate-background-color: #e6f2ff;
                border: 1px solid #cccccc;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:hover {
                background-color: #d9eefb;
                color: #072045;
            }
            QTableWidget::item:selected {
                background-color: #a6d1ff;
                color: #072045;
            }
            QHeaderView::section {
                background-color: #1f4e78;
                color: #ffffff;
                padding: 5px;
                border: none;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: #333333;
            }
            QCalendarWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QCalendarWidget QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #0d47a1;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #ffffff;
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
            QCalendarWidget QToolButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #f5f5f5;
            }
            QCalendarWidget QMenu {
                background-color: #ffffff;
                color: #333333;
            }
        """)

        self.setup_ui()
        self.load_reports()

    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Title
        title = QLabel("Attendance Reports")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0d47a1; margin-bottom: 15px;")
        main_layout.addWidget(title)

        # ==================== FILTER SECTION ====================
        filter_frame = QtWidgets.QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(10)

        filter_layout.addWidget(QLabel("Date From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("Date To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)

        filter_layout.addWidget(QLabel("Department:"))
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("All")
        self.load_departments()
        filter_layout.addWidget(self.dept_combo)

        # ── Format selector (live — changes take effect immediately) ──
        filter_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Excel (.xlsx)", "PDF (.pdf)"])
        self.format_combo.setToolTip("Choose the output format for generated reports.")
        # Initialise from saved setting
        saved = QtCore.QSettings("AI_Attendance_System", "AppSettings").value(
            "report_format", "Excel (.xlsx)"
        )
        idx = self.format_combo.findText(saved)
        self.format_combo.setCurrentIndex(idx if idx >= 0 else 0)
        # Persist any change the user makes in the combo
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        filter_layout.addWidget(self.format_combo)
        # ─────────────────────────────────────────────────────────────

        filter_btn = QPushButton("Generate Report")
        filter_btn.clicked.connect(self.generate_filtered_report)
        filter_layout.addWidget(filter_btn)

        filter_layout.addStretch()
        main_layout.addWidget(filter_frame)

        # ==================== REPORTS TABLE ====================
        table_label = QLabel("Available Reports")
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0d47a1; margin-top: 10px;")
        main_layout.addWidget(table_label)

        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels(
            ["Report Name", "Date Modified", "Size (KB)", "View", "Download"]
        )
        self.reports_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.reports_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.reports_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.reports_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.reports_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.reports_table.horizontalHeader().setStretchLastSection(True)
        self.reports_table.horizontalHeader().setMinimumHeight(40)
        self.reports_table.verticalHeader().setDefaultSectionSize(35)
        self.reports_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.reports_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.reports_table.setAlternatingRowColors(True)
        self.reports_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        main_layout.addWidget(self.reports_table)

        # ==================== BUTTON SECTION ====================
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.load_reports)
        button_layout.addWidget(refresh_btn)

        send_email_btn = QPushButton("Send Student Report Email")
        send_email_btn.clicked.connect(self.send_student_report_emails)
        button_layout.addWidget(send_email_btn)

        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    # ──────────────────────────────────────────────────────
    #  FORMAT COMBO HANDLER
    # ──────────────────────────────────────────────────────
    def _on_format_changed(self, text: str):
        """Persist the selected format to QSettings immediately."""
        QtCore.QSettings("AI_Attendance_System", "AppSettings").setValue(
            "report_format", text
        )

    def load_departments(self):
        """Load departments from database"""
        if not self.db or not getattr(self.db, 'conn', None):
            print("Warning: cannot load departments, database not available")
            return
        try:
            departments = self.db.conn.execute(
                "SELECT DISTINCT dept FROM students WHERE dept IS NOT NULL"
            ).fetchall()
            for dept in departments:
                dept_name = dept[0] if isinstance(dept, tuple) else dept['dept']
                if dept_name:
                    self.dept_combo.addItem(dept_name)
        except Exception as e:
            print(f"Error loading departments: {e}")

    def load_reports(self):
        """Load existing reports from reports directory"""
        from utils.attendance_report_generator import AttendanceReportGenerator

        generator = AttendanceReportGenerator(self.username, account_id=self.account_id)
        reports = generator.get_all_reports()

        self.reports_table.setRowCount(len(reports))

        for row, report in enumerate(reports):
            name_item = QTableWidgetItem(report['filename'])
            name_item.setData(Qt.UserRole, report['filepath'])
            name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.reports_table.setItem(row, 0, name_item)

            modified_str = report['modified'].strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(modified_str)
            date_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.reports_table.setItem(row, 1, date_item)

            size_kb = report['size'] / 1024
            size_item = QTableWidgetItem(f"{size_kb:.2f}")
            size_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.reports_table.setItem(row, 2, size_item)

            view_btn = QPushButton("View")
            view_btn.setMaximumWidth(70)
            view_btn.setStyleSheet("""
                QPushButton { background-color: #4caf50; padding: 5px; }
                QPushButton:hover { background-color: #66bb6a; }
            """)
            view_btn.clicked.connect(lambda checked, r=row: self.view_report(r))
            view_container = QtWidgets.QWidget()
            view_layout = QHBoxLayout(view_container)
            view_layout.setContentsMargins(0, 0, 0, 0)
            view_layout.setAlignment(Qt.AlignCenter)
            view_layout.addWidget(view_btn)
            self.reports_table.setCellWidget(row, 3, view_container)

            download_btn = QPushButton("Download")
            download_btn.setMaximumWidth(90)
            download_btn.setStyleSheet("""
                QPushButton { background-color: #2196f3; padding: 5px; }
                QPushButton:hover { background-color: #42a5f5; }
            """)
            download_btn.clicked.connect(lambda checked, r=row: self.download_report(r))
            download_container = QtWidgets.QWidget()
            download_layout = QHBoxLayout(download_container)
            download_layout.setContentsMargins(0, 0, 0, 0)
            download_layout.setAlignment(Qt.AlignCenter)
            download_layout.addWidget(download_btn)
            self.reports_table.setCellWidget(row, 4, download_container)

    # ──────────────────────────────────────────────────────
    #  GENERATE REPORT  (respects Settings format)
    # ──────────────────────────────────────────────────────
    def generate_filtered_report(self):
        """
        Generate a report based on filters.

        The output format is controlled by Settings → Report format:
          • Excel (.xlsx)  →  only an Excel file is produced  (default)
          • PDF (.pdf)     →  only a PDF file is produced
        """
        from utils.attendance_report_generator import AttendanceReportGenerator

        try:
            date_from  = self.date_from.date().toPyDate()
            date_to    = self.date_to.date().toPyDate()
            department = self.dept_combo.currentText()

            if department == "All":
                department = None

            attendance_data = self.get_attendance_for_date_range(date_from, date_to, department)

            if not attendance_data:
                QMessageBox.warning(
                    self, "No Data",
                    "No attendance records found for the selected date range."
                )
                return

            fmt = "pdf" if "pdf" in self.format_combo.currentText().lower() else "excel"
            is_single_day = (date_from == date_to)

            generator = AttendanceReportGenerator(
                self.username,
                account_id=self.account_id
            )

            if fmt == "pdf":
                # ── PDF only ──────────────────────────────────────────
                if is_single_day:
                    out_file = generator.generate_daily_pdf_report(
                        attendance_data,
                        date_from.strftime("%Y-%m-%d")
                    )
                else:
                    out_file = generator.generate_monthly_pdf_report(
                        attendance_data,
                        date_from.year,
                        date_from.month,
                        department
                    )
                label = "PDF report"
            else:
                # ── Excel only (default) ──────────────────────────────
                if is_single_day:
                    out_file = generator.generate_daily_report(
                        attendance_data,
                        date_from.strftime("%Y-%m-%d"),
                        department
                    )
                else:
                    out_file = generator.generate_monthly_report(
                        attendance_data,
                        date_from.year,
                        date_from.month,
                        department
                    )
                label = "Excel report"

            QMessageBox.information(
                self, "Success",
                f"{label} generated successfully!\n\n{out_file}"
            )
            self.load_reports()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def get_attendance_for_date_range(self, date_from, date_to, department=None):
        """Fetch attendance records for a date range"""
        if not self.db or not getattr(self.db, 'conn', None):
            print("Error fetching attendance data: database connection missing")
            return []
        try:
            query = """
                SELECT
                    COALESCE(a.id, 0) as id,
                    COALESCE(s.name, 'Unknown') as name,
                    COALESCE(s.roll, 'N/A') as roll,
                    COALESCE(s.dept, 'N/A') as dept,
                    COALESCE(s.year, 'N/A') as year,
                    COALESCE(s.email, '') as email,
                    a.date as date,
                    a.time as time,
                    a.status as status
                FROM attendance a
                LEFT JOIN students s ON a.student_id = s.id
                WHERE a.date >= ? AND a.date <= ?
            """
            params = [date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")]

            if self.account_id is not None:
                query += " AND s.teacher_account_id = ?"
                params.append(self.account_id)

            if department and department != "All":
                query += " AND s.dept = ?"
                params.append(department)

            query += " ORDER BY a.date DESC, COALESCE(s.name, 'Unknown') ASC"

            rows = self.db.conn.execute(query, params).fetchall()

            data = []
            for row in rows:
                data.append({
                    'id':     row[0] if isinstance(row, tuple) else row['id'],
                    'name':   row[1] if isinstance(row, tuple) else row['name'],
                    'roll':   row[2] if isinstance(row, tuple) else row['roll'],
                    'dept':   row[3] if isinstance(row, tuple) else row['dept'],
                    'year':   row[4] if isinstance(row, tuple) else row['year'],
                    'email':  row[5] if isinstance(row, tuple) else row['email'],
                    'date':   row[6] if isinstance(row, tuple) else row['date'],
                    'time':   row[7] if isinstance(row, tuple) else row['time'],
                    'status': row[8] if isinstance(row, tuple) else row['status'],
                })
            return data
        except Exception as e:
            print(f"Error fetching attendance data: {e}")
            return []

    def view_report(self, row):
        """Open and view a report"""
        try:
            filepath = self.reports_table.item(row, 0).data(Qt.UserRole)

            if not os.path.exists(filepath):
                QMessageBox.warning(self, "Error", "Report file not found.")
                return

            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', filepath])
            else:
                subprocess.Popen(['xdg-open', filepath])

            QMessageBox.information(self, "Success", "Report opened in default application.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open report: {str(e)}")

    def download_report(self, row):
        """Download/Save a report to a custom location"""
        try:
            filepath = self.reports_table.item(row, 0).data(Qt.UserRole)
            filename = os.path.basename(filepath)

            if not os.path.exists(filepath):
                QMessageBox.warning(self, "Error", "Report file not found.")
                return

            if filename.lower().endswith(".pdf"):
                file_filter = "PDF Files (*.pdf);;All Files (*.*)"
            else:
                file_filter = "Excel Files (*.xlsx);;All Files (*.*)"

            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", filename, file_filter
            )

            if save_path:
                import shutil
                shutil.copy2(filepath, save_path)
                QMessageBox.information(self, "Success", f"Report saved to:\n{save_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download report: {str(e)}")

    def send_student_report_emails(self):
        """Send individual monthly attendance reports to students via email"""
        from utils.attendance_report_generator import AttendanceReportGenerator
        from utils.email_sender import send_attendance_report_email

        try:
            date_from  = self.date_from.date().toPyDate()
            date_to    = self.date_to.date().toPyDate()
            department = self.dept_combo.currentText()

            if department == "All":
                department = None

            attendance_data = self.get_attendance_for_date_range(date_from, date_to, department)

            if not attendance_data:
                QMessageBox.warning(
                    self, "No Data",
                    "No attendance records found for the selected date range."
                )
                return

            students_data = {}
            for record in attendance_data:
                student_key = (record['name'], record['roll'], record['email'])
                if student_key not in students_data:
                    students_data[student_key] = {'present': 0, 'absent': 0}

                if record['status'] and record['status'].lower() in ['present', 'p']:
                    students_data[student_key]['present'] += 1
                elif record['status'] and record['status'].lower() in ['absent', 'a']:
                    students_data[student_key]['absent'] += 1

            generator = AttendanceReportGenerator(self.username, account_id=self.account_id)

            if date_from == date_to:
                date_range_str = date_from.strftime("%d %B %Y")
            else:
                date_range_str = (
                    f"{date_from.strftime('%d %B %Y')} to {date_to.strftime('%d %B %Y')}"
                )

            email_count  = 0
            failed_count = 0
            error_details = []

            for (student_name, student_roll, student_email), attendance_counts in students_data.items():
                if not student_email or '@' not in student_email:
                    print(f"⚠️ Skipping {student_name} ({student_roll}): Invalid email")
                    failed_count += 1
                    continue

                student_attendance = [
                    r for r in attendance_data
                    if r['name'] == student_name and r['roll'] == student_roll
                ]

                student_report_filepath = None
                try:
                    student_report_filepath = generator.generate_monthly_report(
                        student_attendance,
                        date_from.year,
                        date_from.month,
                        department,
                        student_name=student_name,
                        save_to_reports_dir=False
                    )

                    sent_result = send_attendance_report_email(
                        student_name=student_name,
                        student_email=student_email,
                        total_present=attendance_counts['present'],
                        total_absent=attendance_counts['absent'],
                        month_year=date_range_str,
                        report_filepath=student_report_filepath
                    )

                    try:
                        success, err_msg = sent_result
                    except Exception:
                        success = bool(sent_result)
                        err_msg = ""

                    if success:
                        email_count += 1
                    else:
                        failed_count += 1
                        error_details.append((student_name, student_email, err_msg))

                except Exception as e:
                    print(f"❌ Error sending report to {student_name}: {e}")
                    failed_count += 1
                finally:
                    try:
                        if student_report_filepath and os.path.exists(student_report_filepath):
                            os.remove(student_report_filepath)
                    except Exception:
                        pass

            summary_lines = [
                "Report Emails Summary:",
                f"✅ Successfully sent: {email_count} emails",
                f"❌ Failed: {failed_count} emails",
                f"📊 Period: {date_range_str}",
                ""
            ]

            if error_details:
                summary_lines.append("Errors (student - email - error):")
                for name, mail, err in error_details[:10]:
                    summary_lines.append(f"- {name} - {mail} - {err}")
                if len(error_details) > 10:
                    summary_lines.append(f"...and {len(error_details) - 10} more errors")

            QMessageBox.information(self, "Emails Sent", "\n".join(summary_lines))
            self.load_reports()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send report emails: {str(e)}")