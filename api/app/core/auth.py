"""Authentication and Email Verification System for PanchangHub Astrology Suite.

Features:
- Email registration & login (passwords hashed with PBKDF2-SHA256).
- Instant verification for Gmail addresses (@gmail.com / @googlemail.com).
- 6-digit OTP code verification for all other email addresses.
- Signed session tokens using HMAC-SHA256.
- Anti-spam & abuse prevention: verified users receive unlimited access to advanced
  astrological calculations (D1-D60 vargas, Prashna, KP System, PDF downloads).
- Persistent SQLite storage for users and sessions.
"""
from __future__ import annotations
import os
import sqlite3
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple

# Database path in data or api directory
_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_DIR, "users.db")
SECRET_KEY = os.environ.get("PH_SECRET_KEY", "panchanghub_astrology_super_secret_key_2026_vedic_divination")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT,
                name TEXT,
                is_verified INTEGER DEFAULT 0,
                verification_code TEXT,
                code_expires_at REAL,
                created_at REAL,
                last_login REAL,
                tier TEXT DEFAULT 'verified'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    conn.close()

init_db()

def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${dk.hex()}"

def _verify_password(password: str, hashed: str) -> bool:
    if not hashed or "$" not in hashed:
        return False
    salt, dk_hex = hashed.split("$", 1)
    new_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return hmac.compare_digest(new_dk.hex(), dk_hex)

def is_gmail(email: str) -> bool:
    email_l = email.strip().lower()
    return email_l.endswith("@gmail.com") or email_l.endswith("@googlemail.com")

def create_token(user_id: int, email: str, is_verified: bool) -> str:
    payload = f"{user_id}:{email}:{1 if is_verified else 0}:{int(time.time())}"
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    if not token or ":" not in token:
        return None
    parts = token.split(":")
    if len(parts) != 5:
        return None
    user_id_s, email, ver_s, ts_s, sig = parts
    payload = f"{user_id_s}:{email}:{ver_s}:{ts_s}"
    expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None
    # Token valid for 90 days
    if time.time() - int(ts_s) > 90 * 86400:
        return None
    return {
        "id": int(user_id_s),
        "email": email,
        "is_verified": bool(int(ver_s))
    }

def register_user(email: str, password: Optional[str] = None, name: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[str]]:
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Invalid email address", None, None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, is_verified FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()
    
    is_auto_verified = is_gmail(email)
    now = time.time()
    pwd_hash = _hash_password(password) if password else None
    otp_code = f"{secrets.randbelow(900000) + 100000}" if not is_auto_verified else None
    code_expires = now + 1800 if otp_code else 0.0

    if existing:
        user_id = existing["id"]
        # Update user details if not verified or updating password
        with conn:
            if pwd_hash:
                conn.execute("UPDATE users SET password_hash = ?, last_login = ? WHERE id = ?", (pwd_hash, now, user_id))
            if not existing["is_verified"] and is_auto_verified:
                conn.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user_id,))
        ver_status = bool(existing["is_verified"]) or is_auto_verified
        token = create_token(user_id, email, ver_status)
        conn.close()
        return True, "Login successful", {"id": user_id, "email": email, "is_verified": ver_status}, token

    # Create new user
    with conn:
        cursor.execute("""
            INSERT INTO users (email, password_hash, name, is_verified, verification_code, code_expires_at, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, pwd_hash, name or email.split("@")[0], 1 if is_auto_verified else 0, otp_code, code_expires, now, now))
        user_id = cursor.lastrowid

    token = create_token(user_id, email, is_auto_verified)
    user_data = {
        "id": user_id,
        "email": email,
        "name": name or email.split("@")[0],
        "is_verified": is_auto_verified,
        "otp_required": not is_auto_verified
    }
    conn.close()
    msg = "Account created and verified via Gmail!" if is_auto_verified else f"Account created. Verification OTP: {otp_code}"
    return True, msg, user_data, token

def login_user(email: str, password: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[str]]:
    email = email.strip().lower()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        # If logging in with Gmail, seamlessly auto-register
        if is_gmail(email):
            return register_user(email, password)
        return False, "No account found with this email. Please register.", None, None

    if password and user["password_hash"]:
        if not _verify_password(password, user["password_hash"]):
            conn.close()
            return False, "Incorrect password.", None, None

    # Update last login
    now = time.time()
    with conn:
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user["id"]))

    is_verified = bool(user["is_verified"]) or is_gmail(email)
    token = create_token(user["id"], user["email"], is_verified)
    user_data = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "is_verified": is_verified
    }
    conn.close()
    return True, "Login successful", user_data, token

def verify_otp(email: str, code: str) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[str]]:
    email = email.strip().lower()
    code = code.strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False, "User not found.", None, None

    now = time.time()
    if user["verification_code"] != code or now > user["code_expires_at"]:
        conn.close()
        return False, "Invalid or expired verification code.", None, None

    with conn:
        conn.execute("UPDATE users SET is_verified = 1, verification_code = NULL WHERE id = ?", (user["id"],))

    token = create_token(user["id"], user["email"], True)
    conn.close()
    return True, "Email successfully verified!", {"id": user["id"], "email": user["email"], "is_verified": True}, token

def get_user_from_request(cookies: Dict[str, str], headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    token = cookies.get("ph_auth")
    if not token and "authorization" in headers:
        auth = headers["authorization"]
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        return None
    return verify_token(token)
