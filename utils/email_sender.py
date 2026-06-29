import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# ---------------- DEV EMAIL ---------------- #

SENDER_EMAIL = os.getenv("APP_EMAIL")
APP_PASSWORD  = os.getenv("APP_EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587


def send_email(to_email, subject, body):
   
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("❌ Email credentials not set.")
        return False

    # ── Normalise recipient(s) ────────────────────────────────────────────────
    if isinstance(to_email, list):
        recipients = to_email                    # keep the list for sendmail()
        to_header  = ", ".join(to_email)         # "To:" header must be a string
    else:
        recipients = [to_email]
        to_header  = to_email
    # ─────────────────────────────────────────────────────────────────────────

    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = to_header          # always a string now
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())

        print(f"✅ Email sent to {to_header}")
        return True
    except Exception as e:
        print("❌ Email sending failed:", e)
        return False


def send_otp_email(to_email, otp):
    """Sends a password reset OTP to the given email."""
    subject = "🔐 Password Reset OTP"
    body = f"""
Hello,

Your One-Time Password (OTP) for password reset is:

🔐 {otp}

⏳ This OTP is valid for 5 minutes.
If you did not request this, please ignore this email.

Regards,
Face Recognition System
"""
    return send_email(to_email, subject, body)


def send_attendance_report_email(student_name, student_email, total_present,
                                  total_absent, month_year, report_filepath=None):
    """
    Sends monthly attendance report to a student via email.
    Optionally attaches an Excel report file.
    """
    if not student_email:
        err = f"No email address for student {student_name}"
        print(f"❌ {err}")
        return False, err

    subject = f"📊 Your Monthly Attendance Report - {month_year}"

    total_days = total_present + total_absent
    attendance_percentage = (total_present / total_days * 100) if total_days > 0 else 0

    body = f"""
Hello {student_name},

Your monthly attendance report for {month_year} is ready.

📋 ATTENDANCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Total Present:     {total_present} days
❌ Total Absent:      {total_absent} days
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Attendance Rate:   {attendance_percentage:.1f}%

Your attendance has been recorded in our system. If you believe there's any
discrepancy, please contact your instructor.

Best regards,
Attendance Management System
"""

    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = student_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach Excel report if provided
    if report_filepath and os.path.exists(report_filepath):
        try:
            from email.mime.base import MIMEBase
            from email import encoders

            filename = os.path.basename(report_filepath)
            with open(report_filepath, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}"
                )
                msg.attach(part)
        except Exception as e:
            print(f"⚠️ Could not attach report file: {e}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Attendance report email sent to {student_email}")
        return True, ""
    except Exception as e:
        err = str(e)
        print(f"❌ Email sending failed: {err}")
        return False, err
