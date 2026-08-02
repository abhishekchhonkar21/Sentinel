from datetime import datetime

from pydantic import BaseModel


class InjectFaultRequest(BaseModel):
    fault_id: str
    service: str | None = None
    params: dict = {}


class InjectFaultResponse(BaseModel):
    fault_id: str
    injected_at: datetime
    status: str
