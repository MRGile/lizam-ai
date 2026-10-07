from .base import BaseAgent


class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="QA Agent",
            role="Menguji perubahan dan mencari bug."
        )

    async def execute(self, task: str) -> dict:
        return {
            "agent": self.name,
            "task": task,
            "status": "completed",
            "message": "QA Agent menerima task."
        }