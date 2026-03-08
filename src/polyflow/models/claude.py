import anthropic
from .base import ModelAdapter


class ClaudeAdapter(ModelAdapter):
    def __init__(self):
        super().__init__("claude")

    async def _call_api(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        message = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
