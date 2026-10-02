from .base import ModelProvider, Result
from .ollama import OllamaProvider
from .anthropic import AnthropicProvider
from .groq import GroqProvider

PROVIDERS = {
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
    "groq": GroqProvider,
}

__all__ = ["ModelProvider", "Result", "OllamaProvider", "AnthropicProvider",
           "GroqProvider", "PROVIDERS"]