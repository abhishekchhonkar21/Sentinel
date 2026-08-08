from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api_gateway"}


# TODO: GET /incidents, GET /incidents/{anomaly_id} — query incident_reports via repository
