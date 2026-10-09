import asyncio

from app.agents.backend import BackendAgent
from app.agents.frontend import FrontendAgent
from app.agents.qa import QAAgent


class Orchestrator:
    def __init__(self, workspace_path: str | None = None):
        self.workspace_path = workspace_path

        self.frontend = FrontendAgent(workspace_path)
        self.backend = BackendAgent(workspace_path)
        self.qa = QAAgent(workspace_path)

    def _detect_agents(self, task: str) -> list[str]:
        task_lower = task.lower()

        agents = []

        frontend_keywords = (
            "frontend",
            "front-end",
            "ui",
            "ux",
            "css",
            "html",
            "javascript",
            "js",
            "blade",
            "tampilan",
            "halaman",
            "responsive",
            "responsif",
        )

        backend_keywords = (
            "backend",
            "back-end",
            "api",
            "database",
            "db",
            "controller",
            "model",
            "migration",
            "route",
            "routing",
            "laravel",
            "php",
            "auth",
            "login",
        )

        qa_keywords = (
            "test",
            "testing",
            "qa",
            "bug",
            "error",
            "debug",
            "review",
            "cek",
            "periksa",
        )

        if any(keyword in task_lower for keyword in frontend_keywords):
            agents.append("frontend")

        if any(keyword in task_lower for keyword in backend_keywords):
            agents.append("backend")

        if any(keyword in task_lower for keyword in qa_keywords):
            agents.append("qa")

        if not agents:
            agents = ["frontend", "backend"]

        return agents

    async def run(self, task: str) -> dict:
        agents = self._detect_agents(task)

        results = {}

        coding_agents = [
            agent
            for agent in agents
            if agent in {"frontend", "backend"}
        ]

        if len(coding_agents) > 1:
            parallel_results = await asyncio.gather(
                *[
                    self._run_agent(agent, task)
                    for agent in coding_agents
                ]
            )

            for agent, result in zip(coding_agents, parallel_results):
                results[agent] = result

        else:
            for agent in coding_agents:
                results[agent] = await self._run_agent(agent, task)

        if "qa" in agents:
            results["qa"] = await self.qa.execute(task)

        return {
            "task": task,
            "agents": agents,
            "status": "completed",
            "results": results,
        }

    async def _run_agent(self, agent: str, task: str) -> dict:
        if agent == "frontend":
            return await self.frontend.execute(task)

        if agent == "backend":
            return await self.backend.execute(task)

        if agent == "qa":
            return await self.qa.execute(task)

        return {
            "agent": agent,
            "status": "failed",
            "message": "Agent tidak dikenal.",
        }