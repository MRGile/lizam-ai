from fastapi import FastAPI

from app.orchestrator.orchestrator import Orchestrator
from app.schemas.task import TaskRequest, TaskResponse


app = FastAPI(
    title="LIZAM AI Service",
    version="0.1.0"
)

orchestrator = Orchestrator()


@app.get("/")
def root():
    return {
        "name": "LIZAM AI",
        "service": "AI Service",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    return await orchestrator.run(request.task)