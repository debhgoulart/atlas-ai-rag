"""Client for Google Gemini API embedding generation."""

import asyncio
from typing import List, Optional
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import AIServiceException


class GeminiEmbeddingClient:
    """Service client generating dense semantic embeddings via Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        """Lazily initialize and return the official Google GenAI client."""
        if self._client is None:
            if not self.api_key:
                raise AIServiceException(
                    "GEMINI_API_KEY is not configured in environment or .env file.",
                    code="MISSING_GEMINI_API_KEY",
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate vector embedding for a single text string."""
        embeddings = await self.generate_embeddings_batch([text], task_type=task_type)
        if not embeddings:
            raise AIServiceException("Empty embedding vector returned from Gemini API.")
        return embeddings[0]

    async def generate_embeddings_batch(
        self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[List[float]]:
        """Generate embeddings for multiple text passages concurrently or in batches."""
        if not texts:
            return []

        # If testing without an API key, provide a deterministic mock fallback
        if not self.api_key:
            return [[0.0] * self.dimension for _ in texts]

        client = self._get_client()

        # Run embedding call in an async executor thread to maintain non-blocking I/O
        def _call_api() -> List[List[float]]:
            results: List[List[float]] = []
            # Process in sub-batches of 50 to respect API limits
            batch_size = 50
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        output_dimensionality=self.dimension,
                    ),
                )
                for emb in response.embeddings:
                    results.append(emb.values)
            return results

        try:
            return await asyncio.to_thread(_call_api)
        except Exception as exc:
            raise AIServiceException(
                f"Google Gemini Embedding API error: {str(exc)}",
                code="GEMINI_API_ERROR",
            )
