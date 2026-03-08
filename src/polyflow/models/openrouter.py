"""
OpenRouter adapter — routes all models through https://openrouter.ai
using the OpenAI-compatible API, so one key covers Claude, Gemini, GPT-4.
"""
from openai import AsyncOpenAI
from .base import ModelAdapter

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Maps Polyflow model aliases to OpenRouter model IDs
_MODEL_MAP: dict[str, str] = {
    "claude": "anthropic/claude-sonnet-4-5",
    "gemini": "google/gemini-2.0-flash-001",
    "gpt-4": "openai/gpt-4o",
    "codex": "openai/gpt-4o",
}


class OpenRouterAdapter(ModelAdapter):
    def __init__(self, model_key: str):
        super().__init__(model_key)
        self._openrouter_model = _MODEL_MAP.get(model_key, model_key)

    async def _call_api(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=float(timeout),
        )
        response = await client.chat.completions.create(
            model=self._openrouter_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
