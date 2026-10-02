from .base import ModelProvider, Result
from .ollama import OllamaProvider
from .anthropic import AnthropicProvider
from .groq import GroqProvider
from .nvidia import NvidiaProvider

PROVIDERS = {
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
    "groq": GroqProvider,
    "nvidia": NvidiaProvider,
}

__all__ = ["ModelProvider", "Result", "OllamaProvider", "AnthropicProvider",
           "GroqProvider", "NvidiaProvider", "PROVIDERS"]
