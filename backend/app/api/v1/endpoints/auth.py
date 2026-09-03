"""
Authentication & Authorization API Endpoints for NEXUS.
Provides JWT session token issuance, user registration, profile inspection, password recovery, and session invalidation.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel, EmailStr
from app.core.security import security_service, UserProfile, UserRole, TokenPayload
from app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["Authentication & Multi-Tenancy"])


class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    name: Optional[str] = None
    tenant_id: str = "nexus_primary_tenant"
    role: UserRole = UserRole.RESEARCHER


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


def get_current_user(authorization: Optional[str] = Header(None)) -> UserProfile:
    """Dependency extracting and validating user from Authorization: Bearer <token>."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )
    token = authorization.split(" ")[1]
    payload = security_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or token invalid."
        )
    user_record = security_service._users_db.get(payload.username)
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found."
        )
    return UserProfile(
        user_id=user_record["user_id"],
        username=user_record["username"],
        name=user_record.get("name") or user_record["username"].capitalize(),
        email=user_record["email"],
        tenant_id=user_record["tenant_id"],
        role=user_record["role"],
        is_active=user_record["is_active"]
    )


@router.post("/login", response_model=AuthTokenResponse)
def login(request: LoginRequest):
    """Authenticates user credentials by username/email and returns a signed JWT token."""
    user = security_service.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )
    token = security_service.create_access_token(user)
    return AuthTokenResponse(access_token=token, user=user)


@router.post("/register", response_model=AuthTokenResponse)
def register(request: RegisterRequest):
    """Registers a new tenant user and returns an active JWT session."""
    try:
        user = security_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            name=request.name,
            tenant_id=request.tenant_id,
            role=request.role
        )
        token = security_service.create_access_token(user)
        return AuthTokenResponse(access_token=token, user=user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """Generates a secure password reset token for the given user email."""
    token = security_service.generate_password_reset_token(request.email)
    # Return message (and token for direct testing if required)
    if not token:
        return {"status": "success", "message": "If that email exists in our system, a password recovery link has been sent."}
    return {
        "status": "success",
        "message": "Password recovery token generated.",
        "reset_token": token
    }


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Resets user password using the provided recovery token."""
    success = security_service.reset_password(request.token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )
    return {"status": "success", "message": "Password updated successfully. You can now log in with your new password."}


@router.get("/me", response_model=UserProfile)
def get_current_profile(token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Validates JWT token and returns current user profile."""
    jwt_token = token
    if not jwt_token and authorization and authorization.startswith("Bearer "):
        jwt_token = authorization.split(" ")[1]
    
    if not jwt_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization token.")

    payload = security_service.verify_token(jwt_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
    
    user_record = security_service._users_db.get(payload.username)
    if not user_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    return UserProfile(
        user_id=user_record["user_id"],
        username=user_record["username"],
        name=user_record.get("name") or user_record["username"].capitalize(),
        email=user_record["email"],
        tenant_id=user_record["tenant_id"],
        role=user_record["role"],
        is_active=user_record["is_active"]
    )


@router.post("/logout")
def logout():
    """Invalidates active session on the client side."""
    return {"status": "success", "message": "Successfully logged out."}
