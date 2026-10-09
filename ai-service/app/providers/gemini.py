import asyncio
import os

from dotenv import load_dotenv
from google import genai

from .base import BaseProvider


load_dotenv()


class GeminiProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Gemini")

        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY belum diset.")

        self.client = genai.Client(api_key=self.api_key)

    async def generate(self, prompt: str) -> str:
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                )

                return response.text

            except Exception as exc:
                error_message = str(exc)

                if "503" not in error_message:
                    raise

                if attempt == max_retries - 1:
                    raise

                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

        raise RuntimeError("Gemini gagal memberikan response.")