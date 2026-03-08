import pytest
import yaml
from pathlib import Path
from polyflow.config import Config, load_config, save_config


def test_config_get_api_key(tmp_path):
    cfg = Config(api_keys={"claude": "sk-ant-test123"}, config_dir=tmp_path)
    assert cfg.get_api_key("claude") == "sk-ant-test123"


def test_config_missing_key_raises(tmp_path):
    cfg = Config(api_keys={}, config_dir=tmp_path)
    with pytest.raises(KeyError, match="No API key configured for 'gemini'"):
        cfg.get_api_key("gemini")


def test_save_and_load_config(tmp_path):
    cfg = Config(api_keys={"claude": "sk-ant-abc"}, config_dir=tmp_path)
    save_config(cfg)
    loaded = load_config(tmp_path)
    assert loaded.get_api_key("claude") == "sk-ant-abc"
