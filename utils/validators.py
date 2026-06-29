import re

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    return len(password) >= 6

def is_valid_mobile(mobile):
    return re.match(r"^\d{10}$", mobile)
