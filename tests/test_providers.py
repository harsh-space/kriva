import asyncio
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from router.providers.anthropic import AnthropicProvider
from router.providers.groq import GroqProvider
from router.providers.nvidia import NvidiaProvider
from router.providers.ollama import OllamaProvider


class ProviderTests(unittest.TestCase):
    def _mock_client(self, response):
        client = MagicMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = False
        client.post = AsyncMock(return_value=response)
        return client

    def test_nvidia_sends_model_context_auth_and_returns_usage(self):
        response = MagicMock()
        response.json.return_value = {
            "choices": [{"message": {"content": "answer"}}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 7},
        }
        client = self._mock_client(response)

        with patch.dict(os.environ, {"NVIDIA_API_KEY": "test-key"}), patch(
            "router.providers.nvidia.httpx.AsyncClient", return_value=client
        ):
            result = asyncio.run(NvidiaProvider().generate("task", "context"))

        self.assertEqual(result.text, "answer")
        self.assertEqual(result.provider, "nvidia")
        self.assertEqual(result.model, "nvidia/nemotron-3-ultra-550b-a55b")
        self.assertEqual(result.tokens_in, 12)
        self.assertEqual(result.tokens_out, 7)
        args, kwargs = client.post.call_args
        self.assertEqual(
            args[0],
            "https://integrate.api.nvidia.com/v1/chat/completions",
        )
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(
            kwargs["json"]["messages"][0]["content"],
            "context\n\ntask",
        )

    def test_nvidia_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "NVIDIA_API_KEY is not set"):
                asyncio.run(NvidiaProvider().generate("task"))

    def test_groq_uses_bearer_api_key(self):
        response = MagicMock()
        response.json.return_value = {
            "choices": [{"message": {"content": "answer"}}],
            "usage": {},
        }
        client = self._mock_client(response)

        with patch.dict(os.environ, {"GROQ_API_KEY": "groq-test-key"}), patch(
            "router.providers.groq.httpx.AsyncClient", return_value=client
        ):
            result = asyncio.run(GroqProvider().generate("task"))

        self.assertEqual(result.text, "answer")
        self.assertEqual(
            client.post.call_args.kwargs["headers"]["Authorization"],
            "Bearer groq-test-key",
        )

    def test_anthropic_sends_api_key_and_parses_usage(self):
        response = MagicMock()
        response.json.return_value = {
            "content": [{"text": "answer"}],
            "usage": {"input_tokens": 8, "output_tokens": 3},
        }
        client = self._mock_client(response)

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-test-key"}), patch(
            "router.providers.anthropic.httpx.AsyncClient", return_value=client
        ):
            result = asyncio.run(AnthropicProvider().generate("task", "context"))

        self.assertEqual(result.text, "answer")
        self.assertEqual(result.tokens_in, 8)
        self.assertEqual(result.tokens_out, 3)
        args, kwargs = client.post.call_args
        self.assertEqual(args[0], "https://api.anthropic.com/v1/messages")
        self.assertEqual(kwargs["headers"]["x-api-key"], "anthropic-test-key")
        self.assertEqual(kwargs["json"]["messages"][0]["content"], "context\n\ntask")

    def test_ollama_sends_non_streaming_chat_request(self):
        response = MagicMock()
        response.json.return_value = {
            "message": {"content": "answer"},
            "prompt_eval_count": 9,
            "eval_count": 4,
        }
        client = self._mock_client(response)

        with patch(
            "router.providers.ollama.httpx.AsyncClient", return_value=client
        ):
            result = asyncio.run(OllamaProvider().generate("task", "context"))

        self.assertEqual(result.text, "answer")
        self.assertEqual(result.tokens_in, 9)
        self.assertEqual(result.tokens_out, 4)
        args, kwargs = client.post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/chat")
        self.assertEqual(kwargs["json"]["stream"], False)
        self.assertEqual(kwargs["json"]["messages"][0]["content"], "context\n\ntask")


if __name__ == "__main__":
    unittest.main()
