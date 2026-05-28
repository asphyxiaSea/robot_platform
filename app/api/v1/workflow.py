from time import perf_counter

from fastapi import APIRouter, HTTPException

from app.schemas.workflow import WorkflowRunRequest, WorkflowRunResponse
from app.workflows.graph import graph

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.post("/run", response_model=WorkflowRunResponse)
def run_workflow(payload: WorkflowRunRequest) -> WorkflowRunResponse:
    started = perf_counter()

    try:
        result = graph.invoke(
            {
                "text": payload.text,
                "session_id": payload.session_id,
                "trace": [],
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"workflow execution failed: {exc}") from exc

    elapsed_ms = int((perf_counter() - started) * 1000)

    return WorkflowRunResponse(
        session_id=payload.session_id,
        intent=result.get("intent", "unknown"),
        route=result.get("route", "fallback"),
        response=result.get("response", ""),
        trace=result.get("trace", []),
        elapsed_ms=elapsed_ms,
    )
