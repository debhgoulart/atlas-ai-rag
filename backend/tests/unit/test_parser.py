"""Unit tests for DocumentParser service."""

import pytest
from app.core.exceptions import DocumentValidationException
from app.services.document_parser import DocumentParser


def test_validate_file_valid() -> None:
    """Verify supported extensions and sizes pass validation."""
    ext = DocumentParser.validate_file(
        filename="notes.md",
        content_type="text/markdown",
        file_size=1024,
        max_bytes=10 * 1024 * 1024,
    )
    assert ext == ".md"


def test_validate_file_empty() -> None:
    """Verify empty file raises DocumentValidationException."""
    with pytest.raises(DocumentValidationException) as exc:
        DocumentParser.validate_file(
            filename="empty.txt",
            content_type="text/plain",
            file_size=0,
            max_bytes=10 * 1024 * 1024,
        )
    assert exc.value.code == "EMPTY_FILE"


def test_validate_file_too_large() -> None:
    """Verify oversized file raises DocumentValidationException."""
    with pytest.raises(DocumentValidationException) as exc:
        DocumentParser.validate_file(
            filename="large.pdf",
            content_type="application/pdf",
            file_size=20 * 1024 * 1024,
            max_bytes=10 * 1024 * 1024,
        )
    assert exc.value.code == "FILE_TOO_LARGE"


def test_validate_file_unsupported_format() -> None:
    """Verify unsupported formats (e.g. .exe) are rejected."""
    with pytest.raises(DocumentValidationException) as exc:
        DocumentParser.validate_file(
            filename="program.exe",
            content_type="application/octet-stream",
            file_size=500,
            max_bytes=10 * 1024 * 1024,
        )
    assert exc.value.code == "UNSUPPORTED_FORMAT"


def test_extract_text_markdown() -> None:
    """Verify extracting text from Markdown string."""
    raw_md = b"# Title\n\nThis is paragraph one.\n\nThis is paragraph two."
    text, meta = DocumentParser.extract_text(raw_md, ".md")
    assert "Title" in text
    assert "paragraph one" in text
    assert "paragraph two" in text
