"""
Unit tests for backup module.

Tests backup encryption, decryption, compression, and validation.
"""

import os
import pytest
from backend.app.core.backup import (
    BackupManager,
    BackupEncryptionError,
    BackupValidationError,
    generate_encryption_key
)


class TestBackupEncryption:
    """Test backup encryption and decryption."""

    @pytest.fixture
    def encryption_key(self):
        """Generate a test encryption key."""
        return generate_encryption_key()

    @pytest.fixture
    def backup_manager(self, encryption_key):
        """Create a backup manager with test key."""
        return BackupManager(encryption_key=encryption_key)

    @pytest.fixture
    def sample_data(self):
        """Generate sample backup data."""
        return b"SIMRS database backup content\n" * 1000

    def test_generate_encryption_key(self):
        """Test encryption key generation."""
        key = generate_encryption_key()
        assert len(key) == 64  # 32 bytes = 64 hex chars
        assert all(c in "0123456789abcdef" for c in key)

    def test_backup_manager_init(self, backup_manager):
        """Test backup manager initialization."""
        assert backup_manager.key_bytes is not None
        assert len(backup_manager.key_bytes) == 32

    def test_backup_manager_invalid_key(self):
        """Test backup manager with invalid key."""
        with pytest.raises(ValueError):
            BackupManager(encryption_key="invalid_key")

    def test_backup_manager_short_key(self):
        """Test backup manager with short key."""
        with pytest.raises(ValueError):
            BackupManager(encryption_key="a" * 32)  # Only 16 bytes

    def test_encrypt_decrypt(self, backup_manager, sample_data):
        """Test encryption and decryption."""
        encrypted = backup_manager.encrypt_backup(sample_data)
        assert encrypted != sample_data
        assert len(encrypted) > len(sample_data)  # nonce + ciphertext + tag

        decrypted = backup_manager.decrypt_backup(encrypted)
        assert decrypted == sample_data

    def test_compress_decompress(self, backup_manager, sample_data):
        """Test compression and decompression."""
        compressed = backup_manager.compress_backup(sample_data)
        assert compressed != sample_data
        assert len(compressed) < len(sample_data)

        decompressed = backup_manager.decompress_backup(compressed)
        assert decompressed == sample_data

    def test_calculate_checksum(self, backup_manager, sample_data):
        """Test checksum calculation."""
        checksum1 = backup_manager.calculate_checksum(sample_data)
        checksum2 = backup_manager.calculate_checksum(sample_data)
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA-256 hex length

        # Different data should have different checksum
        different_data = b"different content"
        assert checksum1 != backup_manager.calculate_checksum(different_data)

    def test_create_backup_compressed_encrypted(self, backup_manager, sample_data):
        """Test creating backup with compression and encryption."""
        backup, checksum = backup_manager.create_backup(
            sample_data,
            compress=True,
            encrypt=True
        )

        assert backup != sample_data
        assert len(checksum) == 64
        assert checksum == backup_manager.calculate_checksum(backup)

    def test_create_backup_uncompressed_unencrypted(self, backup_manager, sample_data):
        """Test creating backup without compression or encryption."""
        backup, checksum = backup_manager.create_backup(
            sample_data,
            compress=False,
            encrypt=False
        )

        assert backup == sample_data
        assert checksum == backup_manager.calculate_checksum(backup)

    def test_validate_backup_success(self, backup_manager, sample_data):
        """Test successful backup validation."""
        backup, checksum = backup_manager.create_backup(
            sample_data,
            compress=True,
            encrypt=True
        )

        # Should not raise exception
        backup_manager.validate_backup(
            backup,
            checksum,
            encrypted=True,
            compressed=True
        )

    def test_validate_backup_checksum_mismatch(self, backup_manager, sample_data):
        """Test backup validation with wrong checksum."""
        backup, _ = backup_manager.create_backup(
            sample_data,
            compress=True,
            encrypt=True
        )

        with pytest.raises(BackupValidationError):
            backup_manager.validate_backup(
                backup,
                "wrong_checksum",
                encrypted=True,
                compressed=True
            )

    def test_restore_backup(self, backup_manager, sample_data):
        """Test restoring backup."""
        backup, _ = backup_manager.create_backup(
            sample_data,
            compress=True,
            encrypt=True
        )

        restored = backup_manager.restore_backup(
            backup,
            encrypted=True,
            compressed=True
        )

        assert restored == sample_data

    def test_decrypt_invalid_data(self, backup_manager):
        """Test decryption of invalid data."""
        with pytest.raises(BackupEncryptionError):
            backup_manager.decrypt_backup(b"invalid_encrypted_data")

    def test_decompress_invalid_data(self, backup_manager):
        """Test decompression of invalid data."""
        with pytest.raises(BackupEncryptionError):
            backup_manager.decompress_backup(b"invalid_compressed_data")

    def test_encrypt_with_associated_data(self, backup_manager, sample_data):
        """Test encryption with associated data."""
        aad = b"additional_authenticated_data"
        encrypted = backup_manager.encrypt_backup(sample_data, associated_data=aad)

        # Decryption fails without AAD
        with pytest.raises(BackupEncryptionError):
            backup_manager.decrypt_backup(encrypted, associated_data=None)

        # Decryption succeeds with correct AAD
        decrypted = backup_manager.decrypt_backup(encrypted, associated_data=aad)
        assert decrypted == sample_data

    def test_encryption_different_each_time(self, backup_manager, sample_data):
        """Test that encryption produces different output each time (due to random nonce)."""
        encrypted1 = backup_manager.encrypt_backup(sample_data)
        encrypted2 = backup_manager.encrypt_backup(sample_data)

        # Outputs should be different due to random nonce
        assert encrypted1 != encrypted2

        # But both should decrypt to the same data
        assert backup_manager.decrypt_backup(encrypted1) == sample_data
        assert backup_manager.decrypt_backup(encrypted2) == sample_data

    def test_large_data_handling(self, backup_manager):
        """Test handling of large data (simulate real database dump)."""
        # Create 10 MB of data
        large_data = b"x" * (10 * 1024 * 1024)

        backup, checksum = backup_manager.create_backup(
            large_data,
            compress=True,
            encrypt=True
        )

        # Should compress well
        assert len(backup) < len(large_data)

        # Should restore correctly
        restored = backup_manager.restore_backup(
            backup,
            encrypted=True,
            compressed=True
        )

        assert restored == large_data
