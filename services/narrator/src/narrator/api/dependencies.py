from functools import lru_cache

from narrator.application.narrator_agent import NarratorAgent
from narrator.domain.report_generator import ReportGenerator
from sentinel_core.infrastructure.dependencies import get_llm_provider, get_trace_writer


@lru_cache
def get_narrator_agent() -> NarratorAgent:
    return NarratorAgent(
        generator=ReportGenerator(llm=get_llm_provider()),
        trace_writer=get_trace_writer(),
    )
