"""Recursive character text chunker preserving semantic boundaries."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TextChunk:
    """Represents a text slice with sequence index and character boundaries."""

    index: int
    content: str
    char_start: int
    char_end: int


class RecursiveTextChunker:
    """Partitions text into overlapping chunks using a hierarchy of separators.

    Separators are tried in priority order:
    1. Double newline ("\\n\\n") -> Paragraph breaks
    2. Single newline ("\\n") -> Line breaks
    3. Period followed by space (". ") -> Sentence breaks
    4. Space (" ") -> Word breaks
    5. Empty string ("") -> Character-level fallback
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

    def split_text(self, text: str) -> List[TextChunk]:
        """Split raw text into structured TextChunk instances with overlap."""
        text = text.strip()
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [TextChunk(index=0, content=text, char_start=0, char_end=len(text))]

        splits = self._split_recursive(text, self.separators)
        chunks = self._merge_splits(splits)
        return chunks

    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using the first separator that appears in text."""
        final_pieces: List[str] = []
        separator = separators[-1]
        new_separators: List[str] = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1 :]
                break

        splits = text.split(separator) if separator else list(text)

        for s in splits:
            if not s:
                continue
            if len(s) <= self.chunk_size:
                final_pieces.append(s)
            else:
                if new_separators:
                    sub_pieces = self._split_recursive(s, new_separators)
                    final_pieces.extend(sub_pieces)
                else:
                    # Forced character splitting when no separators remain
                    for j in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        final_pieces.append(s[j : j + self.chunk_size])

        return final_pieces

    def _merge_splits(self, splits: List[str]) -> List[TextChunk]:
        """Merge smaller splits into chunks matching chunk_size with overlap."""
        chunks: List[TextChunk] = []
        current_doc: List[str] = []
        total_len = 0
        char_cursor = 0
        chunk_index = 0

        for split in splits:
            split_len = len(split)
            if total_len + split_len > self.chunk_size and current_doc:
                merged_content = " ".join(current_doc).strip()
                if merged_content:
                    chunks.append(
                        TextChunk(
                            index=chunk_index,
                            content=merged_content,
                            char_start=char_cursor,
                            char_end=char_cursor + len(merged_content),
                        )
                    )
                    chunk_index += 1

                # Retain overlap from end of current_doc
                while total_len > self.chunk_overlap and len(current_doc) > 1:
                    popped = current_doc.pop(0)
                    total_len -= len(popped) + 1
                    char_cursor += len(popped) + 1

            current_doc.append(split)
            total_len += split_len + 1

        if current_doc:
            merged_content = " ".join(current_doc).strip()
            if merged_content:
                chunks.append(
                    TextChunk(
                        index=chunk_index,
                        content=merged_content,
                        char_start=char_cursor,
                        char_end=char_cursor + len(merged_content),
                    )
                )

        return chunks
