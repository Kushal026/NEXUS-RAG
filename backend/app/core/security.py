"""
Security, Authentication & Multi-Tenancy Core for NEXUS-RAG (Phase 10).
Handles password hashing, JWT session tokens, Role-Based Access Control (RBAC), and tenant context scoping.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import base64
import json
import uuid
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logging import logger


class UserRole(str, Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: str
    tenant_id: str = "default_tenant"
    role: UserRole = UserRole.RESEARCHER
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TokenPayload(BaseModel):
    sub: str  # user_id
    username: str
    tenant_id: str
    role: str
    exp: int


class SecurityService:
    """Provides cryptographic password hashing, JWT signing, and tenant isolation."""

    SECRET_KEY = getattr(settings, "SECRET_KEY", "nexus_rag_enterprise_secret_key_2026_super_secure")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

    def __init__(self):
        # In-memory user store for deterministic authentication
        self._users_db: Dict[str, Dict[str, Any]] = {
            "admin": {
                "user_id": "usr-admin-001",
                "username": "admin",
                "email": "admin@nexus-rag.internal",
                "hashed_password": self.hash_password("AdminSecure2026!"),
                "tenant_id": "nexus_primary_tenant",
                "role": UserRole.ADMIN,
                "is_active": True
            },
            "researcher": {
                "user_id": "usr-res-002",
                "username": "researcher",
                "email": "researcher@nexus-rag.internal",
                "hashed_password": self.hash_password("Researcher2026!"),
                "tenant_id": "nexus_primary_tenant",
                "role": UserRole.RESEARCHER,
                "is_active": True
            }
        }

    def hash_password(self, password: str) -> str:
        """Secure SHA-256 HMAC password hashing with system salt."""
        h = hmac.new(self.SECRET_KEY.encode(), password.encode(), hashlib.sha256)
        return h.hexdigest()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain text password against hashed password."""
        return hmac.compare_digest(self.hash_password(plain_password), hashed_password)

    def create_access_token(self, user: UserProfile, expires_delta: Optional[timedelta] = None) -> str:
        """Encodes and signs a JWT access token."""
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "tenant_id": user.tenant_id,
            "role": user.role.value if isinstance(user.role, UserRole) else str(user.role),
            "exp": int(expire.timestamp())
        }
        # Standard Base64Url JWT encoding
        header = {"alg": "HS256", "typ": "JWT"}
        h_bytes = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
        p_bytes = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')
        signing_input = h_bytes + b'.' + p_bytes
        signature = hmac.new(self.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        s_bytes = base64.urlsafe_b64encode(signature).rstrip(b'=')
        return (signing_input + b'.' + s_bytes).decode()

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verifies and decodes a signed JWT access token."""
        try:
            parts = token.strip().split('.')
            if len(parts) != 3:
                return None
            signing_input = (parts[0] + '.' + parts[1]).encode()
            sig_received = base64.urlsafe_b64decode(parts[2] + '=' * (-len(parts[2]) % 4))
            sig_expected = hmac.new(self.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
            if not hmac.compare_digest(sig_received, sig_expected):
                return None
            
            payload_json = base64.urlsafe_b64decode(parts[1] + '=' * (-len(parts[1]) % 4)).decode()
            data = json.loads(payload_json)
            if datetime.utcnow().timestamp() > data.get("exp", 0):
                return None  # Expired
            return TokenPayload(**data)
        except Exception as e:
            logger.warning(f"JWT Token validation error: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[UserProfile]:
        """Validates credentials and returns UserProfile."""
        user_record = self._users_db.get(username)
        if not user_record:
            return None
        if not self.verify_password(password, user_record["hashed_password"]):
            return None
        return UserProfile(
            user_id=user_record["user_id"],
            username=user_record["username"],
            email=user_record["email"],
            tenant_id=user_record["tenant_id"],
            role=user_record["role"],
            is_active=user_record["is_active"]
        )

    def register_user(self, username: str, email: str, password: str, tenant_id: str = "default_tenant", role: UserRole = UserRole.RESEARCHER) -> UserProfile:
        """Registers a new tenant-scoped user."""
        if username in self._users_db:
            raise ValueError(f"Username '{username}' is already registered.")
        user_id = f"usr-{uuid.uuid4().hex[:6]}"
        self._users_db[username] = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": self.hash_password(password),
            "tenant_id": tenant_id,
            "role": role,
            "is_active": True
        }
        return UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            tenant_id=tenant_id,
            role=role,
            is_active=True
        )


security_service = SecurityService()
