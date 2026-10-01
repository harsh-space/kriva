"""Step 1: the provider interface.

Every model (local or cloud) implements this, so the rest of the system
never special-cases a vendor.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Result:
    text: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


class ModelProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def generate(self, prompt: str, context: str = "",
                       tools: list | None = None) -> Result:
        """Send a prompt (plus optional context) and return a Result.

        `tools` is unused in Phase 1; it reserves the slot for Phase 4.
        """

    @abstractmethod
    async def health(self) -> bool:
        """Return True if this provider is reachable/configured."""
