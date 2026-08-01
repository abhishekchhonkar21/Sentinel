from functools import lru_cache

from critic.application.critic_agent import CriticAgent
from critic.domain.claim_verifier import ClaimVerifier
from sentinel_core.infrastructure.dependencies import get_llm_provider, get_trace_writer


@lru_cache
def get_critic_agent() -> CriticAgent:
    return CriticAgent(
        verifier=ClaimVerifier(llm=get_llm_provider()),
        trace_writer=get_trace_writer(),
    )
