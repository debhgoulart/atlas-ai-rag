"""Client for Google Gemini API embedding generation and conversational chat synthesis."""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import AIServiceException


@dataclass
class ChatGenerationResult:
    """Result data container for an LLM response synthesis."""

    content: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]


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
            self._client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(api_version=settings.GEMINI_API_VERSION),
            )
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

        def _call_api() -> List[List[float]]:
            results: List[List[float]] = []
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


class GeminiChatClient:
    """Service client for generating grounded chat answers via Google Gemini Flash."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_CHAT_MODEL
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise AIServiceException(
                    "GEMINI_API_KEY is not configured in environment or .env file.",
                    code="MISSING_GEMINI_API_KEY",
                )
            self._client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(api_version=settings.GEMINI_API_VERSION),
            )
        return self._client

    async def generate_response(
        self,
        system_instruction: str,
        contents: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> ChatGenerationResult:
        """Synthesize an answer using Google Gemini."""
        # Testing fallback if no API key is provided
        if not self.api_key:
            return ChatGenerationResult(
                content="[Modo de Teste] Resposta simulada fundamentada no contexto fornecido.",
                prompt_tokens=100,
                completion_tokens=25,
            )

        client = self._get_client()

        # Build contents structure for the Gemini SDK
        gemini_contents = []
        for msg in contents:
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        )

        def _call_generate() -> ChatGenerationResult:
            response = client.models.generate_content(
                model=self.model,
                contents=gemini_contents,
                config=config,
            )
            usage = response.usage_metadata
            prompt_toks = getattr(usage, "prompt_token_count", None) if usage else None
            cand_toks = getattr(usage, "candidates_token_count", None) if usage else None

            return ChatGenerationResult(
                content=response.text or "",
                prompt_tokens=prompt_toks,
                completion_tokens=cand_toks,
            )

        try:
            return await asyncio.to_thread(_call_generate)
        except Exception as exc:
            raise AIServiceException(
                f"Google Gemini Chat API error: {str(exc)}",
                code="GEMINI_CHAT_ERROR",
            )
