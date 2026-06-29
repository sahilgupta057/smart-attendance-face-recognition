import sqlite3
import bcrypt
import random
from datetime import datetime, timedelta
from services.api_client import login as api_login

class AuthDatabase:
    def __init__(self, db_path="users.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def get_teacher_assignments(self, user_id):
        rows = self.conn.execute("""
            SELECT id, class, subject FROM teacher_assignments
            WHERE user_id=?
        """, (user_id,)).fetchall()
        return [{"id": r["id"], "class": r["class"], "subject": r["subject"]} for r in rows]


    def create_table(self):
        # ------------------ USERS TABLE ------------------ #
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                mobile TEXT,
                password TEXT NOT NULL,
                profile_image TEXT,
                reset_otp TEXT,
                otp_expiry TEXT
            )
        """)

        columns = [
            row["name"]
            for row in self.conn.execute("PRAGMA table_info(users)")
        ]

        if "profile_image" not in columns:
            self.conn.execute(
                "ALTER TABLE users ADD COLUMN profile_image TEXT"
            )
            self.conn.commit()
        # ------------------ TEACHER ASSIGNMENTS TABLE ------------------ #
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS teacher_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                class TEXT NOT NULL,
                subject TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.conn.commit()

        

    def update_profile_image(self, email, image_path):
        self.conn.execute(
            "UPDATE users SET profile_image=? WHERE email=?",
            (image_path, email)
        )
        self.conn.commit()


    def get_profile_image(self, email):
        row = self.conn.execute(
            "SELECT profile_image FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if row:
            return row["profile_image"]

        return None

    # ---------------- SIGNUP / CREATE USER ---------------- #
    def create_user(self, name, email, mobile, password, assignments=None):
        if self.user_exists(email):
            return False
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, mobile, password)
            VALUES (?, ?, ?, ?)
        """, (name, email, mobile, hashed_pw))
        user_id = cursor.lastrowid

        # Save assignments if any
        if assignments:
            for assign in assignments:
                cursor.execute("""
                    INSERT INTO teacher_assignments (user_id, class, subject)
                    VALUES (?, ?, ?)
                """, (user_id, assign['class'], assign['subject']))
        self.conn.commit()
        return True


    # ---------------- LOGIN / AUTHENTICATE ---------------- #
    def authenticate(self, email, password):
        row = self.conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            return None

        if bcrypt.checkpw(password.encode("utf-8"), row["password"].encode("utf-8")):
            user_id = row["id"]

            assignments = self.get_teacher_assignments(user_id)

            # ✅ NEW: Cloud login
            try:
                from services.api_client import login as api_login
                import json, os

                cloud = api_login(email, password)

                if "token" in cloud:
                    os.makedirs("config", exist_ok=True)
                    with open("config/token.json", "w") as f:
                        json.dump(cloud, f)

            except Exception as e:
                print("Cloud login failed:", e)

            return {
                "id": user_id,
                "name": row["name"],
                "email": row["email"],
                "mobile": row["mobile"],
                "profile_image": row["profile_image"],
                "assignments": assignments
            }
        return None


    # ---------------- HELPER ---------------- #
    def user_exists(self, email):
        row = self.conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone()
        return row is not None

    # ---------------- PASSWORD / OTP ---------------- #
    def generate_otp(self, email):
        otp = str(random.randint(100000, 999999))
        expiry = (datetime.now() + timedelta(minutes=5)).isoformat()
        self.conn.execute("""
            UPDATE users SET reset_otp=?, otp_expiry=? WHERE email=?
        """, (otp, expiry, email))
        self.conn.commit()
        return otp

    def verify_otp(self, email, otp):
        row = self.conn.execute("""
            SELECT reset_otp, otp_expiry FROM users WHERE email=?
        """, (email,)).fetchone()
        if not row:
            return False
        if row["reset_otp"] != otp:
            return False
        if datetime.fromisoformat(row["otp_expiry"]) < datetime.now():
            return False
        return True

    def update_password(self, email, new_password: str):
        # Hash inside this method
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.conn.execute("""
            UPDATE users
            SET password=?, reset_otp=NULL, otp_expiry=NULL
            WHERE email=?
        """, (hashed, email))
        self.conn.commit()

    # ---------------- DELETE USER ---------------- #
    def delete_user(self, email):
        """Delete user and any teacher_assignments. Returns True on success."""
        row = self.conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            return False
        user_id = row["id"]
        with self.conn:
            self.conn.execute("DELETE FROM teacher_assignments WHERE user_id = ?", (user_id,))
            self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
        return True

