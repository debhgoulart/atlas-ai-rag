"""Unit tests for logging sanitization filter."""

import logging
from app.core.logging import SensitiveDataFilter


def test_sensitive_data_filter_redacts_api_key() -> None:
    """Ensure Gemini API keys are redacted from log messages."""
    filter_instance = SensitiveDataFilter()
    sample_key = "AIzaSyD" + "1" * 32
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg=f"Calling Gemini with key {sample_key} now",
        args=(),
        exc_info=None,
    )

    filter_instance.filter(record)
    assert sample_key not in record.msg
    assert "[REDACTED_GEMINI_KEY]" in record.msg


def test_sensitive_data_filter_redacts_bearer_token() -> None:
    """Ensure JWT Bearer tokens are redacted from log messages."""
    filter_instance = SensitiveDataFilter()
    sample_jwt = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThisSignature"
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=20,
        msg=f"Incoming request authorization: {sample_jwt}",
        args=(),
        exc_info=None,
    )

    filter_instance.filter(record)
    assert sample_jwt not in record.msg
    assert "Bearer [REDACTED_JWT_TOKEN]" in record.msg
