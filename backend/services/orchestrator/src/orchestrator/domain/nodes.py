"""LangGraph node functions — thin adapters over HTTP agent clients."""

from orchestrator.domain.state import PipelineState
from orchestrator.infrastructure.agent_clients import AgentClientRegistry


async def detector_node(state: PipelineState, clients: AgentClientRegistry) -> PipelineState:
    # Detector may run upstream; orchestrator typically receives pre-detected AnomalyEvent
    return state


async def investigator_node(state: PipelineState, clients: AgentClientRegistry) -> PipelineState:
    state.evidence_bundle = await clients.investigator.investigate(state.anomaly_event)
    return state


async def ranker_node(state: PipelineState, clients: AgentClientRegistry) -> PipelineState:
    assert state.evidence_bundle is not None
    state.ranked_hypotheses = await clients.ranker.rank(state.evidence_bundle)
    return state


async def narrator_node(state: PipelineState, clients: AgentClientRegistry) -> PipelineState:
    assert state.ranked_hypotheses is not None and state.evidence_bundle is not None
    state.incident_report = await clients.narrator.narrate(
        state.ranked_hypotheses, state.evidence_bundle
    )
    return state


async def critic_node(state: PipelineState, clients: AgentClientRegistry) -> PipelineState:
    assert state.incident_report is not None and state.evidence_bundle is not None
    state.critic_verdict = await clients.critic.verify(
        state.incident_report, state.evidence_bundle
    )
    return state
