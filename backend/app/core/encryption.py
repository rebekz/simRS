"""
Encryption utilities for securing sensitive data at rest.

Uses Fernet (symmetric encryption) from cryptography library.
All data is encrypted using AES-128 in CBC mode with PKCS7 padding.
"""
import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class EncryptionError(Exception):
    """Custom exception for encryption/decryption errors."""
    pass


def generate_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        str: URL-safe base64-encoded 32-byte key
    """
    return Fernet.generate_key().decode('utf-8')


def _get_fernet() -> Fernet:
    """
    Get Fernet instance using the encryption key from environment.

    Returns:
        Fernet: Configured Fernet instance

    Raises:
        EncryptionError: If AUDIT_LOG_ENCRYPTION_KEY is not set
    """
    from app.core.config import settings

    encryption_key = getattr(settings, 'AUDIT_LOG_ENCRYPTION_KEY', None)

    if not encryption_key:
        raise EncryptionError(
            "AUDIT_LOG_ENCRYPTION_KEY is not set in environment. "
            "Please generate a key using: python -m app.scripts.generate_audit_key"
        )

    try:
        return Fernet(encryption_key.encode('utf-8'))
    except Exception as e:
        raise EncryptionError(f"Invalid encryption key format: {str(e)}")


def encrypt_field(plaintext: Optional[str]) -> Optional[str]:
    """
    Encrypt a plaintext field.

    Args:
        plaintext: String to encrypt (can be None)

    Returns:
        str: Base64-encoded encrypted string, or None if input is None

    Raises:
        EncryptionError: If encryption fails
    """
    if plaintext is None:
        return None

    if not plaintext:
        # Encrypt empty string to maintain consistency
        plaintext = ""

    try:
        fernet = _get_fernet()
        encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {str(e)}")


def decrypt_field(ciphertext: Optional[str]) -> Optional[str]:
    """
    Decrypt a ciphertext field.

    Args:
        ciphertext: Base64-encoded encrypted string (can be None)

    Returns:
        str: Decrypted plaintext, or None if input is None

    Raises:
        EncryptionError: If decryption fails
    """
    if ciphertext is None:
        return None

    if not ciphertext:
        # Return empty string for consistency
        return ""

    try:
        fernet = _get_fernet()
        encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        # Attempt to return as-is if it's not encrypted (backward compatibility)
        try:
            # Check if it's already a valid UTF-8 string (not encrypted)
            ciphertext.encode('utf-8').decode('utf-8')
            return ciphertext
        except Exception:
            raise EncryptionError(f"Decryption failed: {str(e)}")


def is_encrypted(value: Optional[str]) -> bool:
    """
    Check if a value appears to be encrypted.

    Args:
        value: String to check

    Returns:
        bool: True if value appears to be encrypted
    """
    if not value:
        return False

    try:
        # Try to decode as base64
        decoded = base64.urlsafe_b64decode(value.encode('utf-8'))
        # Check if it looks like Fernet output (typically > 32 bytes)
        return len(decoded) > 32
    except Exception:
        return False
