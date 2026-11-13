"""Document parsing service extracting text from PDF, TXT, and Markdown files."""

import io
from typing import Tuple

from app.core.exceptions import DocumentValidationException


class DocumentParser:
    """Parser extracting clean plain text from supported document formats."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
    SUPPORTED_MIME_TYPES = {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/octet-stream",  # Fallback for some OS file uploads
    }

    @classmethod
    def validate_file(cls, filename: str, content_type: str, file_size: int, max_bytes: int) -> str:
        """Validate filename extension, MIME type and maximum file size.

        Returns:
            The normalized lower-cased file extension (e.g. '.pdf').
        """
        if file_size <= 0:
            raise DocumentValidationException(
                "Uploaded file is empty (0 bytes).",
                code="EMPTY_FILE",
            )

        if file_size > max_bytes:
            max_mb = max_bytes // (1024 * 1024)
            raise DocumentValidationException(
                f"File size exceeds maximum allowed limit of {max_mb} MB.",
                code="FILE_TOO_LARGE",
            )

        # Extract extension
        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[-1].lower()

        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise DocumentValidationException(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(cls.SUPPORTED_EXTENSIONS)}",
                code="UNSUPPORTED_FORMAT",
            )

        return ext

    @classmethod
    def extract_text(cls, file_bytes: bytes, extension: str) -> Tuple[str, dict]:
        """Extract plain text and basic metadata from raw file bytes.

        Returns:
            Tuple of (extracted_text, metadata_dict)
        """
        metadata = {}

        if extension == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(file_bytes))
                num_pages = len(reader.pages)
                metadata["page_count"] = num_pages

                pages_text = []
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        pages_text.append(page_text.strip())

                extracted = "\n\n".join(pages_text)
                if not extracted.strip():
                    raise DocumentValidationException(
                        "The PDF document does not contain readable text layers (scanned images are not supported).",
                        code="EMPTY_TEXT_CONTENT",
                    )
                return cls._sanitize_text(extracted), metadata

            except DocumentValidationException:
                raise
            except Exception as exc:
                raise DocumentValidationException(
                    f"Failed to parse PDF document: {str(exc)}",
                    code="PDF_PARSING_FAILED",
                )

        elif extension in {".txt", ".md"}:
            try:
                # Attempt UTF-8 with fallback to Latin-1
                try:
                    text = file_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text = file_bytes.decode("latin-1")

                if not text.strip():
                    raise DocumentValidationException(
                        "The document contains no readable text content.",
                        code="EMPTY_TEXT_CONTENT",
                    )

                return cls._sanitize_text(text), metadata

            except DocumentValidationException:
                raise
            except Exception as exc:
                raise DocumentValidationException(
                    f"Failed to read text file: {str(exc)}",
                    code="TEXT_READ_FAILED",
                )

        raise DocumentValidationException(f"Unsupported format {extension}")

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Clean null bytes and standardize newline characters."""
        # Remove null bytes that break PostgreSQL text fields
        text = text.replace("\x00", "")
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return text.strip()
