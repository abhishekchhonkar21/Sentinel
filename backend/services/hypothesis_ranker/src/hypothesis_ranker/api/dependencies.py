from functools import lru_cache

from hypothesis_ranker.application.ranker_agent import HypothesisRankerAgent
from hypothesis_ranker.domain.scorers.rule_based_scorer import RuleBasedHypothesisScorer
from sentinel_core.infrastructure.dependencies import get_trace_writer


@lru_cache
def get_ranker_agent() -> HypothesisRankerAgent:
    return HypothesisRankerAgent(
        scorer=RuleBasedHypothesisScorer(),
        trace_writer=get_trace_writer(),
    )
