from .base import ModelProvider, Result
from .ollama import OllamaProvider
from .anthropic import AnthropicProvider

PROVIDERS = {
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
}

__all__ = ["ModelProvider", "Result", "OllamaProvider", "AnthropicProvider", "PROVIDERS"]
