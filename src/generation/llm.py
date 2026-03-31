"""LLM handler for text generation via Ollama."""

from __future__ import annotations

import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434/v1"


class LLMHandler:
    """Generates text using a local Ollama model.

    Args:
        model: Ollama model name.
        temperature: Sampling temperature (0.0 = deterministic).
        max_tokens: Maximum tokens in the response.
    """

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        temperature: float = 0.0,
        max_tokens: int = 2000,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    def generate(self, prompt: str, temperature: float | None = None) -> str:
        """Send a prompt and return the model's response as a string.

        Args:
            prompt: The full prompt text to send.
            temperature: Override instance temperature for this call.

        Returns:
            The generated text response.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=self.max_tokens,
        )
        result = response.choices[0].message.content
        logger.info("Generated %d chars with %s", len(result), self.model)
        return result
