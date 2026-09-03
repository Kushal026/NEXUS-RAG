"""
Unit tests for NEXUS Multi-User Authentication, Password Reset, and Tenant/User Data Isolation.
"""
import pytest
from app.core.security import security_service, UserRole


def test_user_registration_and_duplicate_prevention():
    # Register user A
    username = "test_researcher_alpha"
    email = "alpha@nexus.internal"
    user = security_service.register_user(
        username=username,
        email=email,
        password="SecureAlphaPass2026!",
        name="Alpha Researcher"
    )
    assert user.username == username
    assert user.email == email
    assert user.name == "Alpha Researcher"
    assert user.is_active is True

    # Duplicate username should be rejected
    with pytest.raises(ValueError, match="already registered"):
        security_service.register_user(
            username=username,
            email="unique_email@nexus.internal",
            password="SomePassword2026!"
        )

    # Duplicate email should be rejected
    with pytest.raises(ValueError, match="already registered"):
        security_service.register_user(
            username="unique_username",
            email=email,
            password="SomePassword2026!"
        )


def test_authentication_by_username_and_email():
    # Login by username
    auth_user = security_service.authenticate_user("admin", "AdminSecure2026!")
    assert auth_user is not None
    assert auth_user.role == UserRole.ADMIN

    # Login by email
    auth_by_email = security_service.authenticate_user("admin@nexus.internal", "AdminSecure2026!")
    assert auth_by_email is not None
    assert auth_by_email.user_id == auth_user.user_id

    # Invalid password should fail
    invalid_auth = security_service.authenticate_user("admin", "WrongPassword!")
    assert invalid_auth is None


def test_password_reset_flow():
    email = "researcher@nexus.internal"
    token = security_service.generate_password_reset_token(email)
    assert token is not None
    assert len(token) > 20

    # Reset password with valid token
    new_pass = "UpdatedResearcherPass2026!"
    success = security_service.reset_password(token, new_pass)
    assert success is True

    # Login with new password
    auth_user = security_service.authenticate_user(email, new_pass)
    assert auth_user is not None

    # Used token should not work again
    second_attempt = security_service.reset_password(token, "AnotherPassword!")
    assert second_attempt is False


def test_document_ownership_and_user_isolation():
    user_a = "usr-alpha-123"
    user_b = "usr-beta-456"
    doc_id = "doc-confidential-001"

    security_service.set_document_owner(doc_id, user_a)

    # User A (owner) should have access
    assert security_service.is_document_accessible(doc_id, user_a) is True

    # User B should be denied access to User A's document
    assert security_service.is_document_accessible(doc_id, user_b) is False
