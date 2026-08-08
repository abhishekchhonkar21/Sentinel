from datetime import datetime

from pydantic import BaseModel, Field

from sentinel_core.schemas.contracts import FaultCatalogueEntry


class InjectFaultRequest(BaseModel):
    fault_id: str
    service: str | None = None
    params: dict = Field(default_factory=dict)


class InjectFaultResponse(BaseModel):
    fault_id: str
    injected_at: datetime
    status: str
    injected_service: str
    catalogue_entry: FaultCatalogueEntry | None = None


class ClearFaultRequest(BaseModel):
    service: str


class ClearFaultResponse(BaseModel):
    service: str
    cleared_at: datetime
    status: str


class ServiceFaultStatus(BaseModel):
    service: str
    state: dict
    active: bool


class LastFaultAction(BaseModel):
    action: str
    fault_id: str | None = None
    service: str
    at: datetime


class SystemStatusResponse(BaseModel):
    services: list[ServiceFaultStatus]
    catalogue_count: int
    last_action: LastFaultAction | None = None
