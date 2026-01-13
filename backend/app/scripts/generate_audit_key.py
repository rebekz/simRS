#!/usr/bin/env python3
"""
Generate a new Fernet encryption key for audit log encryption.

This script generates a cryptographically secure key for encrypting
sensitive audit log data at rest.

Usage:
    python -m app.scripts.generate_audit_key

Output:
    A new encryption key that should be stored in the AUDIT_LOG_ENCRYPTION_KEY
    environment variable.

IMPORTANT:
    - Store the generated key securely in your environment configuration
    - Do NOT commit the key to version control
    - Keep a backup of the key in a secure location
    - If the key is lost, encrypted audit logs cannot be decrypted
"""
import secrets
import sys
import os

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("Error: cryptography library is not installed.")
    print("Install it with: pip install cryptography==41.0.7")
    sys.exit(1)


def generate_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        str: URL-safe base64-encoded 32-byte key
    """
    return Fernet.generate_key().decode('utf-8')


def main():
    """Main function to generate and display the encryption key."""
    print("=" * 70)
    print("Audit Log Encryption Key Generator")
    print("=" * 70)
    print()

    # Generate the key
    key = generate_key()

    print("Your new encryption key has been generated:")
    print()
    print("-" * 70)
    print(key)
    print("-" * 70)
    print()

    print("IMPORTANT INSTRUCTIONS:")
    print()
    print("1. Add this key to your environment variables:")
    print(f"   AUDIT_LOG_ENCRYPTION_KEY={key}")
    print()
    print("2. Add to your .env file:")
    print(f"   AUDIT_LOG_ENCRYPTION_KEY={key}")
    print()
    print("3. Store this key securely:")
    print("   - DO NOT commit to version control")
    print("   - Keep a secure backup")
    print("   - Use different keys for development, staging, and production")
    print("   - Rotate keys periodically (recommended: annually)")
    print()
    print("4. If you lose this key, encrypted audit logs CANNOT be recovered.")
    print()
    print("=" * 70)
    print()

    return key


if __name__ == "__main__":
    main()
