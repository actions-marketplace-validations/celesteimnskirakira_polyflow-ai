from __future__ import annotations
import yaml
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".polyflow"


@dataclass
class Config:
    api_keys: dict[str, str] = field(default_factory=dict)
    config_dir: Path = DEFAULT_CONFIG_DIR

    def get_api_key(self, model: str) -> str:
        if model not in self.api_keys:
            raise KeyError(
                f"No API key configured for '{model}'. "
                f"Run `polyflow init` to configure."
            )
        return self.api_keys[model]


def save_config(cfg: Config) -> None:
    cfg.config_dir.mkdir(parents=True, exist_ok=True)
    config_file = cfg.config_dir / "config.yaml"
    data = {"api_keys": cfg.api_keys}
    config_file.write_text(yaml.dump(data))


def load_config(config_dir: Path = DEFAULT_CONFIG_DIR) -> Config:
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        return Config(config_dir=config_dir)
    data = yaml.safe_load(config_file.read_text()) or {}
    return Config(
        api_keys=data.get("api_keys", {}),
        config_dir=config_dir,
    )
