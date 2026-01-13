"""
Unit tests for authentication CRUD operations
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import (
    create_user,
    authenticate_user,
    change_password,
    enable_mfa,
    disable_mfa,
)
from app.crud.session import (
    create_session,
    refresh_session,
    revoke_session,
    revoke_all_sessions,
    get_user_sessions,
)
from app.crud.audit_log import (
    create_audit_log,
    get_user_audit_logs,
    get_failed_login_attempts,
)
from app.crud.password_reset import (
    create_password_reset_token,
    verify_password_reset_token,
    mark_password_reset_token_used,
)
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.core.security import hash_token


class TestUserCRUD:
    """Test user CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_user(self, db: AsyncSession):
        """Test creating a new user"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password is not None
        assert user.hashed_password != "SecureP@ssw0rd123"
        assert user.password_changed_at is not None

    @pytest.mark.asyncio
    async def test_create_user_weak_password(self, db: AsyncSession):
        """Test creating user with weak password fails"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="weak",  # Too short and doesn't meet requirements
            role=UserRole.DOCTOR,
        )

        with pytest.raises(ValueError) as exc_info:
            await create_user(db, user_in)

        assert "Password validation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db: AsyncSession):
        """Test successful user authentication"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)
        authenticated_user = await authenticate_user(db, "testuser", "SecureP@ssw0rd123")

        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db: AsyncSession):
        """Test authentication with wrong password"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        await create_user(db, user_in)
        authenticated_user = await authenticate_user(db, "testuser", "WrongPassword123!")

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(self, db: AsyncSession):
        """Test authentication with locked account"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        # Lock the account
        user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        user.failed_login_attempts = 5
        await db.commit()

        authenticated_user = await authenticate_user(db, "testuser", "SecureP@ssw0rd123")

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_change_password(self, db: AsyncSession):
        """Test changing user password"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)
        updated_user = await change_password(
            db, user, "SecureP@ssw0rd123", "NewSecureP@ssw0rd456"
        )

        assert updated_user is not None
        # Verify new password works
        authenticated = await authenticate_user(db, "testuser", "NewSecureP@ssw0rd456")
        assert authenticated is not None

        # Verify old password doesn't work
        authenticated = await authenticate_user(db, "testuser", "SecureP@ssw0rd123")
        assert authenticated is None

    @pytest.mark.asyncio
    async def test_enable_mfa(self, db: AsyncSession):
        """Test enabling MFA for user"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)
        secret = "JBSWY3DPEHPK3PXP"
        updated_user = await enable_mfa(db, user, secret)

        assert updated_user.mfa_enabled is True
        assert updated_user.mfa_secret == secret

    @pytest.mark.asyncio
    async def test_disable_mfa(self, db: AsyncSession):
        """Test disabling MFA for user"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)
        secret = "JBSWY3DPEHPK3PXP"
        await enable_mfa(db, user, secret)

        updated_user = await disable_mfa(db, user)

        assert updated_user.mfa_enabled is False
        assert updated_user.mfa_secret is None


