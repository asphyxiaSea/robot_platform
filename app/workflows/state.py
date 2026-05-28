from typing import TypedDict


class WorkflowState(TypedDict, total=False):
    text: str
    session_id: str | None
    normalized_text: str
    intent: str
    route: str
    response: str
    trace: list[str]
    error: str
