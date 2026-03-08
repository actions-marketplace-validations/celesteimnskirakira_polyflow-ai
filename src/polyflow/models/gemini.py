import google.generativeai as genai
from .base import ModelAdapter


class GeminiAdapter(ModelAdapter):
    def __init__(self):
        super().__init__("gemini")

    async def _call_api(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
