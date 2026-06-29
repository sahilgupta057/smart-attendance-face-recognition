from utils.database import UserDatabase   # import your DB file
from datetime import datetime


class AttendanceManager:

    def __init__(self, username=None):
        """
        username = folder name for database
        Example: admin, teacher1, etc.
        """

        # If you pass username later, store it
        self.username = username

        # Database connection (created when needed)
        self.db = None


    # ---------------- CONNECT DB ---------------- #

    def connect(self, username=None):

        if username:
            self.username = username

        if not self.username:
            raise ValueError("Username required for database")

        if not self.db:
            self.db = UserDatabase(self.username)


    # ---------------- MARK ATTENDANCE ---------------- #

    def mark_attendance(self, roll, account_id, status="Present"):
        # convenience wrapper used by face-recognition thread etc.
        if not self.db:
            self.connect()

        if status == "Present":
            # make sure attendance rows exist for today before updating
            try:
                self.db.initialize_today_attendance(account_id)
            except Exception:
                # ignore if initialization fails for some reason
                pass
            return self.db.mark_present_by_account(roll, account_id)

        return False



    # ---------------- FINALIZE ---------------- #

    def finalize(self, account_id):
        """
        Mark unmarked students as Absent
        """

        if not self.db:
            self.connect()

        self.db.finalize_attendance(account_id)


    # ---------------- REPORT ---------------- #

    def get_today_sheet(self, account_id):

        if not self.db:
            self.connect()

        return self.db.get_today_attendance_sheet(account_id)


    def get_full_report(self, account_id):

        if not self.db:
            self.connect()

        return self.db.get_attendance_records_by_account(account_id)
    

    def get_attendance_by_account(self, account_id):
        """Return all attendance records for the given teacher account"""
        if not self.db:
            self.connect()
        return self.get_full_report(account_id)



    # ---------------- CLOSE ---------------- #

    def close(self):

        if self.db:
            self.db.close()
            self.db = None
