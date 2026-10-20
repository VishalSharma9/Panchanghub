"""Authentication and Session Management API Router."""
from fastapi import APIRouter, Request, Response, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional

from ...core import auth

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthRequest(BaseModel):
    email: str = Field(..., max_length=120)
    password: Optional[str] = None
    name: Optional[str] = None

class OTPVerifyRequest(BaseModel):
    email: str = Field(..., max_length=120)
    code: str = Field(..., min_length=4, max_length=10)

@router.post("/register", summary="Register a new user or auto-verify via Gmail")
def register_endpoint(req: AuthRequest, response: Response):
    ok, msg, user, token = auth.register_user(req.email, req.password, req.name)
    if not ok:
        raise HTTPException(400, msg)
    if token:
        response.set_cookie("ph_auth", token, max_age=90 * 86400, path="/", samesite="lax", httponly=False)
    return {"success": True, "message": msg, "user": user, "token": token}

@router.post("/login", summary="Login with email/password or Gmail")
def login_endpoint(req: AuthRequest, response: Response):
    ok, msg, user, token = auth.login_user(req.email, req.password)
    if not ok:
        raise HTTPException(401, msg)
    if token:
        response.set_cookie("ph_auth", token, max_age=90 * 86400, path="/", samesite="lax", httponly=False)
    return {"success": True, "message": msg, "user": user, "token": token}

@router.post("/verify-otp", summary="Verify email using 6-digit OTP code")
def verify_otp_endpoint(req: OTPVerifyRequest, response: Response):
    ok, msg, user, token = auth.verify_otp(req.email, req.code)
    if not ok:
        raise HTTPException(400, msg)
    if token:
        response.set_cookie("ph_auth", token, max_age=90 * 86400, path="/", samesite="lax", httponly=False)
    return {"success": True, "message": msg, "user": user, "token": token}

@router.post("/logout", summary="Logout and clear authentication session")
def logout_endpoint(response: Response):
    response.delete_cookie("ph_auth", path="/")
    return {"success": True, "message": "Logged out successfully."}

@router.get("/me", summary="Get currently logged in user profile & verification status")
def me_endpoint(request: Request):
    user = auth.get_user_from_request(request.cookies, dict(request.headers))
    if not user:
        return {"logged_in": False, "user": None}
    return {"logged_in": True, "user": user}
