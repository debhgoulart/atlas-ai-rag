"""Unit tests for Gemini API Key validation logic."""

from unittest.mock import MagicMock, patch
import pytest
from app.services.gemini_credential_service import GeminiCredentialService


def test_validate_gemini_key_success() -> None:
    """Ensure key is considered valid when models.get succeeds."""
    service = GeminiCredentialService()

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.models.get.return_value = MagicMock(name="gemini-2.5-flash")
        mock_client_cls.return_value = mock_instance

        is_valid = service.validate_key_with_gemini("AIzaSyValidCandidateKey123")
        assert is_valid is True
        mock_instance.models.get.assert_called_once()


def test_validate_gemini_key_failure() -> None:
    """Ensure key is considered invalid when models.get raises an API error."""
    service = GeminiCredentialService()

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.models.get.side_effect = Exception("API key not valid. Please pass a valid API key.")
        mock_client_cls.return_value = mock_instance

        is_valid = service.validate_key_with_gemini("AIzaSyInvalidCandidateKey999")
        assert is_valid is False
