from .base import BaseAgent


class BackendAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Backend Agent",
            role="Menganalisis dan mengembangkan bagian backend."
        )

    async def execute(self, task: str) -> dict:
        return {
            "agent": self.name,
            "task": task,
            "status": "completed",
            "message": "Backend Agent menerima task."
        }