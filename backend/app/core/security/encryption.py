"""Symmetric encryption service using Fernet (AES-128-CBC + HMAC-SHA256).

Ensures secure, authenticated encryption for storing sensitive user API keys.
"""

from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings


class EncryptionException(Exception):
    """Base exception for encryption and decryption errors."""

    def __init__(self, message: str, code: str = "ENCRYPTION_ERROR") -> None:
        super().__init__(message)
        self.code = code


class EncryptionService:
    """Service handling symmetric encryption and decryption of secrets."""

    def __init__(self, master_key: Optional[str] = None) -> None:
        key = master_key or settings.CREDENTIALS_ENCRYPTION_KEY
        if not key:
            # If not configured, provide a deterministic warning or fallback in development
            raise EncryptionException(
                "Master encryption key (CREDENTIALS_ENCRYPTION_KEY) is not configured.",
                code="MISSING_ENCRYPTION_KEY",
            )
        try:
            self._fernet = Fernet(key.encode("utf-8") if isinstance(key, str) else key)
        except Exception as exc:
            raise EncryptionException(
                f"Invalid CREDENTIALS_ENCRYPTION_KEY format: {str(exc)}",
                code="INVALID_ENCRYPTION_KEY",
            )

    @classmethod
    def generate_key(cls) -> str:
        """Generate a cryptographically secure 32-byte base64-encoded Fernet key."""
        return Fernet.generate_key().decode("utf-8")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string and return base64 encoded token with version prefix."""
        if not plaintext:
            raise EncryptionException("Cannot encrypt empty or null plaintext.", code="EMPTY_PLAINTEXT")
        try:
            token_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))
            return f"v1:{token_bytes.decode('utf-8')}"
        except Exception as exc:
            raise EncryptionException(
                "Failed to encrypt secret payload.",
                code="ENCRYPTION_FAILED",
            )

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt token and return original plaintext string."""
        if not ciphertext:
            raise EncryptionException("Cannot decrypt empty or null ciphertext.", code="EMPTY_CIPHERTEXT")

        # Strip version prefix if present
        raw_token = ciphertext
        if ciphertext.startswith("v1:"):
            raw_token = ciphertext[3:]

        try:
            decrypted_bytes = self._fernet.decrypt(raw_token.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            raise EncryptionException(
                "Decryption failed: invalid token, tampered data, or mismatched encryption key.",
                code="DECRYPTION_FAILED",
            )
        except Exception:
            raise EncryptionException(
                "Unexpected failure during decryption.",
                code="DECRYPTION_ERROR",
            )
