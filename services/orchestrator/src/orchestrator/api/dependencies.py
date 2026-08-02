from functools import lru_cache

from orchestrator.application.pipeline_service import PipelineService
from orchestrator.infrastructure.agent_clients import HttpAgentClientRegistry


@lru_cache
def get_pipeline_service() -> PipelineService:
    return PipelineService(clients=HttpAgentClientRegistry())
