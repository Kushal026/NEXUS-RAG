"""
Unit and Integration tests for Production Security & Authentication (Phase 10).
"""
import pytest
from app.core.security import security_service, UserProfile, UserRole


def test_password_hashing_and_verification():
    raw_pass = "Enterprise2026!Secure"
    hashed = security_service.hash_password(raw_pass)

    assert hashed != raw_pass
    assert security_service.verify_password(raw_pass, hashed) is True
    assert security_service.verify_password("WrongPassword!", hashed) is False


def test_jwt_token_lifecycle():
    user = UserProfile(
        user_id="usr-test-123",
        username="lead_researcher",
        email="lead@nexus.internal",
        tenant_id="tenant_aerospace_01",
        role=UserRole.ADMIN
    )

    token = security_service.create_access_token(user)
    assert isinstance(token, str)
    assert len(token.split('.')) == 3

    payload = security_service.verify_token(token)
    assert payload is not None
    assert payload.sub == "usr-test-123"
    assert payload.username == "lead_researcher"
    assert payload.tenant_id == "tenant_aerospace_01"
    assert payload.role == "admin"


def test_multi_tenancy_user_registration():
    new_user = security_service.register_user(
        username="biomed_analyst_99",
        email="analyst@biomed.internal",
        password="BioSecurePassword2026!",
        tenant_id="tenant_biomed_vault",
        role=UserRole.RESEARCHER
    )

    assert new_user.username == "biomed_analyst_99"
    assert new_user.tenant_id == "tenant_biomed_vault"

    # Authenticate new user
    auth_user = security_service.authenticate_user("biomed_analyst_99", "BioSecurePassword2026!")
    assert auth_user is not None
    assert auth_user.tenant_id == "tenant_biomed_vault"
