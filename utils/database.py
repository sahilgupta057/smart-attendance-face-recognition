import sqlite3
import os
from datetime import datetime

class UserDatabase:
    def __init__(self, username):
        self.db_path = f"data/{username}/students.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")

        self.create_tables()

    # ---------------- CREATE TABLES ---------------- #
    def create_tables(self):
        with self.conn:
            # Teachers
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            """)

            # Departments
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Subjects
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Teacher Accounts
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS teacher_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER,
                    department_id INTEGER,
                    subject_id INTEGER,
                    UNIQUE (teacher_id, department_id, subject_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                    FOREIGN KEY (department_id) REFERENCES departments(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            """)

            # Students
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL,
                dept TEXT,
                year TEXT,
                face_image TEXT,
                email TEXT,
                teacher_account_id INTEGER,
                created_at TEXT,
                UNIQUE (roll, teacher_account_id),
                FOREIGN KEY (teacher_account_id) REFERENCES teacher_accounts(id) ON DELETE CASCADE
            )

            """)

            # Attendance
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    name TEXT,
                    roll TEXT,
                    dept TEXT,
                    year TEXT,
                    date TEXT,
                    time TEXT,
                    status TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            """)

            self.conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique
                ON attendance(student_id, date)
            """)

            # Backwards compatibility: add 'dept' column if an older DB lacks it
            cur = self.conn.execute("PRAGMA table_info(students)").fetchall()
            cols = [r[1] if not isinstance(r, dict) else r["name"] for r in cur]
            # r might be sqlite3.Row or tuple depending on environment; handle both
            if "dept" not in cols:
                try:
                    self.conn.execute("ALTER TABLE students ADD COLUMN dept TEXT")
                except Exception:
                    # If it fails (e.g., locked db), we ignore; table will still work without dept column
                    pass

    # ---------------- MASTER INSERTS ---------------- #
    def add_teacher(self, name, email):
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO teachers (name, email) VALUES (?, ?)",
                (name, email)
            )

    def get_teacher_id_by_email(self, email):
        """Return teacher id for given email, or None if not found."""
        row = self.conn.execute("SELECT id FROM teachers WHERE email = ?", (email,)).fetchone()
        return row["id"] if row else None

    def add_department(self, name):
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO departments (name) VALUES (?)",
                (name,)
            )

    def add_subject(self, name):
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO subjects (name) VALUES (?)",
                (name,)
            )

    # ---------------- TEACHER ACCOUNT ---------------- #
    def create_teacher_account(self, teacher_id, department_id, subject_id):
        with self.conn:
            self.conn.execute("""
                INSERT OR IGNORE INTO teacher_accounts
                (teacher_id, department_id, subject_id)
                VALUES (?, ?, ?)
            """, (teacher_id, department_id, subject_id))

    def get_teacher_accounts(self, teacher_id):
        return self.conn.execute("""
            SELECT ta.id,
                   d.name AS department,
                   s.name AS subject
            FROM teacher_accounts ta
            JOIN departments d ON ta.department_id = d.id
            JOIN subjects s ON ta.subject_id = s.id
            WHERE ta.teacher_id = ?
        """, (teacher_id,)).fetchall()

    # ---------------- STUDENTS ---------------- #
    def add_student(self, name, roll, dept=None, year=None, face_image=None, email=None, teacher_account_id=None):
        """Add a student. Returns the inserted row id on success, False on duplicate."""
        try:
            with self.conn:
                cur = self.conn.execute("""
                    INSERT INTO students
                    (name, roll, dept, year, face_image, email, teacher_account_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, roll, dept, year, face_image, email,
                    teacher_account_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                return cur.lastrowid
        except sqlite3.IntegrityError:
            # Roll number already exists for this teacher_account
            return False

    def get_students_by_account(self, teacher_account_id):
        rows = self.conn.execute("""
            SELECT * FROM students
            WHERE teacher_account_id = ?
            ORDER BY name
        """, (teacher_account_id,)).fetchall()
        return [dict(row) for row in rows]

    def get_student_by_roll(self, roll):
        row = self.conn.execute(
            "SELECT * FROM students WHERE roll = ?",
            (roll,)
        ).fetchone()
        return dict(row) if row else None

    def student_exists(self, roll, teacher_account_id):
        row = self.conn.execute(
            """
            SELECT 1 FROM students
            WHERE roll = ? AND teacher_account_id = ?
            """,
            (roll, teacher_account_id)
        ).fetchone()
        return row is not None

    # ---------------- DEPARTMENTS / SUBJECTS HELPERS ---------------- #
    def get_department_id(self, name):
        row = self.conn.execute("SELECT id FROM departments WHERE name = ?", (name,)).fetchone()
        return row["id"] if row else None

    def get_subject_id(self, name):
        row = self.conn.execute("SELECT id FROM subjects WHERE name = ?", (name,)).fetchone()
        return row["id"] if row else None

    def get_or_create_department(self, name):
        if not name:
            return None
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (name,))
        return self.get_department_id(name)

    def get_or_create_subject(self, name):
        if not name:
            return None
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (name,))
        return self.get_subject_id(name)

    def get_or_create_teacher_account(self, teacher_id, department_name, subject_name):
        """Ensure department & subject rows exist, then create or fetch teacher_account and return its id."""
        dept_id = self.get_or_create_department(department_name)
        subj_id = self.get_or_create_subject(subject_name)
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO teacher_accounts (teacher_id, department_id, subject_id) VALUES (?, ?, ?)",
                (teacher_id, dept_id, subj_id)
            )
        row = self.conn.execute(
            "SELECT id FROM teacher_accounts WHERE teacher_id=? AND department_id=? AND subject_id=?",
            (teacher_id, dept_id, subj_id)
        ).fetchone()
        return row["id"] if row else None

    # ---------------- ADDITIONAL STUDENT HELPERS ---------------- #
    def get_all_students(self):
        rows = self.conn.execute("SELECT * FROM students ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def delete_student(self, roll):
        """Delete a student by roll number and all related attendance records."""
        # First get the student_id to ensure we're deleting the right records
        student = self.get_student_by_roll(roll)
        if not student:
            return False
        
        student_id = student["id"]
        
        try:
            with self.conn:
                # Delete attendance records first (though CASCADE should handle this)
                self.conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
                # Then delete the student
                self.conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
            return True
        except sqlite3.IntegrityError as e:
            print(f"Foreign key constraint error: {e}")
            return False

    def get_student_by_name(self, name):
        row = self.conn.execute("SELECT * FROM students WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        return dict(row) if row else None

    def get_student_email_by_roll(self, roll):
        row = self.conn.execute("SELECT email FROM students WHERE roll = ?", (roll,)).fetchone()
        return row["email"] if row and row["email"] else None


    def clear_students_by_account(self, teacher_account_id):
        with self.conn:
            self.conn.execute(
                "DELETE FROM students WHERE teacher_account_id = ?",
                (teacher_account_id,)
            )

    # ---------------- INITIALIZE ATTENDANCE ---------------- #
    def initialize_today_attendance(self, teacher_account_id):
        """
        Add all students for today into attendance table.
        Only stores student_id, date, time, status (other data is joined from students table).
        """
        today = datetime.now().strftime("%Y-%m-%d")
        students = self.get_students_by_account(teacher_account_id)

        for s in students:
            try:
                with self.conn:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO attendance
                        (student_id, date, time, status)
                        VALUES (?, ?, ?, ?)
                    """, (
                        s["id"],
                        today,
                        datetime.now().strftime("%H:%M:%S"),
                        "Not Marked"  # initial status
                    ))
            except sqlite3.IntegrityError:
                pass  # row already exists


    # ---------------- ATTENDANCE ---------------- #
    def mark_present(self, roll):
        student = self.get_student_by_roll(roll)

        if not student:
            return False

        now = datetime.now()

        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO attendance
                (student_id, date, time, status)
                VALUES (?, ?, ?, ?)
            """, (
                student["id"],
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                "Present"
            ))

        return True
    
    
    def mark_present_by_account(self, roll, teacher_account_id):
        student = self.conn.execute("""
            SELECT id FROM students
            WHERE roll = ? AND teacher_account_id = ?
        """, (roll, teacher_account_id)).fetchone()

        if not student:
            return False

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        with self.conn:
            cur = self.conn.execute("""
                UPDATE attendance
                SET status = ?, time = ?
                WHERE student_id = ? AND date = ?
            """, ("Present", time_str, student["id"], today))

            # if update didn't hit anything (no row for today), insert it
            if cur.rowcount == 0:
                self.conn.execute("""
                    INSERT INTO attendance
                    (student_id, date, time, status)
                    VALUES (?, ?, ?, ?)
                """, (student["id"], today, time_str, "Present"))

        return True


        
    # ---------------- AUTO ABSENT ---------------- #
    def finalize_attendance(self, teacher_account_id):

        today = datetime.now().strftime("%Y-%m-%d")

        students = self.get_students_by_account(teacher_account_id)

        for s in students:
            try:
                with self.conn:
                    self.conn.execute("""
                        INSERT INTO attendance
                        (student_id, date, time, status)
                        VALUES (?, ?, ?, ?)
                    """, (
                        s["id"],
                        today,
                        datetime.now().strftime("%H:%M:%S"),
                        "Absent"
                    ))
            except sqlite3.IntegrityError:
                pass  # already present


        
    def clear_all_students(self, teacher_account_id=None):
        """Delete all students for a given teacher account."""
        if teacher_account_id is None and getattr(self, "teacher_account_id", None):
            teacher_account_id = self.teacher_account_id

        if teacher_account_id:
            with self.conn:
                self.conn.execute(
                    "DELETE FROM students WHERE teacher_account_id = ?",
                    (teacher_account_id,)
                )
        else:
            with self.conn:
                self.conn.execute("DELETE FROM students")


    def get_attendance(self, roll):
        student = self.get_student_by_roll(roll)
        if not student:
            return []
        rows = self.conn.execute("""
            SELECT date, time, status
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
        """, (student["id"],)).fetchall()
        return [dict(r) for r in rows]
    
    # ---------------- ATTENDANCE RECORDS (FULL) ---------------- #

    def get_attendance_records_by_account(self, teacher_account_id):
        """
        Get full attendance records for one teacher account
        """

        rows = self.conn.execute("""
            SELECT 
                s.name,
                s.dept,
                s.year,
                a.date,
                a.time,
                a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.teacher_account_id = ?
            ORDER BY a.date DESC, a.time DESC
        """, (teacher_account_id,)).fetchall()

        return [dict(r) for r in rows]
    
    
    def get_today_attendance_sheet(self, teacher_account_id):

        today = datetime.now().strftime("%Y-%m-%d")

        rows = self.conn.execute("""
            SELECT
                s.id AS student_id,
                s.name,
                s.roll,
                s.dept,
                s.year,
                COALESCE(a.date, ?) AS date,
                COALESCE(a.time, '') AS time,

                CASE
                    WHEN a.status IS NULL THEN ''
                    ELSE a.status
                END AS status

            FROM students s

            LEFT JOIN attendance a
                ON s.id = a.student_id
                AND a.date = ?

            WHERE s.teacher_account_id = ?

            ORDER BY s.name
        """, (today, today, teacher_account_id)).fetchall()

        return [dict(r) for r in rows]
    
    # ---------------- CLOSE CONNECTION ---------------- #

    def close(self):
        try:
            if self.conn:
                self.conn.commit()
                self.conn.close()
                self.conn = None
                print("✅ Database connection closed")
        except Exception as e:
            print("❌ Error closing database:", e)
