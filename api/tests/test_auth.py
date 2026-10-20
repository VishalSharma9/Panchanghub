"""Tests for Authentication, Gmail Auto-Verification and OTP Flow."""
import pytest
import secrets
from fastapi.testclient import TestClient
from app.main import app
from app.core import auth

client = TestClient(app)

def test_gmail_auto_verification():
    rnd = secrets.token_hex(4)
    email = f"astrologer_{rnd}@gmail.com"
    resp = client.post("/api/auth/register", json={
        "email": email,
        "password": "secret_password",
        "name": "Vedic Scholar"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["user"]["is_verified"] is True
    assert "token" in data

    # Verify session with /me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["logged_in"] is True
    assert me_data["user"]["email"] == email
    assert me_data["user"]["is_verified"] is True

def test_otp_verification_flow():
    rnd = secrets.token_hex(4)
    email = f"seeker_{rnd}@example.com"
    # 1. Register with non-gmail
    resp = client.post("/api/auth/register", json={
        "email": email,
        "password": "seeker_pass",
        "name": "Jyotish Seeker"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["is_verified"] is False
    
    # Extract OTP code from message
    code = data["message"].split(": ")[-1]
    assert len(code) == 6

    # 2. Verify OTP
    verify_resp = client.post("/api/auth/verify-otp", json={
        "email": email,
        "code": code
    })
    assert verify_resp.status_code == 200
    ver_data = verify_resp.json()
    assert ver_data["user"]["is_verified"] is True

def test_login_routes():
    rnd = secrets.token_hex(4)
    email = f"user_{rnd}@gmail.com"
    # Register first
    client.post("/api/auth/register", json={"email": email, "password": "password123"})
    
    # Login
    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "password123"
    })
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # Web route /login
    web_resp = client.get("/login")
    assert web_resp.status_code == 200
    assert "Member Access &amp; Email Verification" in web_resp.text
