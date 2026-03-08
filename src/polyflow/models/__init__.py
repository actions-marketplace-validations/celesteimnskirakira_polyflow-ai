from __future__ import annotations
from typing import TYPE_CHECKING

from .base import ModelAdapter
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .openai_model import OpenAIAdapter
from .openrouter import OpenRouterAdapter

if TYPE_CHECKING:
    from polyflow.config import Config

# Native adapter registry (used when no OpenRouter key is configured)
_NATIVE_REGISTRY: dict[str, ModelAdapter] = {
    "claude": ClaudeAdapter(),
    "gemini": GeminiAdapter(),
    "gpt-4": OpenAIAdapter("gpt-4"),
    "codex": OpenAIAdapter("codex"),
}


def get_model_adapter(model_key: str, config: "Config | None" = None) -> ModelAdapter:
    """
    Return the appropriate adapter for a model key.

    When config has an OpenRouter key, ALL models are routed through
    OpenRouter regardless of model_key — one key, all models.
    """
    if config is not None and config.uses_openrouter:
        return OpenRouterAdapter(model_key)

    if model_key not in _NATIVE_REGISTRY:
        raise ValueError(
            f"Unknown model '{model_key}'. "
            f"Available: {list(_NATIVE_REGISTRY.keys())}. "
            f"Or set OPENROUTER_API_KEY to use any model via OpenRouter."
        )
    return _NATIVE_REGISTRY[model_key]
