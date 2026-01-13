"""
Backup module for SIMRS automated backup system.

Provides encryption, compression, and validation for database backups.
Uses AES-256-GCM encryption for secure backup storage.
"""

import os
import gzip
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

logger = logging.getLogger(__name__)


class BackupEncryptionError(Exception):
    """Raised when backup encryption/decryption fails."""
    pass


class BackupValidationError(Exception):
    """Raised when backup validation fails."""
    pass


class BackupManager:
    """
    Manages backup encryption, compression, and validation.

    Uses AES-256-GCM for authenticated encryption.
    Compresses backups using gzip.
    Validates backups using SHA-256 checksums.
    """

    def __init__(
        self,
        encryption_key: Optional[str] = None,
        compression_level: int = 6
    ):
        """
        Initialize backup manager.

        Args:
            encryption_key: 32-byte hex string for AES-256. If None, reads from env.
            compression_level: gzip compression level (0-9, default 6)
        """
        self.encryption_key = encryption_key or os.getenv("BACKUP_ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError(
                "BACKUP_ENCRYPTION_KEY must be set in environment or passed as parameter"
            )

        # Validate and convert key
        try:
            self.key_bytes = bytes.fromhex(self.encryption_key)
            if len(self.key_bytes) != 32:
                raise ValueError(
                    f"Encryption key must be 32 bytes (64 hex chars), got {len(self.key_bytes)}"
                )
        except ValueError as e:
            raise ValueError(
                f"Invalid encryption key format: {e}. Must be 64-character hex string."
            )

        self.compression_level = compression_level

    def encrypt_backup(
        self,
        data: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Encrypt backup data using AES-256-GCM.

        Args:
            data: Raw backup data to encrypt
            associated_data: Optional additional authenticated data

        Returns:
            Encrypted data with nonce prepended (12 bytes nonce + ciphertext + tag)
        """
        try:
            # Generate random nonce (96 bits for GCM)
            nonce = os.urandom(12)

            # Create AES-GCM cipher
            aesgcm = AESGCM(self.key_bytes)

            # Encrypt with authenticated encryption
            ciphertext = aesgcm.encrypt(nonce, data, associated_data)

            # Return nonce + ciphertext (nonce needed for decryption)
            return nonce + ciphertext

        except Exception as e:
            logger.error(f"Backup encryption failed: {e}")
            raise BackupEncryptionError(f"Failed to encrypt backup: {e}")

    def decrypt_backup(
        self,
        encrypted_data: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt backup data using AES-256-GCM.

        Args:
            encrypted_data: Encrypted data with nonce prepended
            associated_data: Optional additional authenticated data

        Returns:
            Decrypted backup data
        """
        try:
            # Extract nonce from first 12 bytes
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]

            # Create AES-GCM cipher
            aesgcm = AESGCM(self.key_bytes)

            # Decrypt and verify authentication tag
            plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)

            return plaintext

        except Exception as e:
            logger.error(f"Backup decryption failed: {e}")
            raise BackupEncryptionError(f"Failed to decrypt backup: {e}")

    def compress_backup(self, data: bytes) -> bytes:
        """
        Compress backup data using gzip.

        Args:
            data: Raw backup data

        Returns:
            Compressed data
        """
        try:
            return gzip.compress(data, compresslevel=self.compression_level)
        except Exception as e:
            logger.error(f"Backup compression failed: {e}")
            raise BackupEncryptionError(f"Failed to compress backup: {e}")

    def decompress_backup(self, compressed_data: bytes) -> bytes:
        """
        Decompress backup data using gzip.

        Args:
            compressed_data: Compressed backup data

        Returns:
            Decompressed data
        """
        try:
            return gzip.decompress(compressed_data)
        except Exception as e:
            logger.error(f"Backup decompression failed: {e}")
            raise BackupEncryptionError(f"Failed to decompress backup: {e}")

    def calculate_checksum(self, data: bytes) -> str:
        """
        Calculate SHA-256 checksum of data.

        Args:
            data: Data to checksum

        Returns:
            Hexadecimal SHA-256 checksum
        """
        return hashlib.sha256(data).hexdigest()

    def create_backup(
        self,
        data: bytes,
        compress: bool = True,
        encrypt: bool = True
    ) -> Tuple[bytes, str]:
        """
        Create a backup with optional compression and encryption.

        Args:
            data: Raw backup data
            compress: Whether to compress with gzip
            encrypt: Whether to encrypt with AES-256-GCM

        Returns:
            Tuple of (backup_bytes, checksum)

        Raises:
            BackupEncryptionError: If compression or encryption fails
        """
        backup_data = data

        # Step 1: Compress if requested
        if compress:
            backup_data = self.compress_backup(backup_data)
            logger.debug(f"Compressed backup: {len(data)} -> {len(backup_data)} bytes")

        # Step 2: Encrypt if requested
        if encrypt:
            backup_data = self.encrypt_backup(backup_data)
            logger.debug(f"Encrypted backup: {len(data)} -> {len(backup_data)} bytes")

        # Step 3: Calculate checksum of final backup
        checksum = self.calculate_checksum(backup_data)
        logger.info(f"Created backup with checksum: {checksum[:16]}...")

        return backup_data, checksum

    def validate_backup(
        self,
        backup_data: bytes,
        expected_checksum: str,
        encrypted: bool = True,
        compressed: bool = True
    ) -> bool:
        """
        Validate backup integrity using checksum.

        Args:
            backup_data: Backup data to validate
            expected_checksum: Expected SHA-256 checksum
            encrypted: Whether backup is encrypted
            compressed: Whether backup is compressed

        Returns:
            True if validation passes

        Raises:
            BackupValidationError: If validation fails
        """
        # Calculate actual checksum
        actual_checksum = self.calculate_checksum(backup_data)

        if actual_checksum != expected_checksum:
            error_msg = (
                f"Checksum mismatch: expected {expected_checksum}, "
                f"got {actual_checksum}"
            )
            logger.error(error_msg)
            raise BackupValidationError(error_msg)

        # Try to decrypt and decompress to ensure data is valid
        try:
            data = backup_data

            if encrypted:
                data = self.decrypt_backup(data)
                logger.debug("Decryption successful during validation")

            if compressed:
                data = self.decompress_backup(data)
                logger.debug("Decompression successful during validation")

            logger.info(f"Backup validation passed ({len(data)} bytes of data)")
            return True

        except Exception as e:
            error_msg = f"Backup validation failed: {e}"
            logger.error(error_msg)
            raise BackupValidationError(error_msg)

    def restore_backup(
        self,
        backup_data: bytes,
        encrypted: bool = True,
        compressed: bool = True
    ) -> bytes:
        """
        Restore backup data (decrypt and decompress).

        Args:
            backup_data: Backup data to restore
            encrypted: Whether backup is encrypted
            compressed: Whether backup is compressed

        Returns:
            Restored raw data
        """
        data = backup_data

        if encrypted:
            data = self.decrypt_backup(data)
            logger.debug("Decrypted backup data")

        if compressed:
            data = self.decompress_backup(data)
            logger.debug("Decompressed backup data")

        logger.info(f"Restored backup ({len(data)} bytes)")
        return data


def generate_encryption_key() -> str:
    """
    Generate a new random encryption key for backups.

    Returns:
        64-character hex string (32 bytes) for AES-256

    Example:
        >>> key = generate_encryption_key()
        >>> print(f"BACKUP_ENCRYPTION_KEY={key}")
    """
    key = os.urandom(32)
    return key.hex()


def main():
    """CLI for generating backup encryption keys."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate encryption key for backup system"
    )
    parser.add_argument(
        "--output",
        help="Output file for the key (default: stdout)"
    )

    args = parser.parse_args()

    key = generate_encryption_key()

    output_line = f"BACKUP_ENCRYPTION_KEY={key}\n"
    output_line += f"\nAdd this to your .env file or environment variables.\n"
    output_line += f"WARNING: Keep this key secure! Losing it means losing all backups.\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_line)
        print(f"Encryption key written to {args.output}")
    else:
        print(output_line)


if __name__ == "__main__":
    main()
