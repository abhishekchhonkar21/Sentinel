"""LangGraph StateGraph — each node delegates to an agent HTTP client."""

from langgraph.graph import END, StateGraph

from orchestrator.domain.nodes import (
    critic_node,
    detector_node,
    investigator_node,
    narrator_node,
    ranker_node,
)
from orchestrator.domain.state import PipelineState
from orchestrator.infrastructure.agent_clients import AgentClientRegistry


def build_investigation_graph(clients: AgentClientRegistry):
    graph = StateGraph(PipelineState)

    graph.add_node("investigator", lambda s: investigator_node(s, clients))
    graph.add_node("ranker", lambda s: ranker_node(s, clients))
    graph.add_node("narrator", lambda s: narrator_node(s, clients))
    graph.add_node("critic", lambda s: critic_node(s, clients))

    graph.set_entry_point("investigator")
    graph.add_edge("investigator", "ranker")
    graph.add_edge("ranker", "narrator")
    graph.add_edge("narrator", "critic")
    graph.add_edge("critic", END)

    return graph.compile()
