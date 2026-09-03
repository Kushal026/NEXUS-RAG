"""
Authentication & Authorization API Endpoints for NEXUS-RAG (Phase 10).
Provides JWT session token issuance, user registration, and profile inspection.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from app.core.security import security_service, UserProfile, UserRole, TokenPayload
from app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["Authentication & Multi-Tenancy"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    tenant_id: str = "nexus_primary_tenant"
    role: UserRole = UserRole.RESEARCHER


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


@router.post("/login", response_model=AuthTokenResponse)
def login(request: LoginRequest):
    """Authenticates user credentials and returns a signed JWT token."""
    user = security_service.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
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
            tenant_id=request.tenant_id,
            role=request.role
        )
        token = security_service.create_access_token(user)
        return AuthTokenResponse(access_token=token, user=user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserProfile)
def get_current_profile(token: str):
    """Validates JWT token and returns current user profile."""
    payload = security_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
    user_record = security_service._users_db.get(payload.username)
    if not user_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserProfile(
        user_id=user_record["user_id"],
        username=user_record["username"],
        email=user_record["email"],
        tenant_id=user_record["tenant_id"],
        role=user_record["role"],
        is_active=user_record["is_active"]
    )
