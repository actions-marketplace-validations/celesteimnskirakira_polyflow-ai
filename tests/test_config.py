import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch
from polyflow.config import Config, load_config, save_config


def test_config_get_api_key(tmp_path):
    cfg = Config(api_keys={"claude": "sk-ant-test123"}, config_dir=tmp_path)
    assert cfg.get_api_key("claude") == "sk-ant-test123"


def test_config_missing_key_raises(tmp_path):
    cfg = Config(api_keys={}, config_dir=tmp_path)
    with pytest.raises(KeyError, match="No API key configured for 'gemini'"):
        cfg.get_api_key("gemini")


def test_openrouter_key_takes_priority(tmp_path):
    cfg = Config(api_keys={"claude": "sk-ant-abc"}, openrouter_api_key="sk-or-test")
    # OpenRouter key is returned for any model
    assert cfg.get_api_key("claude") == "sk-or-test"
    assert cfg.get_api_key("gemini") == "sk-or-test"


def test_uses_openrouter_flag(tmp_path):
    cfg_with = Config(openrouter_api_key="sk-or-test")
    cfg_without = Config(api_keys={"claude": "sk-ant-abc"})
    assert cfg_with.uses_openrouter is True
    assert cfg_without.uses_openrouter is False


def test_save_and_load_config_file_only(tmp_path):
    """Test file-based config load without env var interference."""
    cfg = Config(api_keys={"claude": "sk-ant-abc"}, config_dir=tmp_path)
    save_config(cfg)
    # Isolate from real env vars so the test is deterministic
    with patch.dict(os.environ, {}, clear=False):
        env_backup = os.environ.pop("OPENROUTER_API_KEY", None)
        try:
            loaded = load_config(tmp_path)
            assert loaded.get_api_key("claude") == "sk-ant-abc"
        finally:
            if env_backup is not None:
                os.environ["OPENROUTER_API_KEY"] = env_backup


def test_load_config_reads_openrouter_env(tmp_path):
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-from-env"}):
        cfg = load_config(tmp_path)
    assert cfg.openrouter_api_key == "sk-or-from-env"
    assert cfg.uses_openrouter is True
