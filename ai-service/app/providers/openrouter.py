import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .base import BaseProvider


load_dotenv()


class OpenRouterProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="OpenRouter")

        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY belum diset.")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content