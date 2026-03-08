from __future__ import annotations
import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".polyflow"


@dataclass
class Config:
    api_keys: dict[str, str] = field(default_factory=dict)
    openrouter_api_key: str = ""
    config_dir: Path = DEFAULT_CONFIG_DIR

    def get_api_key(self, model: str) -> str:
        """Return the API key for a model. OpenRouter key takes priority."""
        if self.openrouter_api_key:
            return self.openrouter_api_key
        if model not in self.api_keys:
            raise KeyError(
                f"No API key configured for '{model}'. "
                f"Run `polyflow init` or set OPENROUTER_API_KEY env var."
            )
        return self.api_keys[model]

    @property
    def uses_openrouter(self) -> bool:
        return bool(self.openrouter_api_key)


def save_config(cfg: Config) -> None:
    cfg.config_dir.mkdir(parents=True, exist_ok=True)
    config_file = cfg.config_dir / "config.yaml"
    data: dict = {"api_keys": cfg.api_keys}
    if cfg.openrouter_api_key:
        data["openrouter_api_key"] = cfg.openrouter_api_key
    config_file.write_text(yaml.dump(data))


def load_config(config_dir: Path = DEFAULT_CONFIG_DIR) -> Config:
    """Load config from file, with env var overrides applied on top."""
    config_file = config_dir / "config.yaml"
    data: dict = {}
    if config_file.exists():
        data = yaml.safe_load(config_file.read_text()) or {}

    # Env vars take priority over file config
    openrouter_key = (
        os.environ.get("OPENROUTER_API_KEY")
        or data.get("openrouter_api_key", "")
    )

    # Also merge individual model env vars (ANTHROPIC_API_KEY, etc.)
    env_keys = {
        "claude": os.environ.get("ANTHROPIC_API_KEY", ""),
        "gemini": os.environ.get("GEMINI_API_KEY", ""),
        "gpt-4": os.environ.get("OPENAI_API_KEY", ""),
    }
    merged_keys = {**data.get("api_keys", {})}
    for model, key in env_keys.items():
        if key:
            merged_keys[model] = key

    return Config(
        api_keys=merged_keys,
        openrouter_api_key=openrouter_key,
        config_dir=config_dir,
    )
