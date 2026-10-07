from app.agents.frontend import FrontendAgent
from app.agents.backend import BackendAgent
from app.agents.qa import QAAgent


class Orchestrator:
    def __init__(self):
        self.frontend = FrontendAgent()
        self.backend = BackendAgent()
        self.qa = QAAgent()

    async def run(self, task: str) -> dict:
        """
        Menjalankan task melalui agent yang sesuai.
        """

        task_lower = task.lower()

        if any(keyword in task_lower for keyword in [
            "frontend",
            "ui",
            "css",
            "html",
            "blade",
            "tampilan",
        ]):
            result = await self.frontend.execute(task)

        elif any(keyword in task_lower for keyword in [
            "backend",
            "api",
            "database",
            "controller",
            "model",
            "route",
            "laravel",
        ]):
            result = await self.backend.execute(task)

        elif any(keyword in task_lower for keyword in [
            "test",
            "testing",
            "qa",
            "bug",
            "error",
            "cek",
        ]):
            result = await self.qa.execute(task)

        else:
            result = {
                "agent": "Orchestrator",
                "task": task,
                "status": "unassigned",
                "message": "Task belum dapat menentukan agent."
            }

        return result