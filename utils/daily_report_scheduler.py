import threading
import schedule
import time
from datetime import datetime, timedelta
from utils.attendance_report_generator import AttendanceReportGenerator
from utils.database import UserDatabase
from utils.email_sender import send_attendance_report_email
import calendar
import os


class DailyReportScheduler:
    """Scheduler for automatic daily attendance report generation"""

    def __init__(self, username, account_id=None, time_str="23:59", enabled=True):
        """
        username: Teacher/admin username
        account_id: optional teacher_account_id to filter/generate appropriate reports
        time_str: Time to generate reports in HH:MM format (24-hour)
        enabled: Whether to enable auto-generation
        """
        self.username = username
        self.account_id = account_id
        self.time_str = time_str
        self.enabled = enabled
        self.scheduler_thread = None
        self.running = False
        self.db = None
        self._last_monthly_sent = None

    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            return
        
        self.running = True
        self.db = UserDatabase(self.username)
        # optional account filter stored for queries
        
        # Schedule the daily task
        schedule.every().day.at(self.time_str).do(self.generate_daily_reports)
        # Schedule a daily check for monthly sending (runs daily at same time)
        schedule.every().day.at(self.time_str).do(self.generate_monthly_student_emails_if_due)
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print(f"Attendance report scheduler started for user: {self.username}")

    def _run_scheduler(self):
        """Run the scheduler (called in background thread)"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)

    def generate_daily_reports(self):
        """Generate attendance reports for today"""
        if not self.enabled or not self.running:
            return
        
        try:
            print(f"[{datetime.now()}] Generating daily reports for {self.username}...")
            
            generator = AttendanceReportGenerator(self.username, account_id=self.account_id)
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get today's attendance data filtered to this teacher account
            query = """
                SELECT 
                    COALESCE(a.id, 0) as id,
                    COALESCE(s.name, 'Unknown') as name,
                    COALESCE(s.roll, 'N/A') as roll,
                    COALESCE(s.dept, 'N/A') as dept,
                    COALESCE(s.year, 'N/A') as year,
                    a.date as date,
                    a.time as time,
                    a.status as status
                FROM attendance a
                LEFT JOIN students s ON a.student_id = s.id
                WHERE a.date = ?
            """
            params = [today]
            if self.account_id is not None:
                query += "\n AND s.teacher_account_id = ?"
                params.append(self.account_id)
            query += "\n ORDER BY COALESCE(s.name, 'Unknown') ASC"
            rows = self.db.conn.execute(query, tuple(params)).fetchall()
            
            attendance_data = []
            for row in rows:
                attendance_data.append({
                    'id': row[0] if isinstance(row, tuple) else row['id'],
                    'name': row[1] if isinstance(row, tuple) else row['name'],
                    'roll': row[2] if isinstance(row, tuple) else row['roll'],
                    'dept': row[3] if isinstance(row, tuple) else row['dept'],
                    'year': row[4] if isinstance(row, tuple) else row['year'],
                    'date': row[5] if isinstance(row, tuple) else row['date'],
                    'time': row[6] if isinstance(row, tuple) else row['time'],
                    'status': row[7] if isinstance(row, tuple) else row['status'],
                })
            
            if attendance_data:
                filepath = generator.generate_daily_report(attendance_data, today)
                print(f"✓ Daily report generated: {filepath}")
            else:
                print(f"No attendance records found for {today}")
            
        except Exception as e:
            print(f"Error generating daily reports: {e}")

    def generate_weekly_summary(self):
        """Generate a weekly summary report"""
        if not self.enabled:
            return
        
        try:
            print(f"[{datetime.now()}] Generating weekly summary for {self.username}...")
            
            generator = AttendanceReportGenerator(self.username, account_id=self.account_id)
            
            # Get data for the past 7 days
            today = datetime.now().date()
            week_start = today - timedelta(days=7)
            
            query = """
                SELECT 
                    COALESCE(a.id, 0) as id,
                    COALESCE(s.name, 'Unknown') as name,
                    COALESCE(s.roll, 'N/A') as roll,
                    COALESCE(s.dept, 'N/A') as dept,
                    COALESCE(s.year, 'N/A') as year,
                    a.date as date,
                    a.time as time,
                    a.status as status
                FROM attendance a
                LEFT JOIN students s ON a.student_id = s.id
                WHERE a.date >= ? AND a.date <= ?
            """
            params = [week_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
            if self.account_id is not None:
                query += "\n AND s.teacher_account_id = ?"
                params.append(self.account_id)
            query += "\n ORDER BY a.date DESC, COALESCE(s.name, 'Unknown') ASC"
            rows = self.db.conn.execute(
                query, 
                tuple(params)
            ).fetchall()
            
            attendance_data = []
            for row in rows:
                attendance_data.append({
                    'id': row[0] if isinstance(row, tuple) else row['id'],
                    'name': row[1] if isinstance(row, tuple) else row['name'],
                    'roll': row[2] if isinstance(row, tuple) else row['roll'],
                    'dept': row[3] if isinstance(row, tuple) else row['dept'],
                    'year': row[4] if isinstance(row, tuple) else row['year'],
                    'date': row[5] if isinstance(row, tuple) else row['date'],
                    'time': row[6] if isinstance(row, tuple) else row['time'],
                    'status': row[7] if isinstance(row, tuple) else row['status'],
                })
            
            if attendance_data:
                filepath = generator.generate_monthly_report(
                    attendance_data,
                    today.year,
                    today.month
                )
                print(f"✓ Weekly summary generated: {filepath}")
            
        except Exception as e:
            print(f"Error generating weekly summary: {e}")

    def generate_monthly_student_emails_if_due(self):
        """Check if monthly email should be sent (run on 1st of month)."""
        if not self.enabled or not self.running:
            return

        try:
            now = datetime.now()
            # send on 1st day for previous month
            if now.day == 1:
                year = now.year
                month = now.month - 1
                if month == 0:
                    month = 12
                    year -= 1

                # avoid sending multiple times in same month
                key = (year, month)
                if self._last_monthly_sent == key:
                    return

                print(f"[{datetime.now()}] Triggering monthly student emails for {month}/{year}...")
                self.generate_monthly_student_emails(year, month)
                self._last_monthly_sent = key
        except Exception as e:
            print(f"Error in monthly email check: {e}")

    def generate_monthly_student_emails(self, year=None, month=None, department=None):
        """Generate individual monthly reports and email them to students.

        If year/month omitted, uses previous month.
        """
        if not self.enabled or not self.running:
            return

        try:
            now = datetime.now()
            if year is None or month is None:
                # default to previous month
                year = now.year
                month = now.month - 1
                if month == 0:
                    month = 12
                    year -= 1

            # compute date range
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

            print(f"[{datetime.now()}] Generating monthly student emails for {month}/{year} ({first_day} to {last_day})")

            # fetch attendance for range
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
            params = [first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')]
            if self.account_id is not None:
                query += " AND s.teacher_account_id = ?"
                params.append(self.account_id)
            if department:
                query += " AND s.dept = ?"
                params.append(department)

            rows = self.db.conn.execute(query, params).fetchall()

            attendance_data = []
            for row in rows:
                attendance_data.append({
                    'id': row[0] if isinstance(row, tuple) else row['id'],
                    'name': row[1] if isinstance(row, tuple) else row['name'],
                    'roll': row[2] if isinstance(row, tuple) else row['roll'],
                    'dept': row[3] if isinstance(row, tuple) else row['dept'],
                    'year': row[4] if isinstance(row, tuple) else row['year'],
                    'email': row[5] if isinstance(row, tuple) else row['email'],
                    'date': row[6] if isinstance(row, tuple) else row['date'],
                    'time': row[7] if isinstance(row, tuple) else row['time'],
                    'status': row[8] if isinstance(row, tuple) else row['status'],
                })

            if not attendance_data:
                print("No attendance records for the month; no emails sent.")
                return

            # group by student
            students = {}
            for rec in attendance_data:
                key = (rec['name'], rec['roll'], rec.get('email', ''))
                if key not in students:
                    students[key] = {'present': 0, 'absent': 0, 'records': []}
                students[key]['records'].append(rec)
                status = rec.get('status', '')
                if status and status.lower() in ['present', 'p']:
                    students[key]['present'] += 1
                else:
                    students[key]['absent'] += 1

            generator = AttendanceReportGenerator(self.username, account_id=self.account_id)
            sent = 0
            failed = 0
            for (name, roll, email), info in students.items():
                if not email or '@' not in email:
                    print(f"Skipping {name} ({roll}) - no valid email")
                    failed += 1
                    continue

                # generate student report (uses monthly generator but filtered by student)
                try:
                    # Generate report into a temporary file so it won't appear in available reports
                    filepath = generator.generate_monthly_report(
                        info['records'],
                        year,
                        month,
                        department,
                        student_name=name,
                        save_to_reports_dir=False
                    )
                    try:
                        success, err = send_attendance_report_email(
                            student_name=name,
                            student_email=email,
                            total_present=info['present'],
                            total_absent=info['absent'],
                            month_year=f"{first_day.strftime('%B %Y')}",
                            report_filepath=filepath
                        )
                        if success:
                            sent += 1
                        else:
                            failed += 1
                            print(f"Failed to send to {email}: {err}")
                    finally:
                        # remove temporary file
                        try:
                            if os.path.exists(filepath):
                                os.remove(filepath)
                        except Exception:
                            pass
                except Exception as e:
                    failed += 1
                    print(f"Error preparing/sending for {name}: {e}")

            print(f"Monthly student emails - Sent: {sent}, Failed: {failed}")

        except Exception as e:
            print(f"Error generating monthly student emails: {e}")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        print(f"Attendance report scheduler stopped for user: {self.username}")
        
        if self.db:
            self.db.close()

    def set_time(self, time_str):
        """Change the scheduled time (HH:MM format)"""
        self.time_str = time_str
        schedule.clear()
        schedule.every().day.at(time_str).do(self.generate_daily_reports)
        print(f"Report generation time updated to: {time_str}")


# Global scheduler instance
_scheduler_instance = None


def initialize_scheduler(username, account_id=None, time_str="23:59"):
    """Initialize and start the global scheduler

    account_id: optional teacher_account_id to scope report generation
    """
    global _scheduler_instance
    
    if _scheduler_instance is not None:
        _scheduler_instance.stop()
    
    # allow passing account_id for proper scoping
    _scheduler_instance = DailyReportScheduler(username, account_id=account_id, time_str=time_str, enabled=True)
    _scheduler_instance.start()
    return _scheduler_instance


def get_scheduler():
    """Get the current scheduler instance"""
    return _scheduler_instance


def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None
