"""
Test encryption functionality for audit logs.

This test suite verifies:
- Encryption and decryption of various data types
- Backward compatibility with non-encrypted data
- Error handling for invalid keys
"""
import json
import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.encryption import (
    generate_key,
    encrypt_field,
    decrypt_field,
    is_encrypted,
    EncryptionError
)


class TestEncryption:
    """Test suite for encryption utilities."""

    def test_generate_key(self):
        """Test that generate_key produces a valid Fernet key."""
        key = generate_key()

        assert key is not None
        assert isinstance(key, str)
        assert len(key) == 44  # Fernet keys are 44 characters (base64)

    def test_encrypt_decrypt_string(self):
        """Test basic string encryption and decryption."""
        # Set up environment with a test key
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        plaintext = "This is a test string"
        ciphertext = encrypt_field(plaintext)
        decrypted = decrypt_field(ciphertext)

        assert ciphertext != plaintext
        assert decrypted == plaintext
        assert is_encrypted(ciphertext) is True

    def test_encrypt_decrypt_json(self):
        """Test encryption and decryption of JSON data."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        data = {
            "user_id": 123,
            "username": "testuser",
            "action": "CREATE",
            "resource": "Patient"
        }
        plaintext = json.dumps(data)
        ciphertext = encrypt_field(plaintext)
        decrypted = decrypt_field(ciphertext)

        decrypted_data = json.loads(decrypted)
        assert decrypted_data == data

    def test_encrypt_decrypt_special_characters(self):
        """Test encryption and decryption with special characters."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        test_cases = [
            "String with émojis 🎉 🔐",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Newlines\nand\ttabs\r\n",
            "Unicode: 你好世界 مرحبا بالعالم Привет мир",
            "SQL: SELECT * FROM users WHERE id = 1; DROP TABLE users; --",
        ]

        for plaintext in test_cases:
            ciphertext = encrypt_field(plaintext)
            decrypted = decrypt_field(ciphertext)
            assert decrypted == plaintext, f"Failed for: {plaintext}"

    def test_encrypt_decrypt_empty_string(self):
        """Test encryption and decryption of empty string."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        plaintext = ""
        ciphertext = encrypt_field(plaintext)
        decrypted = decrypt_field(ciphertext)

        assert decrypted == plaintext

    def test_encrypt_decrypt_none(self):
        """Test encryption and decryption of None values."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        ciphertext = encrypt_field(None)
        decrypted = decrypt_field(None)

        assert ciphertext is None
        assert decrypted is None

    def test_backward_compatibility_non_encrypted(self):
        """Test that non-encrypted data is returned as-is (backward compatibility)."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        # Simulate existing non-encrypted data
        existing_data = "This is existing non-encrypted data"

        # Should return as-is since it's not encrypted
        decrypted = decrypt_field(existing_data)
        assert decrypted == existing_data

    def test_is_encrypted(self):
        """Test the is_encrypted utility function."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        plaintext = "Test data"
        ciphertext = encrypt_field(plaintext)

        assert is_encrypted(ciphertext) is True
        assert is_encrypted(plaintext) is False
        assert is_encrypted("") is False
        assert is_encrypted(None) is False

    def test_encrypt_decrypt_large_data(self):
        """Test encryption and decryption of large data."""
        test_key = generate_key()
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = test_key

        # Create a large JSON payload
        large_data = {
            "records": [
                {
                    "id": i,
                    "data": "x" * 1000,
                    "nested": {
                        "field1": "value1" * 10,
                        "field2": "value2" * 10
                    }
                }
                for i in range(100)
            ]
        }
        plaintext = json.dumps(large_data)
        ciphertext = encrypt_field(plaintext)
        decrypted = decrypt_field(ciphertext)

        decrypted_data = json.loads(decrypted)
        assert decrypted_data == large_data

    def test_invalid_key_raises_error(self):
        """Test that invalid encryption key raises EncryptionError."""
        # Use an invalid key
        os.environ['AUDIT_LOG_ENCRYPTION_KEY'] = "invalid_key"

        with pytest.raises(EncryptionError):
            encrypt_field("test data")

    def test_missing_key_raises_error(self):
        """Test that missing encryption key raises EncryptionError."""
        # Remove the key from environment
        os.environ.pop('AUDIT_LOG_ENCRYPTION_KEY', None)

        with pytest.raises(EncryptionError):
            encrypt_field("test data")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
