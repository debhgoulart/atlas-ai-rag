"""Logging configuration and sensitive credentials redaction filter."""

import logging
import re

# Regex matching Google API Keys (e.g. AIzaSy...) and JWT Bearer tokens
GEMINI_KEY_REGEX = re.compile(r"AIza[0-9A-Za-z-_]{35}")
BEARER_TOKEN_REGEX = re.compile(r"Bearer\s+eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+")


class SensitiveDataFilter(logging.Filter):
    """Logging filter that scrubs sensitive API keys and authorization tokens from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact(v) if isinstance(v, str) else v for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact(v) if isinstance(v, str) else v for v in record.args)
        return True

    @staticmethod
    def redact(text: str) -> str:
        """Replace sensitive patterns with a safe redaction placeholder."""
        redacted = GEMINI_KEY_REGEX.sub("[REDACTED_GEMINI_KEY]", text)
        redacted = BEARER_TOKEN_REGEX.sub("Bearer [REDACTED_JWT_TOKEN]", redacted)
        return redacted


def setup_secure_logging() -> None:
    """Attach SensitiveDataFilter to root logger to ensure zero credential leakage."""
    root_logger = logging.getLogger()
    sensitive_filter = SensitiveDataFilter()
    root_logger.addFilter(sensitive_filter)
    for handler in root_logger.handlers:
        handler.addFilter(sensitive_filter)
