"""NVIDIA-hosted models via the NVIDIA NIM OpenAI-compatible API."""
import os
import time

import httpx

from .base import ModelProvider, Result


class NvidiaProvider(ModelProvider):
    name = "nvidia"

    def __init__(
        self,
        model: str = "nvidia/nemotron-3-ultra-550b-a55b",
        base_url: str = "https://integrate.api.nvidia.com/v1",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("NVIDIA_API_KEY")

    async def generate(self, prompt, context="", tools=None) -> Result:
        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY is not set")
        content = f"{context}\n\n{prompt}" if context else prompt
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": content}],
                },
            )
            response.raise_for_status()
        data = response.json()
        usage = data.get("usage", {})
        return Result(
            text=data["choices"][0]["message"]["content"],
            provider=self.name,
            model=self.model,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.api_key)
