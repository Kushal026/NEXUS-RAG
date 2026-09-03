"""
Security, Authentication & Multi-Tenancy Core for NEXUS.
Handles password hashing, JWT session tokens, Role-Based Access Control (RBAC), and tenant/user context scoping.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import base64
import json
import uuid
import secrets
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
    name: Optional[str] = None
    email: str
    tenant_id: str = "nexus_primary_tenant"
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
    """Provides cryptographic password hashing, JWT signing, multi-user isolation and password recovery."""

    SECRET_KEY = getattr(settings, "SECRET_KEY", "nexus_enterprise_secret_key_2026_super_secure")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

    def __init__(self):
        # In-memory user store for deterministic authentication & isolation
        self._users_db: Dict[str, Dict[str, Any]] = {
            "admin": {
                "user_id": "usr-admin-001",
                "username": "admin",
                "name": "NEXUS Administrator",
                "email": "admin@nexus.internal",
                "hashed_password": self.hash_password("AdminSecure2026!"),
                "tenant_id": "nexus_primary_tenant",
                "role": UserRole.ADMIN,
                "is_active": True
            },
            "researcher": {
                "user_id": "usr-res-002",
                "username": "researcher",
                "name": "Lead AI Researcher",
                "email": "researcher@nexus.internal",
                "hashed_password": self.hash_password("Researcher2026!"),
                "tenant_id": "nexus_primary_tenant",
                "role": UserRole.RESEARCHER,
                "is_active": True
            }
        }
        # In-memory password reset tokens: token -> {email, exp}
        self._reset_tokens: Dict[str, Dict[str, Any]] = {}
        # Document ownership registry: doc_id -> owner_user_id
        self._document_owners: Dict[str, str] = {}

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

    def authenticate_user(self, email_or_username: str, password: str) -> Optional[UserProfile]:
        """Validates credentials by either username or email and returns UserProfile."""
        target_record = None
        for record in self._users_db.values():
            if record["username"].lower() == email_or_username.lower() or record["email"].lower() == email_or_username.lower():
                target_record = record
                break

        if not target_record:
            return None
        if not self.verify_password(password, target_record["hashed_password"]):
            return None
        return UserProfile(
            user_id=target_record["user_id"],
            username=target_record["username"],
            name=target_record.get("name") or target_record["username"].capitalize(),
            email=target_record["email"],
            tenant_id=target_record["tenant_id"],
            role=target_record["role"],
            is_active=target_record["is_active"]
        )

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        name: Optional[str] = None,
        tenant_id: str = "nexus_primary_tenant",
        role: UserRole = UserRole.RESEARCHER
    ) -> UserProfile:
        """Registers a new tenant-scoped user."""
        # Check uniqueness of username and email
        for record in self._users_db.values():
            if record["username"].lower() == username.lower():
                raise ValueError(f"Username '{username}' is already registered.")
            if record["email"].lower() == email.lower():
                raise ValueError(f"Email '{email}' is already registered.")

        user_id = f"usr-{uuid.uuid4().hex[:8]}"
        self._users_db[username] = {
            "user_id": user_id,
            "username": username,
            "name": name or username.capitalize(),
            "email": email,
            "hashed_password": self.hash_password(password),
            "tenant_id": tenant_id,
            "role": role,
            "is_active": True
        }
        return UserProfile(
            user_id=user_id,
            username=username,
            name=name or username.capitalize(),
            email=email,
            tenant_id=tenant_id,
            role=role,
            is_active=True
        )

    def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generates a secure password reset token valid for 30 minutes."""
        user_exists = any(r["email"].lower() == email.lower() for r in self._users_db.values())
        if not user_exists:
            return None
        token = secrets.token_urlsafe(32)
        exp = datetime.utcnow() + timedelta(minutes=30)
        self._reset_tokens[token] = {
            "email": email.lower(),
            "exp": int(exp.timestamp())
        }
        return token

    def reset_password(self, token: str, new_password: str) -> bool:
        """Resets user password with valid reset token."""
        entry = self._reset_tokens.get(token)
        if not entry:
            return False
        if datetime.utcnow().timestamp() > entry["exp"]:
            del self._reset_tokens[token]
            return False

        email = entry["email"]
        for user_key, record in self._users_db.items():
            if record["email"].lower() == email:
                record["hashed_password"] = self.hash_password(new_password)
                del self._reset_tokens[token]
                return True
        return False

    def set_document_owner(self, document_id: str, user_id: str) -> None:
        """Assigns document ownership."""
        self._document_owners[document_id] = user_id

    def is_document_accessible(self, document_id: str, user_id: str, tenant_id: str = "nexus_primary_tenant") -> bool:
        """Verifies if user has permission to view or delete document."""
        owner = self._document_owners.get(document_id)
        if not owner:
            return True  # Legacy/system documents accessible to all tenant users
        return owner == user_id


security_service = SecurityService()