class TestSessionCRUD:
    """Test session CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_session(self, db: AsyncSession):
        """Test creating a user session"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        access_token = "access_token_123"
        refresh_token = "refresh_token_456"

        session = await create_session(
            db=db,
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        assert session is not None
        assert session.user_id == user.id
        assert session.token_hash == hash_token(access_token)
        assert session.refresh_token_hash == hash_token(refresh_token)

    @pytest.mark.asyncio
    async def test_refresh_session(self, db: AsyncSession):
        """Test refresh token rotation"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        old_access_token = "access_token_123"
        old_refresh_token = "refresh_token_456"

        await create_session(
            db=db,
            user=user,
            access_token=old_access_token,
            refresh_token=old_refresh_token,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        new_access_token = "new_access_token_789"
        new_refresh_token = "new_refresh_token_012"

        new_session = await refresh_session(
            db=db,
            old_refresh_token=old_refresh_token,
            new_access_token=new_access_token,
            new_refresh_token=new_refresh_token,
        )

        assert new_session is not None
        assert new_session.token_hash == hash_token(new_access_token)

    @pytest.mark.asyncio
    async def test_revoke_session(self, db: AsyncSession):
        """Test revoking a session"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        session = await create_session(
            db=db,
            user=user,
            access_token="access_token_123",
            refresh_token="refresh_token_456",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        success = await revoke_session(db, session.id, user.id)

        assert success is True
        await db.refresh(session)
        assert session.is_revoked is True
        assert session.revoked_at is not None

    @pytest.mark.asyncio
    async def test_revoke_all_sessions(self, db: AsyncSession):
        """Test revoking all user sessions"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        # Create multiple sessions
        for i in range(3):
            await create_session(
                db=db,
                user=user,
                access_token=f"access_token_{i}",
                refresh_token=f"refresh_token_{i}",
                ip_address="127.0.0.1",
                user_agent="Mozilla/5.0",
            )

        count = await revoke_all_sessions(db, user.id)

        assert count == 3


class TestAuditLogCRUD:
    """Test audit log CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_audit_log(self, db: AsyncSession):
        """Test creating an audit log entry"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        audit_log = await create_audit_log(
            db=db,
            action="LOGIN",
            resource_type="User",
            user_id=user.id,
            username=user.username,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
            request_path="/api/v1/auth/login",
            request_method="POST",
            success=True,
        )

        assert audit_log is not None
        assert audit_log.action == "LOGIN"
        assert audit_log.user_id == user.id

    @pytest.mark.asyncio
    async def test_get_user_audit_logs(self, db: AsyncSession):
        """Test getting audit logs for a user"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        # Create multiple audit logs
        for i in range(5):
            await create_audit_log(
                db=db,
                action=f"ACTION_{i}",
                resource_type="Test",
                user_id=user.id,
                username=user.username,
            )

        logs = await get_user_audit_logs(db, user.id, limit=10)

        assert len(logs) == 5

    @pytest.mark.asyncio
    async def test_get_failed_login_attempts(self, db: AsyncSession):
        """Test getting failed login attempts"""
        username = "testuser"

        # Create failed login attempts
        for _ in range(3):
            await create_audit_log(
                db=db,
                action="LOGIN",
                resource_type="User",
                username=username,
                success=False,
                failure_reason="Invalid password",
            )

        since = datetime.utcnow() - timedelta(minutes=15)
        failed_attempts = await get_failed_login_attempts(db, username, since)

        assert len(failed_attempts) == 3
        assert all(not log.success for log in failed_attempts)


class TestPasswordResetCRUD:
    """Test password reset CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_password_reset_token(self, db: AsyncSession):
        """Test creating password reset token"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        reset_token = await create_password_reset_token(
            db=db,
            user=user,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        assert reset_token is not None
        assert hasattr(reset_token, "plain_token")
        assert reset_token.plain_token is not None
        assert len(reset_token.plain_token) > 0

    @pytest.mark.asyncio
    async def test_verify_password_reset_token(self, db: AsyncSession):
        """Test verifying password reset token"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        reset_token = await create_password_reset_token(
            db=db,
            user=user,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        verified_user = await verify_password_reset_token(db, reset_token.plain_token)

        assert verified_user is not None
        assert verified_user.id == user.id

    @pytest.mark.asyncio
    async def test_verify_invalid_reset_token(self, db: AsyncSession):
        """Test verifying invalid reset token"""
        verified_user = await verify_password_reset_token(db, "invalid_token")

        assert verified_user is None

    @pytest.mark.asyncio
    async def test_mark_reset_token_used(self, db: AsyncSession):
        """Test marking reset token as used"""
        user_in = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="SecureP@ssw0rd123",
            role=UserRole.DOCTOR,
        )

        user = await create_user(db, user_in)

        reset_token = await create_password_reset_token(
            db=db,
            user=user,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        success = await mark_password_reset_token_used(db, reset_token.plain_token)

        assert success is True

        # Token should no longer be valid
        verified_user = await verify_password_reset_token(db, reset_token.plain_token)
        assert verified_user is None
