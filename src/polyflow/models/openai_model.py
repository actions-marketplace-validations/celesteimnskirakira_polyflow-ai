from openai import AsyncOpenAI
from .base import ModelAdapter


class OpenAIAdapter(ModelAdapter):
    MODEL_MAP = {
        "gpt-4": "gpt-4o",
        "codex": "gpt-4o",
    }

    def __init__(self, model_key: str):
        super().__init__(model_key)
        self._openai_model = self.MODEL_MAP.get(model_key, model_key)

    async def _call_api(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=self._openai_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
