from .base import ModelAdapter
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .openai_model import OpenAIAdapter

_REGISTRY: dict[str, ModelAdapter] = {
    "claude": ClaudeAdapter(),
    "gemini": GeminiAdapter(),
    "gpt-4": OpenAIAdapter("gpt-4"),
    "codex": OpenAIAdapter("codex"),
}


def get_model_adapter(model_key: str) -> ModelAdapter:
    if model_key not in _REGISTRY:
        raise ValueError(f"Unknown model '{model_key}'. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[model_key]
