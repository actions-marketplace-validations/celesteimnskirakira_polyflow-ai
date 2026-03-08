from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    def __init__(self, model_key: str):
        self.model_key = model_key

    async def complete(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        return await self._call_api(prompt, api_key, timeout)

    @abstractmethod
    async def _call_api(self, prompt: str, api_key: str, timeout: int) -> str:
        pass
