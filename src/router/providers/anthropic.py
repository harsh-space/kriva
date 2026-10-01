"""Step 3: cloud provider via the Anthropic Messages API (plain HTTP)."""
import os
import time

import httpx

from .base import ModelProvider, Result


class AnthropicProvider(ModelProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.model = model
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")

    async def generate(self, prompt, context="", tools=None) -> Result:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        content = f"{context}\n\n{prompt}" if context else prompt
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": content}],
                },
            )
            r.raise_for_status()
        data = r.json()
        return Result(
            text=data["content"][0]["text"],
            provider=self.name,
            model=self.model,
            tokens_in=data["usage"]["input_tokens"],
            tokens_out=data["usage"]["output_tokens"],
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.api_key)
