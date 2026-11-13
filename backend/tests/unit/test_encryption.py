"""Unit tests for EncryptionService."""

import pytest
from app.core.security.encryption import EncryptionException, EncryptionService


def test_encryption_and_decryption_roundtrip() -> None:
    """Ensure plaintext can be encrypted and accurately decrypted."""
    key = EncryptionService.generate_key()
    service = EncryptionService(master_key=key)

    secret = "AIzaSySecretApiKey123456789"
    ciphertext = service.encrypt(secret)

    assert ciphertext.startswith("v1:")
    assert secret not in ciphertext

    decrypted = service.decrypt(ciphertext)
    assert decrypted == secret


def test_encryption_rejects_empty_string() -> None:
    """Ensure empty plaintext raises EncryptionException."""
    key = EncryptionService.generate_key()
    service = EncryptionService(master_key=key)

    with pytest.raises(EncryptionException) as exc_info:
        service.encrypt("")
    assert exc_info.value.code == "EMPTY_PLAINTEXT"


def test_decryption_fails_with_tampered_ciphertext() -> None:
    """Ensure tampered ciphertext triggers decryption failure without leaking raw data."""
    key = EncryptionService.generate_key()
    service = EncryptionService(master_key=key)

    secret = "AIzaSySecretApiKey123456789"
    ciphertext = service.encrypt(secret)

    # Tamper with the ciphertext token
    tampered = ciphertext[:-4] + "AAAA"

    with pytest.raises(EncryptionException) as exc_info:
        service.decrypt(tampered)
    assert exc_info.value.code == "DECRYPTION_FAILED"


def test_decryption_fails_with_different_key() -> None:
    """Ensure decryption with a different key fails safely."""
    key1 = EncryptionService.generate_key()
    key2 = EncryptionService.generate_key()

    service1 = EncryptionService(master_key=key1)
    service2 = EncryptionService(master_key=key2)

    ciphertext = service1.encrypt("MyTopSecretApiKey")

    with pytest.raises(EncryptionException) as exc_info:
        service2.decrypt(ciphertext)
    assert exc_info.value.code == "DECRYPTION_FAILED"


def test_missing_or_invalid_master_key() -> None:
    """Ensure invalid key format raises EncryptionException."""
    with pytest.raises(EncryptionException) as exc_info:
        EncryptionService(master_key="invalid-not-base64-key")
    assert exc_info.value.code == "INVALID_ENCRYPTION_KEY"
