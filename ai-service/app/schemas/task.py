from pydantic import BaseModel


class TaskRequest(BaseModel):
    task: str


class TaskResponse(BaseModel):
    agent: str
    task: str
    status: str
    message: str