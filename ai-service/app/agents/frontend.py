from .base import BaseAgent


class FrontendAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Frontend Agent",
            role="Menganalisis dan mengembangkan bagian frontend."
        )

    async def execute(self, task: str) -> dict:
        return {
            "agent": self.name,
            "task": task,
            "status": "completed",
            "message": "Frontend Agent menerima task."
        }