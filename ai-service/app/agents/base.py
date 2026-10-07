from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    async def execute(self, task: str) -> dict:
        """
        Menjalankan task yang diberikan kepada agent.
        """
        pass