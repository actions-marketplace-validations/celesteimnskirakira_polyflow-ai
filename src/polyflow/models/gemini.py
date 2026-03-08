import google.genai as genai
from .base import ModelAdapter


class GeminiAdapter(ModelAdapter):
    def __init__(self):
        super().__init__("gemini")

    async def _call_api(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        client = genai.Client(api_key=api_key)
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
