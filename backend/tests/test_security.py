"""
Unit tests for security functions
"""
import pytest
from datetime import datetime, timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_token_hash,
    generate_mfa_secret,
    generate_mfa_backup_codes,
    get_mfa_totp_uri,
    verify_mfa_code,
    validate_password_strength,
    is_password_expired,
)
from app.core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long

    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token(self):
        """Test creating access token"""
        user_id = 1
        token = create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        user_id = 1
        token = create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        """Test decoding valid token"""
        user_id = 1
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        payload = decode_token("invalid_token")

        assert payload is None

    def test_access_token_expiration(self):
        """Test access token expiration"""
        user_id = 1
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        # Check expiration time
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Allow 5 second difference
        assert abs((exp_datetime - expected_exp).total_seconds()) < 5

    def test_token_type_differentiation(self):
        """Test that access and refresh tokens have different types"""
        user_id = 1
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"


class TestTokenHashing:
    """Test token hashing for secure storage"""

    def test_hash_token(self):
        """Test token hashing"""
        token = "test_token_123"
        hashed = hash_token(token)

        assert hashed is not None
        assert hashed != token
        assert len(hashed) == 64  # SHA-256 produces 64 hex characters

    def test_verify_token_hash_correct(self):
        """Test verifying correct token hash"""
        token = "test_token_123"
        hashed = hash_token(token)

        assert verify_token_hash(token, hashed) is True

    def test_verify_token_hash_incorrect(self):
        """Test verifying incorrect token hash"""
        token = "test_token_123"
        wrong_token = "wrong_token_456"
        hashed = hash_token(token)

        assert verify_token_hash(wrong_token, hashed) is False


class TestMFA:
    """Test Multi-Factor Authentication functions"""

    def test_generate_mfa_secret(self):
        """Test MFA secret generation"""
        secret = generate_mfa_secret()

        assert secret is not None
        assert len(secret) == 32  # Base32 encoded secret
        assert secret.isalnum() or secret.isupper()

    def test_generate_mfa_backup_codes(self):
        """Test MFA backup codes generation"""
        codes = generate_mfa_backup_codes(10)

        assert len(codes) == 10
        assert all(len(code) == 8 for code in codes)  # 4 bytes = 8 hex chars
        assert all(code.isupper() for code in codes)
        # Check uniqueness
        assert len(set(codes)) == 10

    def test_get_mfa_totp_uri(self):
        """Test TOTP URI generation"""
        secret = "JBSWY3DPEHPK3PXP"
        username = "testuser"
        uri = get_mfa_totp_uri(secret, username)

        assert uri is not None
        assert "otpauth://totp" in uri
        assert secret in uri
        assert username in uri
        assert "SIMRS" in uri

    def test_verify_mfa_code(self):
        """Test MFA code verification"""
        secret = generate_mfa_secret()

        # Generate a valid TOTP code
        import pyotp
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        assert verify_mfa_code(secret, valid_code) is True

    def test_verify_invalid_mfa_code(self):
        """Test invalid MFA code verification"""
        secret = generate_mfa_secret()
        invalid_code = "000000"

        assert verify_mfa_code(secret, invalid_code) is False


class TestPasswordValidation:
    """Test password validation"""

    def test_valid_password(self):
        """Test valid password passes validation"""
        password = "SecureP@ssw0rd123"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is True
        assert len(errors) == 0

    def test_password_too_short(self):
        """Test password that's too short"""
        password = "Short1!"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is False
        assert any("12 characters" in error for error in errors)

    def test_password_no_uppercase(self):
        """Test password without uppercase"""
        password = "lowercase123!"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is False
        assert any("uppercase" in error for error in errors)

    def test_password_no_lowercase(self):
        """Test password without lowercase"""
        password = "UPPERCASE123!"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is False
        assert any("lowercase" in error for error in errors)

    def test_password_no_digit(self):
        """Test password without digit"""
        password = "NoDigitsHere!"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is False
        assert any("digit" in error for error in errors)

    def test_password_no_special(self):
        """Test password without special character"""
        password = "NoSpecial123"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is False
        assert any("special" in error for error in errors)

    def test_common_password(self):
        """Test common password rejection"""
        password = "password123"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is False
        assert any("too common" in error for error in errors)

    def test_all_requirements_met(self):
        """Test password meeting all requirements"""
        password = "MyS3cure@P@ssw0rd"
        is_valid, errors = validate_password_strength(password)

        assert is_valid is True
        assert len(errors) == 0


class TestPasswordExpiration:
    """Test password expiration checking"""

    def test_password_not_expired(self):
        """Test recently changed password is not expired"""
        password_changed_at = datetime.utcnow() - timedelta(days=30)

        assert is_password_expired(password_changed_at) is False

    def test_password_expired(self):
        """Test old password is expired"""
        password_changed_at = datetime.utcnow() - timedelta(days=100)

        assert is_password_expired(password_changed_at) is True

    def test_password_never_changed(self):
        """Test password that was never changed is considered expired"""
        assert is_password_expired(None) is True

    def test_custom_expiration_days(self):
        """Test custom expiration period"""
        password_changed_at = datetime.utcnow() - timedelta(days=60)

        # Default 90 days
        assert is_password_expired(password_changed_at) is False

        # Custom 30 days
        assert is_password_expired(password_changed_at, max_days=30) is True

    def test_exactly_at_limit(self):
        """Test password exactly at expiration limit"""
        password_changed_at = datetime.utcnow() - timedelta(days=90)

        # Should be considered expired
        assert is_password_expired(password_changed_at, max_days=90) is True
