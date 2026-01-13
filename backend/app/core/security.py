from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional, Dict, Any
import hashlib
import secrets
import pyotp
import qrcode
from io import BytesIO
import base64

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(subject: int, claims: Optional[Dict[str, Any]] = None) -> str:
    """Create a JWT access token"""
    payload = {
        "sub": str(subject),
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }

    if claims:
        payload.update(claims)

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: int) -> str:
    """Create a JWT refresh token"""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject),
        "type": "refresh",
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.JWTError:
        return None


def hash_token(token: str) -> str:
    """Hash a token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify a token against its hash"""
    return hash_token(token) == token_hash


def generate_mfa_secret() -> str:
    """Generate a new MFA secret key"""
    return pyotp.random_base32()


def generate_mfa_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes for MFA"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def get_mfa_totp_uri(secret: str, username: str, issuer: str = "SIMRS") -> str:
    """Generate the TOTP URI for QR code generation"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=username,
        issuer_name=issuer
    )


def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify a TOTP code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 1 step window for clock drift


def generate_qr_code(data: str) -> str:
    """Generate a QR code as base64 encoded image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength according to security policy
    Returns: (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 12:
        errors.append("Password must be at least 12 characters long")

    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit")

    if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
        errors.append("Password must contain at least one special character")

    # Check for common passwords
    common_passwords = [
        "password", "123456789", "qwerty123", "abc123456",
        "password123", "admin123", "letmein123"
    ]
    if password.lower() in common_passwords:
        errors.append("Password is too common")

    return len(errors) == 0, errors


def is_password_expired(password_changed_at: Optional[datetime], max_days: int = 90) -> bool:
    """Check if password has expired based on policy"""
    if not password_changed_at:
        return True

    expiration_date = password_changed_at + timedelta(days=max_days)
    return datetime.utcnow() > expiration_date
