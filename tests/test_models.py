import pytest
from unittest.mock import AsyncMock, patch
from polyflow.models import get_model_adapter
from polyflow.models.base import ModelAdapter


def test_get_claude_adapter():
    adapter = get_model_adapter("claude")
    assert isinstance(adapter, ModelAdapter)
    assert adapter.model_key == "claude"


def test_get_gemini_adapter():
    adapter = get_model_adapter("gemini")
    assert adapter.model_key == "gemini"


def test_get_openai_adapter():
    adapter = get_model_adapter("gpt-4")
    assert adapter.model_key == "gpt-4"


def test_unknown_model_raises():
    with pytest.raises(ValueError, match="Unknown model"):
        get_model_adapter("unknown-model-xyz")


@pytest.mark.asyncio
async def test_claude_adapter_calls_api():
    adapter = get_model_adapter("claude")
    mock_response = "Here is the plan."
    with patch.object(adapter, "_call_api", new=AsyncMock(return_value=mock_response)):
        result = await adapter.complete("Write a plan", api_key="test-key")
    assert result == "Here is the plan."
