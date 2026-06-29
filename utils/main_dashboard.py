import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem
from utils.database import UserDatabase  # adjust import according to your structure


class MainDashboard(QMainWindow):
    def __init__(self, username, user_db=None):
        super().__init__()
        self.username = username
        self.db = user_db or UserDatabase(username)

        self.setWindowTitle(f"Dashboard - {username}")
        self.resize(900, 600)

        # Table will be created only when setup_table() is called
        self.table = None

    # ---------------- SETUP TABLE ---------------- #
    def setup_table(self):
        """Create table and load students. Call only when dashboard opens."""
        if self.table is None:
            self.table = QTableWidget()
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(
                ["Name", "Roll", "Department", "Year", "Image", "Email"]
            )
            self.setCentralWidget(self.table)
            self.load_students()

    # ---------------- LOAD STUDENTS ---------------- #
    def load_students(self):
        self.table.setRowCount(0)
        students = self.db.get_all_students()
        for row_num, student in enumerate(students):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(student["name"]))
            self.table.setItem(row_num, 1, QTableWidgetItem(student["roll"]))
            self.table.setItem(row_num, 2, QTableWidgetItem(student["dept"] or ""))
            self.table.setItem(row_num, 3, QTableWidgetItem(student["year"] or ""))
            self.table.setItem(
                row_num,
                4,
                QTableWidgetItem(os.path.basename(student["face_image"]))
                if student["face_image"]
                else QTableWidgetItem(""),
            )
            self.table.setItem(row_num, 5, QTableWidgetItem(student["email"] or ""))

    # ---------------- ADD STUDENT ---------------- #
    def add_student(self, name, roll, dept, year, image_path, email):
        success = self.db.add_student(name, roll, dept, year, image_path, email)
        if success:
            self.load_students()
            QMessageBox.information(self, "Success", f"Student {name} added successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Roll number {roll} already exists!")

    # ---------------- DELETE STUDENT ---------------- #
    def delete_student_from_db(self, roll):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete student {roll}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.delete_student(roll)
            self.load_students()

    # ---------------- CLEAR ALL STUDENTS ---------------- #
    def clear_all_students(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear All",
            "Are you sure you want to delete ALL students?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db.clear_all_students()
            self.load_students()
            QMessageBox.information(self, "Cleared", "All students have been deleted.")
