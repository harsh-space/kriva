"""Step 2: local models via Ollama's HTTP server (default port 11434)."""
import time

import httpx

from .base import ModelProvider, Result


class OllamaProvider(ModelProvider):
    name = "ollama"

    def __init__(self, model: str = "qwen2.5-coder:7b",
                 base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate(self, prompt, context="", tools=None) -> Result:
        content = f"{context}\n\n{prompt}" if context else prompt
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "stream": False,
                    "messages": [{"role": "user", "content": content}],
                },
            )
            r.raise_for_status()
        data = r.json()
        return Result(
            text=data["message"]["content"],
            provider=self.name,
            model=self.model,
            tokens_in=data.get("prompt_eval_count", 0),
            tokens_out=data.get("eval_count", 0),
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except httpx.HTTPError:
            return False
