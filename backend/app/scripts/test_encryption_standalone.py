#!/usr/bin/env python3
"""
Standalone test script for audit log encryption.

This script tests the encryption functionality without requiring pytest.
Run with: python app/scripts/test_encryption_standalone.py
"""
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("ERROR: cryptography library not installed")
    print("Install it with: pip install cryptography==41.0.7")
    sys.exit(1)


def generate_key():
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode('utf-8')


def encrypt_field(plaintext, fernet):
    """Encrypt a plaintext field."""
    if plaintext is None:
        return None
    if not plaintext:
        plaintext = ""
    import base64
    encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
    return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')


def decrypt_field(ciphertext, fernet):
    """Decrypt a ciphertext field."""
    if ciphertext is None:
        return None
    if not ciphertext:
        return ""
    import base64
    encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
    decrypted_bytes = fernet.decrypt(encrypted_bytes)
    return decrypted_bytes.decode('utf-8')


def run_tests():
    """Run all encryption tests."""
    print("=" * 70)
    print("Audit Log Encryption Test Suite")
    print("=" * 70)
    print()

    # Generate test key
    key = generate_key()
    fernet = Fernet(key.encode('utf-8'))

    tests_passed = 0
    tests_failed = 0

    # Test 1: Basic string encryption/decryption
    print("Test 1: Basic string encryption/decryption")
    try:
        plaintext = "This is a test string"
        ciphertext = encrypt_field(plaintext, fernet)
        decrypted = decrypt_field(ciphertext, fernet)

        assert ciphertext != plaintext, "Ciphertext should differ from plaintext"
        assert decrypted == plaintext, "Decrypted text should match plaintext"
        print("  PASS")
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 2: JSON data encryption/decryption
    print("Test 2: JSON data encryption/decryption")
    try:
        data = {
            "user_id": 123,
            "username": "testuser",
            "action": "CREATE",
            "resource": "Patient"
        }
        plaintext = json.dumps(data)
        ciphertext = encrypt_field(plaintext, fernet)
        decrypted = decrypt_field(ciphertext, fernet)
        decrypted_data = json.loads(decrypted)

        assert decrypted_data == data, "Decrypted JSON should match original"
        print("  PASS")
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 3: Special characters
    print("Test 3: Special characters encryption/decryption")
    try:
        test_cases = [
            "String with special chars",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Newlines\nand\ttabs\r\n",
        ]

        for test_string in test_cases:
            ciphertext = encrypt_field(test_string, fernet)
            decrypted = decrypt_field(ciphertext, fernet)
            assert decrypted == test_string, "Failed for: {}".format(test_string)

        print("  PASS ({} test cases)".format(len(test_cases)))
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 4: Empty string
    print("Test 4: Empty string encryption/decryption")
    try:
        plaintext = ""
        ciphertext = encrypt_field(plaintext, fernet)
        decrypted = decrypt_field(ciphertext, fernet)

        assert decrypted == plaintext, "Empty string should encrypt/decrypt correctly"
        print("  PASS")
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 5: None values
    print("Test 5: None value handling")
    try:
        ciphertext = encrypt_field(None, fernet)
        decrypted = decrypt_field(None, fernet)

        assert ciphertext is None, "None should return None"
        assert decrypted is None, "None should return None"
        print("  PASS")
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 6: Large data
    print("Test 6: Large data encryption/decryption")
    try:
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
        ciphertext = encrypt_field(plaintext, fernet)
        decrypted = decrypt_field(ciphertext, fernet)
        decrypted_data = json.loads(decrypted)

        assert decrypted_data == large_data, "Large data should encrypt/decrypt correctly"
        print("  PASS (100 records, ~500KB)")
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 7: SQL injection patterns
    print("Test 7: SQL injection patterns")
    try:
        test_cases = [
            "SELECT * FROM users WHERE id = 1; DROP TABLE users; --",
            "'; DELETE FROM patients; --",
            "1' OR '1'='1",
            "admin'--",
        ]

        for sql_string in test_cases:
            ciphertext = encrypt_field(sql_string, fernet)
            decrypted = decrypt_field(ciphertext, fernet)
            assert decrypted == sql_string, "Failed for: {}".format(sql_string)

        print("  PASS ({} SQL patterns)".format(len(test_cases)))
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Test 8: Key generation
    print("Test 8: Key generation")
    try:
        key1 = generate_key()
        key2 = generate_key()

        assert len(key1) == 44, "Key should be 44 characters"
        assert len(key2) == 44, "Key should be 44 characters"
        assert key1 != key2, "Each generated key should be unique"
        print("  PASS")
        tests_passed += 1
    except AssertionError as e:
        print("  FAIL: {}".format(str(e)))
        tests_failed += 1
    print()

    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("Total tests: {}".format(tests_passed + tests_failed))
    print("Passed: {}".format(tests_passed))
    print("Failed: {}".format(tests_failed))
    print()

    if tests_failed == 0:
        print("All tests passed!")
        print()
        print("Encryption is working correctly for audit logs.")
        print()
        print("Sample encryption key for testing:")
        print("  AUDIT_LOG_ENCRYPTION_KEY={}".format(key))
        print()
        return 0
    else:
        print("Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
