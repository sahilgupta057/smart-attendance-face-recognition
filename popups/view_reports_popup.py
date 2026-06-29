from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QDateEdit, 
                             QComboBox, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QColor
from utils.open_popup_sound import PopupSound
import os
import subprocess
import platform
from datetime import datetime


class ViewReportsPopup(QDialog):
    """Popup for viewing and downloading attendance reports"""

    def __init__(self, db_instance, username, account_id=None, parent=None):
        super().__init__(parent)
        self.db = db_instance
        self.username = username
        self.account_id = account_id
        self.popup_sound = PopupSound()
        
        self.setWindowTitle("Attendance Reports")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #eee;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d3d8f;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #eee;
                gridline-color: #444;
                selection-background-color: #0d47a1;
            }
            QHeaderView::section {
                background-color: #1f4e78;
                color: #eee;
                padding: 5px;
                border: none;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #2d2d2d;
                color: #eee;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: #eee;
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
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0d47a1;")
        main_layout.addWidget(title)

        # Filter Section
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Date From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("Date To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        
        filter_layout.addWidget(QLabel("Department:"))
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("All")
        self.load_departments()
        filter_layout.addWidget(self.dept_combo)
        
        filter_btn = QPushButton("Filter")
        filter_btn.clicked.connect(self.generate_filtered_report)
        filter_layout.addWidget(filter_btn)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # Reports Table
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels(
            ["Report Name", "Date Modified", "Size (KB)", "View", "Download"]
        )
        self.reports_table.horizontalHeader().setStretchLastSection(False)
        self.reports_table.setColumnWidth(0, 300)
        self.reports_table.setColumnWidth(1, 150)
        self.reports_table.setColumnWidth(2, 100)
        self.reports_table.setColumnWidth(3, 100)
        self.reports_table.setColumnWidth(4, 100)
        self.reports_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        main_layout.addWidget(self.reports_table)

        # Button Section
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_reports)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)

    def load_departments(self):
        """Load departments from database"""
        try:
            departments = self.db.conn.execute("SELECT DISTINCT dept FROM students WHERE dept IS NOT NULL").fetchall()
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
            # Report name
            name_item = QTableWidgetItem(report['filename'])
            name_item.setData(Qt.UserRole, report['filepath'])
            self.reports_table.setItem(row, 0, name_item)
            
            # Modified date
            modified_str = report['modified'].strftime("%Y-%m-%d %H:%M")
            self.reports_table.setItem(row, 1, QTableWidgetItem(modified_str))
            
            # Size
            size_kb = report['size'] / 1024
            self.reports_table.setItem(row, 2, QTableWidgetItem(f"{size_kb:.2f}"))
            
            # View button
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, r=row: self.view_report(r))
            self.reports_table.setCellWidget(row, 3, view_btn)
            
            # Download button
            download_btn = QPushButton("Download")
            download_btn.clicked.connect(lambda checked, r=row: self.download_report(r))
            self.reports_table.setCellWidget(row, 4, download_btn)

    def generate_filtered_report(self):
        """Generate a new report based on filters"""
        from utils.attendance_report_generator import AttendanceReportGenerator
        from datetime import datetime, timedelta
        
        try:
            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()
            department = self.dept_combo.currentText()
            
            if department == "All":
                department = None
            
            # Fetch attendance data for the date range
            attendance_data = self.get_attendance_for_date_range(date_from, date_to, department)
            
            if not attendance_data:
                QMessageBox.warning(self, "No Data", "No attendance records found for the selected date range.")
                return
            
            generator = AttendanceReportGenerator(self.username, account_id=self.account_id)
            
            # If single day, use daily report format
            if date_from == date_to:
                filepath = generator.generate_daily_report(
                    attendance_data,
                    date_from.strftime("%Y-%m-%d"),
                    department
                )
            else:
                # For multiple days, generate monthly-style report
                filepath = generator.generate_monthly_report(
                    attendance_data,
                    date_from.year,
                    date_from.month,
                    department
                )
            
            QMessageBox.information(self, "Success", f"Report generated successfully!\n\n{filepath}")
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
                SELECT id, name, roll, dept, year, date, time, status 
                FROM attendance 
                WHERE date >= ? AND date <= ?
            """
            params = [date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")]

            if self.account_id is not None:
                query += " AND roll IN (SELECT roll FROM students WHERE teacher_account_id = ?)"
                params.append(self.account_id)
            
            if department and department != "All":
                query += " AND dept = ?"
                params.append(department)
            
            query += " ORDER BY date DESC, name ASC"
            
            rows = self.db.conn.execute(query, params).fetchall()
            
            data = []
            for row in rows:
                data.append({
                    'id': row[0] if isinstance(row, tuple) else row['id'],
                    'name': row[1] if isinstance(row, tuple) else row['name'],
                    'roll': row[2] if isinstance(row, tuple) else row['roll'],
                    'dept': row[3] if isinstance(row, tuple) else row['dept'],
                    'year': row[4] if isinstance(row, tuple) else row['year'],
                    'date': row[5] if isinstance(row, tuple) else row['date'],
                    'time': row[6] if isinstance(row, tuple) else row['time'],
                    'status': row[7] if isinstance(row, tuple) else row['status'],
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
            
            # Open with default application
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', filepath])
            else:  # Linux
                subprocess.Popen(['xdg-open', filepath])
                
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
            
            # Ask user where to save
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Report",
                filename,
                "Excel Files (*.xlsx);;All Files (*.*)"
            )
            
            if save_path:
                import shutil
                shutil.copy2(filepath, save_path)
                QMessageBox.information(self, "Success", f"Report saved to:\n{save_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download report: {str(e)}")

    def showEvent(self, event):
        """Play sound when popup opens"""
        super().showEvent(event)
        self.popup_sound.play_openPopup()
