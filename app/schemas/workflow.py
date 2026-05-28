from pydantic import BaseModel, Field


class WorkflowRunRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    session_id: str | None = Field(default=None, max_length=64)


class WorkflowRunResponse(BaseModel):
    session_id: str | None
    intent: str
    route: str
    response: str
    trace: list[str]
    elapsed_ms: int
