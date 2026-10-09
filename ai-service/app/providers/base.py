from abc import ABC, abstractmethod


class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Mengirim prompt ke AI provider dan mengembalikan respons.
        """
        pass