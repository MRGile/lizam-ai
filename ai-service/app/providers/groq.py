import os

from dotenv import load_dotenv
from groq import AsyncGroq

from .base import BaseProvider


load_dotenv()


class GroqProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Groq")

        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY belum diset.")

        self.client = AsyncGroq(api_key=self.api_key)

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content