from typing import Any

from fastapi import APIRouter, Request, Response, status

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request, response: Response) -> dict[str, Any]:
    """Readiness: dependencies reachable. Checks are registered on app.state.ready_checks."""
    results: dict[str, bool] = {}
    for name, check in getattr(request.app.state, "ready_checks", {}).items():
        try:
            results[name] = bool(await check())
        except Exception:
            results[name] = False
    ok = all(results.values())
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if ok else "degraded", "checks": results}
