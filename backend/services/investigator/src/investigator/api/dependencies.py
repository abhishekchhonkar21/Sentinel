from functools import lru_cache

from investigator.application.investigator_agent import InvestigatorAgent
from sentinel_core.infrastructure.dependencies import (
    get_evidence_repository,
    get_graph_store,
    get_trace_writer,
)


@lru_cache
def get_investigator_agent() -> InvestigatorAgent:
    return InvestigatorAgent(
        graph_store=get_graph_store(),
        evidence_repo=get_evidence_repository(),
        trace_writer=get_trace_writer(),
    )
